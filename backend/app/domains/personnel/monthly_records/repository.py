"""Monthly Personnel Records domain repository"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.shared.base.repository import CRUDBase
from app.models import MonthlyPersonnelRecord
from app.domains.personnel.monthly_records.schemas import (
    MonthlyPersonnelRecordCreate,
    MonthlyPersonnelRecordUpdate
)


class MonthlyPersonnelRecordRepository(CRUDBase[MonthlyPersonnelRecord, MonthlyPersonnelRecordCreate, MonthlyPersonnelRecordUpdate]):
    """Monthly Personnel Record repository with custom queries"""
    
    def __init__(self):
        super().__init__(MonthlyPersonnelRecord)
    
    def get_by_donem(
        self, 
        db: Session, 
        donem: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[MonthlyPersonnelRecord]:
        """Get records by period"""
        return db.query(self.model).filter(
            MonthlyPersonnelRecord.donem == donem
        ).offset(skip).limit(limit).all()
    
    def get_by_personnel_id(
        self,
        db: Session,
        personnel_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[MonthlyPersonnelRecord]:
        """Get records by personnel ID"""
        return db.query(self.model).filter(
            MonthlyPersonnelRecord.personnel_id == personnel_id
        ).offset(skip).limit(limit).all()
    
    def count_filtered(
        self,
        db: Session,
        donem: Optional[str] = None,
        personnel_id: Optional[int] = None
    ) -> int:
        """Count records with filters"""
        query = db.query(self.model)
        
        if donem:
            query = query.filter(MonthlyPersonnelRecord.donem == donem)
        
        if personnel_id:
            query = query.filter(MonthlyPersonnelRecord.personnel_id == personnel_id)
        
        return query.count()
    
    def get_periods(self, db: Session) -> List[str]:
        """Get all distinct periods"""
        periods = db.query(MonthlyPersonnelRecord.donem).distinct().order_by(
            MonthlyPersonnelRecord.donem.desc()
        ).all()
        return [p[0] for p in periods if p[0]]
    
    def get_filtered(
        self,
        db: Session,
        donem: Optional[str] = None,
        personnel_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[MonthlyPersonnelRecord]:
        """Get records with filters"""
        query = db.query(self.model)
        
        if donem:
            query = query.filter(MonthlyPersonnelRecord.donem == donem)
        
        if personnel_id:
            query = query.filter(MonthlyPersonnelRecord.personnel_id == personnel_id)
        
        return query.offset(skip).limit(limit).all()
