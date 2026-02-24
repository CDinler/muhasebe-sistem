"""Puantaj Grid domain repository"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.models import PersonnelPuantajGrid
from app.models import Personnel
from app.models import PersonnelContract
from app.models import PersonnelDraftContract
from app.models import Contact
from app.models import MonthlyPersonnelRecord


class PuantajGridRepository:
    """Repository for Puantaj Grid operations"""
    
    def __init__(self):
        self.model = PersonnelPuantajGrid
    
    def get_grid_records(
        self,
        db: Session,
        donem: str,
        cost_center_id: Optional[int] = None
    ) -> List[PersonnelPuantajGrid]:
        """Get grid records for a period - returns latest record per personnel+contract combination
        NOT: cost_center_id parametresi kullanılmıyor - filtreleme service katmanında draft contract'a göre yapılıyor"""
        from sqlalchemy import func
        
        # Subquery to get latest record ID for each personnel+contract+donem combination
        subquery = db.query(
            func.max(self.model.id).label('max_id')
        ).filter(
            self.model.donem == donem
        )
        
        # cost_center_id filtresi KALDIRILDI - service katmanında draft contract'a göre filtreleme yapılıyor
        # Bu sayede maliyet merkezi değiştiğinde eski grid kayıtları da güncel draft contract'a göre filtrelenir
        
        subquery = subquery.group_by(
            self.model.personnel_id,
            self.model.cost_center_id,
            self.model.donem
        ).subquery()
        
        # Get the actual records with those IDs
        query = db.query(self.model).filter(
            self.model.id.in_(db.query(subquery.c.max_id))
        )
        
        return query.all()
    
    def get_by_personnel_and_donem(
        self,
        db: Session,
        personnel_id: int,
        donem: str
    ) -> Optional[PersonnelPuantajGrid]:
        """Get grid record by personnel ID and period (DEPRECATED - use get_by_personnel_contract_donem)"""
        return db.query(self.model).filter(
            self.model.personnel_id == personnel_id,
            self.model.donem == donem
        ).first()
    
    # get_by_personnel_contract_donem KALDIRILDI - contract_id artık tabloda yok
    # Bunun yerine get_by_personnel_donem kullanın
    
    def get_by_personnel_donem(
        self,
        db: Session,
        personnel_id: int,
        donem: str
    ) -> Optional["PersonnelPuantajGrid"]:
        """Get puantaj record by personnel_id and donem only (bir personelin bir dönemde tek puantajı var)"""
        return db.query(self.model).filter(
            self.model.personnel_id == personnel_id,
            self.model.donem == donem
        ).first()
    
    def get_active_personnel_ids(
        self,
        db: Session,
        donem_ilk_gun: date,
        donem_son_gun: date,
        cost_center_id: Optional[int] = None
    ) -> List[int]:
        """Get active personnel IDs for a period from contracts - based on date range only"""
        from sqlalchemy import or_, and_
        
        # Sadece dönem içinde çalışanları getir (is_active kontrolü YOK)
        # Çalışma takvimi 'ctipi' olanları hariç tut (NULL ve diğer değerler dahil)
        # Çalışma takvimi bilgisi draft_contract'tan alınır
        # SADECE AKTİF DRAFT CONTRACT'I OLAN personelleri getir
        query = db.query(PersonnelContract.personnel_id).join(
            PersonnelDraftContract,
            and_(
                PersonnelContract.personnel_id == PersonnelDraftContract.personnel_id,
                PersonnelDraftContract.is_active == 1
            )
        ).filter(
            PersonnelContract.ise_giris_tarihi <= donem_son_gun,
            or_(
                PersonnelContract.isten_cikis_tarihi == None,
                PersonnelContract.isten_cikis_tarihi >= donem_ilk_gun
            ),
            or_(
                PersonnelDraftContract.calisma_takvimi == None,
                PersonnelDraftContract.calisma_takvimi != 'ctipi'
            )
        )
        
        if cost_center_id:
            query = query.filter(
                PersonnelDraftContract.cost_center_id == cost_center_id
            )
        
        result = [p[0] for p in query.distinct().all()]
        
        # Debug log
        print(f"[DEBUG] get_active_personnel_ids:")
        print(f"  donem: {donem_ilk_gun} - {donem_son_gun}")
        print(f"  cost_center_id: {cost_center_id}")
        print(f"  found personnel count: {len(result)}")
        
        return result
    
    def get_personnel_batch(
        self,
        db: Session,
        personnel_ids: List[int]
    ) -> dict:
        """Get personnel records in batch"""
        personnel_list = db.query(Personnel).filter(
            Personnel.id.in_(personnel_ids)
        ).all()
        return {p.id: p for p in personnel_list}
    
    def get_contracts_batch(
        self,
        db: Session,
        personnel_ids: List[int],
        donem_ilk_gun: date,
        donem_son_gun: date
    ) -> dict:
        """Get latest contracts for personnel batch with taseron info and meslek_adi"""
        from sqlalchemy import or_
        # Query with LEFT JOIN to get taseron info, meslek_adi, and ucret_nevi
        query = db.query(
            PersonnelContract,
            Contact.name.label('taseron_name'),
            MonthlyPersonnelRecord.meslek_adi.label('meslek_adi')
        ).outerjoin(
            Contact,
            PersonnelContract.taseron_id == Contact.id
        ).outerjoin(
            MonthlyPersonnelRecord,
            PersonnelContract.monthly_personnel_records_id == MonthlyPersonnelRecord.id
        ).outerjoin(
            PersonnelDraftContract,
            PersonnelContract.personnel_draft_contracts_id == PersonnelDraftContract.id
        ).filter(
            PersonnelContract.personnel_id.in_(personnel_ids),
            PersonnelContract.ise_giris_tarihi <= donem_son_gun,
            or_(
                PersonnelContract.isten_cikis_tarihi == None,
                PersonnelContract.isten_cikis_tarihi >= donem_ilk_gun
            ),
            or_(
                PersonnelDraftContract.calisma_takvimi == None,
                PersonnelDraftContract.calisma_takvimi != 'ctipi'
            )
        ).order_by(
            PersonnelContract.personnel_id,
            PersonnelContract.ise_giris_tarihi.desc()
        )
        
        results = query.all()
        
        # Get ALL contracts for each personnel (not just latest)
        contract_dict = {}
        for contract, taseron_name, meslek_adi in results:
            # Attach taseron_name, meslek_adi to contract object
            contract._taseron_name = taseron_name
            contract._meslek_adi = meslek_adi
            
            # Add to list of contracts for this personnel
            if contract.personnel_id not in contract_dict:
                contract_dict[contract.personnel_id] = []
            contract_dict[contract.personnel_id].append(contract)
        
        return contract_dict
    
    def get_contracts_by_ids(
        self,
        db: Session,
        contract_ids: List[int]
    ) -> dict:
        """Get contracts by IDs with taseron info, meslek_adi and draft_contract"""
        from sqlalchemy.orm import joinedload
        
        if not contract_ids:
            return {}
        
        query = db.query(
            PersonnelContract,
            Contact.name.label('taseron_name'),
            MonthlyPersonnelRecord.meslek_adi.label('meslek_adi')
        ).options(
            joinedload(PersonnelContract.draft_contract)  # Eager load draft contract
        ).outerjoin(
            Contact,
            PersonnelContract.taseron_id == Contact.id
        ).outerjoin(
            MonthlyPersonnelRecord,
            PersonnelContract.monthly_personnel_records_id == MonthlyPersonnelRecord.id
        ).filter(
            PersonnelContract.id.in_(contract_ids)
        )
        
        results = query.all()
        
        contract_dict = {}
        for contract, taseron_name, meslek_adi in results:
            contract._taseron_name = taseron_name
            contract._meslek_adi = meslek_adi
            contract_dict[contract.id] = contract
        
        return contract_dict
    
    def create(self, db: Session, obj_in: PersonnelPuantajGrid) -> PersonnelPuantajGrid:
        """Create new grid record"""
        db.add(obj_in)
        db.flush()
        return obj_in
    
    def update(self, db: Session, db_obj: PersonnelPuantajGrid, **kwargs) -> PersonnelPuantajGrid:
        """Update grid record"""
        for key, value in kwargs.items():
            setattr(db_obj, key, value)
        db.flush()
        return db_obj
