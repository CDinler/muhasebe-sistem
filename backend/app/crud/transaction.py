"""Transaction CRUD operations"""
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date

from app.models.transaction import Transaction
from app.models.transaction_line import TransactionLine
from app.schemas.transaction import TransactionCreate, TransactionLineCreate

def get_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    """Tek fiş getir"""
    return db.query(Transaction).options(
        joinedload(Transaction.lines),
        joinedload(Transaction.doc_type),
        joinedload(Transaction.doc_subtype),
        joinedload(Transaction.cost_center)
    ).filter(Transaction.id == transaction_id).first()

def get_transaction_by_number(db: Session, transaction_number: str) -> Optional[Transaction]:
    """Fiş numarasına göre getir"""
    return db.query(Transaction).options(
        joinedload(Transaction.lines),
        joinedload(Transaction.doc_type),
        joinedload(Transaction.doc_subtype),
        joinedload(Transaction.cost_center)
    ).filter(Transaction.transaction_number == transaction_number).first()

def get_transactions(
    db: Session,
    skip: int = 0,
    limit: int = 100,  # Sayfa başına kayıt
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    cost_center_id: Optional[int] = None,
    order_by: str = "date_desc",
    search: Optional[str] = None
) -> List[Transaction]:
    """Fişleri listele (filtreleme ile) - Eager loading ile N+1 çözümü"""
    query = db.query(Transaction).options(
        joinedload(Transaction.lines),
        joinedload(Transaction.doc_type),
        joinedload(Transaction.doc_subtype),
        joinedload(Transaction.cost_center)
    )
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    if cost_center_id:
        query = query.filter(Transaction.cost_center_id == cost_center_id)
    
    # Arama filtresi
    if search:
        search_pattern = f"%{search}%"
        from app.models.document_type import DocumentType, DocumentSubtype
        query = query.outerjoin(Transaction.doc_type).outerjoin(Transaction.doc_subtype).filter(
            (Transaction.transaction_number.like(search_pattern)) |
            (Transaction.description.like(search_pattern)) |
            (DocumentType.name.like(search_pattern)) |
            (DocumentSubtype.name.like(search_pattern)) |
            (Transaction.document_number.like(search_pattern))
        )
    
    # Sıralama
    if order_by == "date_asc":
        query = query.order_by(Transaction.transaction_date.asc())
    elif order_by == "date_desc":
        query = query.order_by(Transaction.transaction_date.desc())
    elif order_by == "number_asc":
        query = query.order_by(Transaction.transaction_number.asc())
    elif order_by == "number_desc":
        query = query.order_by(Transaction.transaction_number.desc())
    else:
        query = query.order_by(Transaction.transaction_date.desc())
    
    return query.offset(skip).limit(limit).all()

def get_transactions_count(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    cost_center_id: Optional[int] = None,
    search: Optional[str] = None
) -> int:
    """Toplam fiş sayısını döndür"""
    query = db.query(Transaction)
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    if cost_center_id:
        query = query.filter(Transaction.cost_center_id == cost_center_id)
    
    # Arama filtresi
    if search:
        search_pattern = f"%{search}%"
        from app.models.document_type import DocumentType, DocumentSubtype
        query = query.outerjoin(Transaction.doc_type).outerjoin(Transaction.doc_subtype).filter(
            (Transaction.transaction_number.like(search_pattern)) |
            (Transaction.description.like(search_pattern)) |
            (DocumentType.name.like(search_pattern)) |
            (DocumentSubtype.name.like(search_pattern)) |
            (Transaction.document_number.like(search_pattern))
        )
    
    return query.count()

def create_transaction(db: Session, transaction: TransactionCreate) -> Transaction:
    """Yeni fiş oluştur"""
    # Fiş başlığı
    db_transaction = Transaction(
        transaction_number=transaction.transaction_number,
        transaction_date=transaction.transaction_date,
        accounting_period=transaction.accounting_period,
        cost_center_id=transaction.cost_center_id,
        description=transaction.description,
        document_type_id=transaction.document_type_id,
        document_subtype_id=transaction.document_subtype_id,
        document_number=transaction.document_number,
        related_invoice_number=transaction.related_invoice_number
    )
    db.add(db_transaction)
    db.flush()  # ID'yi al
    
    # Fiş satırları
    for line in transaction.lines:
        db_line = TransactionLine(
            transaction_id=db_transaction.id,
            account_id=line.account_id,
            contact_id=line.contact_id,
            description=line.description,
            debit=line.debit,
            credit=line.credit,
            quantity=line.quantity,
            unit=line.unit
        )
        db.add(db_line)
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def update_transaction(db: Session, transaction_id: int, transaction: TransactionCreate) -> Optional[Transaction]:
    """Fişi güncelle"""
    db_transaction = get_transaction(db, transaction_id)
    if not db_transaction:
        return None
    
    # Başlık güncelle
    for key, value in transaction.dict(exclude={'lines'}).items():
        setattr(db_transaction, key, value)
    
    # Eski satırları sil
    db.query(TransactionLine).filter(TransactionLine.transaction_id == transaction_id).delete()
    
    # Yeni satırları ekle
    for line in transaction.lines:
        db_line = TransactionLine(
            transaction_id=transaction_id,
            account_id=line.account_id,
            contact_id=line.contact_id,
            description=line.description,
            debit=line.debit,
            credit=line.credit,
            quantity=line.quantity,
            unit=line.unit
        )
        db.add(db_line)
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: int) -> bool:
    """Fişi sil"""
    db_transaction = get_transaction(db, transaction_id)
    if not db_transaction:
        return False
    
    db.delete(db_transaction)
    db.commit()
    return True
