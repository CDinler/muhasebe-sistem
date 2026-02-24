"""Monthly Personnel Records domain service"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from fastapi import UploadFile
import pandas as pd
from io import BytesIO

from app.domains.personnel.monthly_records.repository import MonthlyPersonnelRecordRepository
from app.services.personnel_sicil_service import PersonnelSicilService
from app.models import MonthlyPersonnelRecord
from app.domains.personnel.monthly_records.schemas import (
    MonthlyPersonnelRecordCreate,
    MonthlyPersonnelRecordUpdate
)


class MonthlyPersonnelRecordService:
    """Service layer for Monthly Personnel Records"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = MonthlyPersonnelRecordRepository()
    
    def list_records(
        self,
        donem: Optional[str] = None,
        personnel_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List monthly personnel records with filters"""
        items = self.repository.get_filtered(
            self.db,
            donem=donem,
            personnel_id=personnel_id,
            skip=skip,
            limit=limit
        )
        total = self.repository.count_filtered(
            self.db,
            donem=donem,
            personnel_id=personnel_id
        )
        
        return {
            "items": items,
            "total": total
        }
    
    def get_periods(self) -> List[str]:
        """Get all available periods"""
        return self.repository.get_periods(self.db)
    
    def get_record(self, record_id: int) -> Optional[MonthlyPersonnelRecord]:
        """Get a specific record by ID"""
        return self.repository.get(self.db, id=record_id)
    
    async def upload_sicil(
        self,
        donem: str,
        file: UploadFile
    ) -> Dict[str, Any]:
        """
        Upload personnel sicil Excel file
        
        Process:
        1. Read Excel file
        2. For each row:
           - Create personnel if doesn't exist
           - Create/update monthly_personnel_record
           - Create/update personnel_contract
        """
        
        # Validate file extension
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise ValueError("File must be Excel format (.xlsx or .xls)")
        
        # Read Excel file
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))
        
        # Convert DataFrame to list of dicts
        records = []
        for _, row in df.iterrows():
            record = {
                "adi": row.get("Adı"),
                "soyadi": row.get("Soyadı"),
                "cinsiyeti": row.get("Cinsiyeti"),
                "unvan": row.get("Ünvan"),
                "isyeri": row.get("İşyeri"),
                "bolum": row.get("Bölüm"),
                "ssk_no": row.get("SSK No"),
                "tc_kimlik_no": str(row.get("TC Kimlik No")).strip(),
                "baba_adi": row.get("Baba Adı"),
                "anne_adi": row.get("Anne Adı"),
                "dogum_yeri": row.get("Doğum Yeri"),
                "dogum_tarihi": pd.to_datetime(row.get("Doğum Tarihi")).date() if pd.notna(row.get("Doğum Tarihi")) else None,
                "nufus_cuzdani_no": row.get("Nüfus Cüzdanı No"),
                "nufusa_kayitli_oldugu_il": row.get("Nüfusa Kayıtlı Olduğu İl"),
                "nufusa_kayitli_oldugu_ilce": row.get("Nüfusa Kayıtlı Olduğu İlçe"),
                "nufusa_kayitli_oldugu_mah": row.get("Nüfusa Kayıtlı Olduğu Mah-Köy"),
                "cilt_no": row.get("Cilt No"),
                "sira_no": row.get("Sıra No"),
                "kutuk_no": row.get("Kütük No"),
                "ise_giris_tarihi": pd.to_datetime(row.get("İşe Giriş Tarihi")).date() if pd.notna(row.get("İşe Giriş Tarihi")) else None,
                "isten_cikis_tarihi": pd.to_datetime(row.get("İşten Çıkış Tarihi")).date() if pd.notna(row.get("İşten Çıkış Tarihi")) else None,
                "isten_ayrilis_kodu": row.get("İşten Ayrılış Kodu"),
                "isten_ayrilis_nedeni": row.get("İşten Ayrılış Nedeni"),
                "adres": row.get("Adres"),
                "telefon": row.get("Telefon"),
                "banka_sube_adi": row.get("Banka Şube Adı"),
                "hesap_no": row.get("Hesap No"),
                "ucret": float(row.get("Ücret")) if pd.notna(row.get("Ücret")) else None,
                "net_brut": row.get("Net / Brüt"),
                "kan_grubu": row.get("Kan Grubu"),
                "meslek_kodu": row.get("Meslek Kodu"),
                "meslek_adi": row.get("Meslek Adı")
            }
            
            # Skip rows without TC Kimlik No
            if not record["tc_kimlik_no"] or record["tc_kimlik_no"] == "nan":
                continue
            
            # Skip rows without İşe Giriş Tarihi
            if not record["ise_giris_tarihi"]:
                continue
            
            records.append(record)
        
        # Process records using existing service
        sicil_service = PersonnelSicilService(self.db)
        results = sicil_service.process_sicil_upload(donem, records)
        
        return {
            "success": True,
            "message": "Personnel sicil uploaded successfully",
            "donem": donem,
            "total_records": len(records),
            "created_personnel": results.get("created_personnel", 0),
            "updated_personnel": results.get("updated_personnel", 0),
            "created_records": results.get("created_records", 0),
            "updated_records": results.get("updated_records", 0),
            "created_contracts": results.get("created_contracts", 0),
            "updated_contracts": results.get("updated_contracts", 0),
            "new_personnel": results.get("created_personnel", 0),
            "new_contracts": results.get("created_contracts", 0),
            "errors": results.get("errors", [])
        }
