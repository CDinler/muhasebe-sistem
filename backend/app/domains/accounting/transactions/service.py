"""
Transaction Service

Muhasebe fişleri için business logic.
"""
from typing import Optional, List, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.domains.accounting.transactions.repository import transaction_repo
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse


class TransactionService:
    """Transaction business logic"""
    
    def __init__(self):
        self.repo = transaction_repo
    
    def get_transaction(self, db: Session, id: int) -> Optional[Transaction]:
        """ID'ye göre fiş getir (satırlarıyla birlikte)"""
        return self.repo.get_with_lines(db, id)
    
    def get_by_number(self, db: Session, transaction_number: str) -> Optional[Transaction]:
        """Fiş numarasına göre getir"""
        return self.repo.get_by_number(db, transaction_number)
    
    def list_transactions(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        cost_center_id: Optional[int] = None,
        document_type_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fişleri filtrele ve listele (pagination ile)"""
        transactions = self.repo.get_filtered(
            db=db,
            skip=skip,
            limit=limit,
            date_from=date_from,
            date_to=date_to,
            cost_center_id=cost_center_id,
            document_type_id=document_type_id,
            search=search
        )
        
        total = self.repo.count_filtered(
            db=db,
            date_from=date_from,
            date_to=date_to,
            cost_center_id=cost_center_id,
            document_type_id=document_type_id,
            search=search
        )
        
        return {
            'items': transactions,
            'total': total,
            'skip': skip,
            'limit': limit
        }
    
    def get_summary(
        self,
        db: Session,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """Fiş özet istatistikleri"""
        return self.repo.get_summary(db, date_from, date_to)
    
    def create_transaction(
        self,
        db: Session,
        transaction_data: TransactionCreate
    ) -> Transaction:
        """Yeni fiş oluştur (satırlarıyla birlikte)"""
        # Fiş numarası kontrolü
        existing = self.repo.get_by_number(db, transaction_data.transaction_number)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Fiş numarası zaten mevcut: {transaction_data.transaction_number}"
            )
        
        # Transaction oluştur
        return self.repo.create(db, obj_in=transaction_data)
    
    def update_transaction(
        self,
        db: Session,
        id: int,
        transaction_data: TransactionCreate
    ) -> Transaction:
        """Fiş güncelle"""
        transaction = self.repo.get(db, id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Fiş bulunamadı")
        
        return self.repo.update(db, db_obj=transaction, obj_in=transaction_data)
    
    def delete_transaction(self, db: Session, id: int) -> bool:
        """Fiş sil (cascade satırları da siler)"""
        transaction = self.repo.get(db, id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Fiş bulunamadı")
        
        self.repo.delete(db, id=id)
        return True


# Singleton instance
transaction_service = TransactionService()
