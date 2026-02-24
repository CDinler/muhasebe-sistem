"""
Monthly Personnel Records Service
Handles Excel upload processing and database synchronization
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict, Any
from datetime import date
from decimal import Decimal
import math

from app.models import MonthlyPersonnelRecord
from app.domains.personnel.models import Personnel, PersonnelContract
from app.models import Account
from app.models import CostCenter
from app.domains.personnel.monthly_records.schemas import MonthlyPersonnelRecordCreate


class PersonnelSicilService:
    """Service for processing personnel sicil (records) uploads"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @staticmethod
    def _clean_nan(value: Any) -> Any:
        """Convert NaN values to None for database compatibility"""
        if value is None:
            return None
        # Check for float NaN
        if isinstance(value, float) and math.isnan(value):
            return None
        return value
    
    def process_sicil_upload(
        self, 
        donem: str,
        records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process personnel sicil Excel upload
        
        Args:
            donem: Period in yyyy-mm format
            records: List of dicts containing personnel sicil data from Excel
            
        Returns:
            Dict with processing results
        """
        results = {
            "created_personnel": 0,
            "updated_personnel": 0,
            "created_contracts": 0,
            "updated_contracts": 0,
            "created_records": 0,
            "updated_records": 0,
            "errors": []
        }
        
        for idx, record_data in enumerate(records):
            try:
                self._process_single_record(donem, record_data, results)
            except Exception as e:
                results["errors"].append({
                    "row": idx + 1,
                    "tc_kimlik_no": record_data.get("tc_kimlik_no"),
                    "error": str(e)
                })
                continue
        
        self.db.commit()
        return results
    
    def _process_single_record(
        self, 
        donem: str, 
        record_data: Dict[str, Any],
        results: Dict[str, Any]
    ) -> None:
        """Process a single personnel sicil record"""
        
        tc_kimlik_no = record_data["tc_kimlik_no"]
        ise_giris_tarihi = record_data["ise_giris_tarihi"]
        bolum = record_data.get("bolum")
        
        # ISLEM4: Check if personnel exists, if not create
        personnel = self.db.query(Personnel).filter(
            Personnel.tc_kimlik_no == tc_kimlik_no
        ).first()
        
        if not personnel:
            personnel = self._create_personnel(record_data)
            results["created_personnel"] += 1
        else:
            # Eğer personel var ama account_id'si yoksa, account oluştur
            if not personnel.accounts_id:
                self._create_account_for_personnel(personnel, record_data)
                results["created_accounts"] = results.get("created_accounts", 0) + 1
            results["updated_personnel"] += 1
        
        personnel_id = personnel.id
        
        # ISLEM5: Check if monthly_personnel_record exists for this donem
        # Use personnel_id instead of tc_kimlik_no to match unique constraint
        mpr = self.db.query(MonthlyPersonnelRecord).filter(
            and_(
                MonthlyPersonnelRecord.personnel_id == personnel_id,
                MonthlyPersonnelRecord.donem == donem,
                MonthlyPersonnelRecord.bolum == bolum,
                MonthlyPersonnelRecord.ise_giris_tarihi == ise_giris_tarihi
            )
        ).first()
        
        if mpr:
            # ISLEM6: Update existing record
            self._update_monthly_record(mpr, record_data)
            results["updated_records"] += 1
        else:
            # Create new monthly record
            mpr = self._create_monthly_record(donem, personnel_id, record_data)
            results["created_records"] += 1
        
        mpr_id = mpr.id
        
        # ISLEM7: Update or create personnel_contract
        contract = self.db.query(PersonnelContract).filter(
            and_(
                PersonnelContract.tc_kimlik_no == tc_kimlik_no,
                PersonnelContract.ise_giris_tarihi == ise_giris_tarihi,
                PersonnelContract.bolum == bolum
            )
        ).first()
        
        if contract:
            # Update existing contract
            self._update_contract_from_sicil(contract, mpr, record_data)
            results["updated_contracts"] += 1
        else:
            # ISLEM8: Create new contract
            contract = self._create_contract_from_sicil(personnel_id, mpr_id, record_data)
            results["created_contracts"] += 1
        
        # Link contract to monthly record
        mpr.contract_id = contract.id
    
    def _create_account_for_personnel(self, personnel: Personnel, record_data: Dict[str, Any]) -> None:
        """Create account for existing personnel without account_id"""
        adi = record_data.get("adi") or personnel.ad
        soyadi = record_data.get("soyadi") or personnel.soyad
        
        acc_code = f"335.{personnel.tc_kimlik_no}"
        acc_name = f"{adi} {soyadi} {personnel.tc_kimlik_no}"
        
        # Check if account already exists (by code)
        existing_account = self.db.query(Account).filter(
            Account.code == acc_code
        ).first()
        
        if existing_account:
            personnel.accounts_id = existing_account.id
            if not existing_account.personnel_id:
                existing_account.personnel_id = personnel.id
        else:
            account = Account(
                code=acc_code,
                name=acc_name,
                account_type="BALANCE_SHEET",
                is_active=1
            )
            self.db.add(account)
            self.db.flush()
            
            personnel.accounts_id = account.id
            account.personnel_id = personnel.id
        
        self.db.flush()
    
    def _create_personnel(self, record_data: Dict[str, Any]) -> Personnel:
        """Create new personnel and associated account"""
        
        tc_kimlik_no = record_data["tc_kimlik_no"]
        adi = record_data.get("adi", "")
        soyadi = record_data.get("soyadi", "")
        
        # Create account first
        acc_code = f"335.{tc_kimlik_no}"
        acc_name = f"{adi} {soyadi} {tc_kimlik_no}"
        
        account = Account(
            code=acc_code,
            name=acc_name,
            account_type="BALANCE_SHEET",
            is_active=1
        )
        self.db.add(account)
        self.db.flush()  # Get account.id
        
        # Create personnel - clean NaN values before database insert
        iban = self._clean_nan(record_data.get("hesap_no"))  # IBAN from Excel hesap_no field
        personnel = Personnel(
            tc_kimlik_no=tc_kimlik_no,
            ad=adi,
            soyad=soyadi,
            accounts_id=account.id,
            iban=iban
        )
        self.db.add(personnel)
        self.db.flush()  # Get personnel.id
        
        # Update account's personnel_id
        account.personnel_id = personnel.id
        
        return personnel
    
    def _create_monthly_record(
        self, 
        donem: str,
        personnel_id: int, 
        record_data: Dict[str, Any]
    ) -> MonthlyPersonnelRecord:
        """Create new monthly personnel record"""
        
        # Calculate yil and ay from donem (yyyy-mm)
        yil, ay = map(int, donem.split('-'))
        
        # Clean NaN values
        cleaned_data = {k: self._clean_nan(v) for k, v in record_data.items()}
        
        mpr = MonthlyPersonnelRecord(
            personnel_id=personnel_id,
            donem=donem,
            yil=yil,
            ay=ay,
            tc_kimlik_no=cleaned_data["tc_kimlik_no"],
            adi=cleaned_data.get("adi"),
            soyadi=cleaned_data.get("soyadi"),
            cinsiyeti=cleaned_data.get("cinsiyeti"),
            unvan=cleaned_data.get("unvan"),
            isyeri=cleaned_data.get("isyeri"),
            bolum=cleaned_data.get("bolum"),
            ssk_no=cleaned_data.get("ssk_no"),
            baba_adi=cleaned_data.get("baba_adi"),
            anne_adi=cleaned_data.get("anne_adi"),
            dogum_yeri=cleaned_data.get("dogum_yeri"),
            dogum_tarihi=cleaned_data.get("dogum_tarihi"),
            nufus_cuzdani_no=cleaned_data.get("nufus_cuzdani_no"),
            nufusa_kayitli_oldugu_il=cleaned_data.get("nufusa_kayitli_oldugu_il"),
            nufusa_kayitli_oldugu_ilce=cleaned_data.get("nufusa_kayitli_oldugu_ilce"),
            nufusa_kayitli_oldugu_mah=cleaned_data.get("nufusa_kayitli_oldugu_mah"),
            cilt_no=cleaned_data.get("cilt_no"),
            sira_no=cleaned_data.get("sira_no"),
            kutuk_no=cleaned_data.get("kutuk_no"),
            ise_giris_tarihi=cleaned_data["ise_giris_tarihi"],
            isten_cikis_tarihi=cleaned_data.get("isten_cikis_tarihi"),
            isten_ayrilis_kodu=cleaned_data.get("isten_ayrilis_kodu"),
            isten_ayrilis_nedeni=cleaned_data.get("isten_ayrilis_nedeni"),
            adres=cleaned_data.get("adres"),
            telefon=cleaned_data.get("telefon"),
            banka_sube_adi=cleaned_data.get("banka_sube_adi"),
            hesap_no=cleaned_data.get("hesap_no"),
            ucret=cleaned_data.get("ucret"),
            net_brut=cleaned_data.get("net_brut"),
            kan_grubu=cleaned_data.get("kan_grubu"),
            meslek_kodu=cleaned_data.get("meslek_kodu"),
            meslek_adi=cleaned_data.get("meslek_adi")
        )
        
        self.db.add(mpr)
        self.db.flush()
        return mpr
    
    def _update_monthly_record(
        self, 
        mpr: MonthlyPersonnelRecord, 
        record_data: Dict[str, Any]
    ) -> None:
        """Update existing monthly personnel record"""
        
        # Clean NaN values before updating
        cleaned_data = {k: self._clean_nan(v) for k, v in record_data.items()}
        
        for key, value in cleaned_data.items():
            if hasattr(mpr, key) and key != "id" and key != "personnel_id":
                setattr(mpr, key, value)
    
    def _create_contract_from_sicil(
        self,
        personnel_id: int,
        mpr_id: int,
        record_data: Dict[str, Any]
    ) -> PersonnelContract:
        """Create new personnel contract from sicil data"""
        
        # Get cost_center_id from bolum
        cost_center_id = None
        if record_data.get("bolum"):
            cost_center = self.db.query(CostCenter).filter(
                CostCenter.bolum_adi == record_data["bolum"]
            ).first()
            if cost_center:
                cost_center_id = cost_center.id
        
        # Determine is_active
        is_active = 1 if not record_data.get("isten_cikis_tarihi") else 0
        
        contract = PersonnelContract(
            personnel_id=personnel_id,
            tc_kimlik_no=record_data["tc_kimlik_no"],
            bolum=record_data.get("bolum"),
            monthly_personnel_records_id=mpr_id,
            cost_center_id=cost_center_id,
            ise_giris_tarihi=record_data["ise_giris_tarihi"],
            isten_cikis_tarihi=record_data.get("isten_cikis_tarihi"),
            net_brut=record_data.get("net_brut"),
            ucret=record_data.get("ucret"),
            is_active=is_active,
            iban=None  # Will be populated from personnel table
        )
        
        self.db.add(contract)
        self.db.flush()
        return contract
    
    def _update_contract_from_sicil(
        self,
        contract: PersonnelContract,
        mpr: MonthlyPersonnelRecord,
        record_data: Dict[str, Any]
    ) -> None:
        """Update existing contract from sicil data"""
        
        # Update fields that should be synced from monthly_personnel_records
        contract.monthly_personnel_records_id = mpr.id
        contract.isten_cikis_tarihi = record_data.get("isten_cikis_tarihi")
        contract.net_brut = record_data.get("net_brut")
        contract.ucret = record_data.get("ucret")
        contract.is_active = 1 if not record_data.get("isten_cikis_tarihi") else 0
