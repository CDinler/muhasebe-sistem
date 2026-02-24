"""
Transaction Service

Muhasebe fişleri için business logic.
"""
from typing import Optional, List, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.domains.accounting.transactions.repository import transaction_repo
from app.models import Transaction, TransactionLine
from app.domains.accounting.transactions.schemas import TransactionCreate, TransactionResponse
from app.utils.transaction_numbering import get_next_transaction_number


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
        search: Optional[str] = None,
        order_by: Optional[str] = None
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
            search=search,
            order_by=order_by
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
        # Fiş numarası boşsa otomatik üret
        if not transaction_data.transaction_number or transaction_data.transaction_number.strip() == "":
            transaction_data.transaction_number = get_next_transaction_number(db, prefix="F")
        else:
            # Fiş numarası kontrolü
            existing = self.repo.get_by_number(db, transaction_data.transaction_number)
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Fiş numarası zaten mevcut: {transaction_data.transaction_number}"
                )
        
        # Lines'ı ayır
        lines_data = transaction_data.lines
        transaction_dict = transaction_data.dict(exclude={'lines'})
        
        # Transaction oluştur (lines olmadan)
        transaction = Transaction(**transaction_dict)
        db.add(transaction)
        db.flush()  # ID almak için
        
        # Lines ekle
        for line_data in lines_data:
            line_dict = line_data.dict() if hasattr(line_data, 'dict') else line_data
            line = TransactionLine(
                transaction_id=transaction.id,
                **line_dict
            )
            db.add(line)
        
        db.commit()
        db.refresh(transaction)
        return transaction
    
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
        
        # Extract lines data before update
        lines_data = transaction_data.lines if hasattr(transaction_data, 'lines') else []
        transaction_dict = transaction_data.dict(exclude={'lines'})
        
        # Update transaction header fields
        for field, value in transaction_dict.items():
            if value is not None:
                setattr(transaction, field, value)
        
        # Delete existing lines
        db.query(TransactionLine).filter(TransactionLine.transaction_id == id).delete()
        
        # Create new lines
        for line_data in lines_data:
            line_dict = line_data if isinstance(line_data, dict) else line_data.dict()
            line = TransactionLine(
                transaction_id=id,
                **line_dict
            )
            db.add(line)
        
        db.commit()
        db.refresh(transaction)
        return transaction
    
    def delete_transaction(self, db: Session, id: int) -> bool:
        """Fiş sil (cascade satırları da siler)"""
        from app.models import TransactionLine
        
        transaction = self.repo.get(db, id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Fiş bulunamadı")
        
        try:
            # Manuel silme - önce satırlar, sonra fiş
            db.query(TransactionLine).filter(TransactionLine.transaction_id == id).delete()
            db.query(Transaction).filter(Transaction.id == id).delete()
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, 
                detail=f"Fiş silinirken hata oluştu: {str(e)}"
            )


# Singleton instance
transaction_service = TransactionService()
