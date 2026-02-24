"""
Transaction Repository

Muhasebe fişleri için veritabanı işlemleri.
"""
from typing import Optional, List, Dict, Any
from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, or_, and_

from app.shared.base.repository import CRUDBase
from app.domains.accounting.transactions.models import Transaction, TransactionLine
from app.domains.accounting.transactions.schemas import TransactionCreate, TransactionResponse


class TransactionRepository(CRUDBase[Transaction, TransactionCreate, TransactionResponse]):
    """Transaction repository with domain-specific queries"""
    
    def get_with_lines(self, db: Session, id: int) -> Optional[Transaction]:
        """Fiş ve satırlarını birlikte getir"""
        return (
            db.query(Transaction)
            .options(
                joinedload(Transaction.lines).joinedload(TransactionLine.account),
                joinedload(Transaction.lines).joinedload(TransactionLine.contact),
                joinedload(Transaction.cost_center),
                joinedload(Transaction.doc_type)
            )
            .filter(Transaction.id == id)
            .first()
        )
    
    def get_by_number(self, db: Session, transaction_number: str) -> Optional[Transaction]:
        """Fiş numarasına göre getir"""
        return (
            db.query(Transaction)
            .filter(Transaction.transaction_number == transaction_number)
            .first()
        )
    
    def get_by_period(
        self, 
        db: Session, 
        accounting_period: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Transaction]:
        """Döneme göre fişleri getir"""
        return (
            db.query(Transaction)
            .filter(Transaction.accounting_period == accounting_period)
            .options(joinedload(Transaction.cost_center))
            .order_by(desc(Transaction.transaction_date), desc(Transaction.id))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_filtered(
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
    ) -> List[Transaction]:
        """Filtrelere göre fişleri getir"""
        query = db.query(Transaction)
        
        if date_from:
            query = query.filter(Transaction.transaction_date >= date_from)
        if date_to:
            query = query.filter(Transaction.transaction_date <= date_to)
        if cost_center_id:
            query = query.filter(Transaction.cost_center_id == cost_center_id)
        if document_type_id:
            query = query.filter(Transaction.document_type_id == document_type_id)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Transaction.transaction_number.ilike(search_pattern),
                    Transaction.description.ilike(search_pattern),
                    Transaction.document_number.ilike(search_pattern)
                )
            )
        
        # Apply ordering
        if order_by == 'date_asc':
            query = query.order_by(Transaction.transaction_date.asc(), Transaction.id.asc())
        elif order_by == 'date_desc':
            query = query.order_by(desc(Transaction.transaction_date), desc(Transaction.id))
        elif order_by == 'number_asc':
            query = query.order_by(Transaction.transaction_number.asc())
        elif order_by == 'number_desc':
            query = query.order_by(desc(Transaction.transaction_number))
        else:  # default to number_desc
            query = query.order_by(desc(Transaction.transaction_number))
        
        return (
            query
            .options(
                joinedload(Transaction.cost_center),
                joinedload(Transaction.doc_type)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def count_filtered(
        self,
        db: Session,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        cost_center_id: Optional[int] = None,
        document_type_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> int:
        """Filtrelere göre toplam kayıt sayısı"""
        query = db.query(func.count(Transaction.id))
        
        if date_from:
            query = query.filter(Transaction.transaction_date >= date_from)
        if date_to:
            query = query.filter(Transaction.transaction_date <= date_to)
        if cost_center_id:
            query = query.filter(Transaction.cost_center_id == cost_center_id)
        if document_type_id:
            query = query.filter(Transaction.document_type_id == document_type_id)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Transaction.transaction_number.ilike(search_pattern),
                    Transaction.description.ilike(search_pattern),
                    Transaction.document_number.ilike(search_pattern)
                )
            )
        
        return query.scalar() or 0
    
    def get_summary(
        self,
        db: Session,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """Fiş özet istatistikleri"""
        query = db.query(Transaction)
        
        if date_from:
            query = query.filter(Transaction.transaction_date >= date_from)
        if date_to:
            query = query.filter(Transaction.transaction_date <= date_to)
        
        total_count = query.count()
        
        # Masraf merkezine göre dağılım
        by_cost_center = (
            db.query(
                Transaction.cost_center_id,
                func.count(Transaction.id).label('count')
            )
            .filter(
                and_(
                    Transaction.transaction_date >= date_from if date_from else True,
                    Transaction.transaction_date <= date_to if date_to else True
                )
            )
            .group_by(Transaction.cost_center_id)
            .all()
        )
        
        return {
            'total_count': total_count,
            'by_cost_center': [
                {'cost_center_id': cc_id, 'count': count}
                for cc_id, count in by_cost_center
            ]
        }


# Singleton instance
transaction_repo = TransactionRepository(Transaction)
