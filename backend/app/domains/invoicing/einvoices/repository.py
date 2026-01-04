"""
E-Invoice Repository

Veritabanı işlemleri için CRUD operasyonları.
"""
from typing import Optional, List, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_, and_

from app.shared.base.repository import CRUDBase
from app.models.einvoice import EInvoice
from app.schemas.einvoice import EInvoiceCreate, EInvoiceUpdate


class EInvoiceRepository(CRUDBase[EInvoice, EInvoiceCreate, EInvoiceUpdate]):
    """E-Fatura repository"""
    
    def get_by_uuid(self, db: Session, *, invoice_uuid: str) -> Optional[EInvoice]:
        """UUID ile fatura bul"""
        return db.query(EInvoice).filter(EInvoice.invoice_uuid == invoice_uuid).first()
    
    def get_by_xml_hash(self, db: Session, *, xml_hash: str) -> Optional[EInvoice]:
        """XML hash ile fatura bul (mükerrer kontrol)"""
        return db.query(EInvoice).filter(EInvoice.xml_hash == xml_hash).first()
    
    def get_summary(
        self,
        db: Session,
        *,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """Özet istatistikler"""
        base_query = db.query(EInvoice)
        
        if date_from:
            base_query = base_query.filter(EInvoice.issue_date >= date_from)
        if date_to:
            base_query = base_query.filter(EInvoice.issue_date <= date_to)
        
        total_count = base_query.with_entities(func.count(EInvoice.id)).scalar()
        total_amount = base_query.with_entities(func.sum(EInvoice.payable_amount)).scalar() or 0
        
        parsed_count = base_query.filter(
            EInvoice.processing_status == 'IMPORTED'
        ).with_entities(func.count(EInvoice.id)).scalar()
        
        imported_count = base_query.filter(
            EInvoice.processing_status == 'TRANSACTION_CREATED'
        ).with_entities(func.count(EInvoice.id)).scalar()
        
        error_count = base_query.filter(
            EInvoice.processing_status == 'ERROR'
        ).with_entities(func.count(EInvoice.id)).scalar()
        
        pending_count = base_query.filter(
            or_(
                EInvoice.processing_status == 'MATCHED',
                EInvoice.processing_status == 'PENDING'
            )
        ).with_entities(func.count(EInvoice.id)).scalar()
        
        # Kategorilere göre
        incoming_count = base_query.filter(
            EInvoice.invoice_category == 'incoming'
        ).with_entities(func.count(EInvoice.id)).scalar() or 0
        
        incoming_amount = base_query.filter(
            EInvoice.invoice_category == 'incoming'
        ).with_entities(func.sum(EInvoice.payable_amount)).scalar() or 0
        
        incoming_archive_count = base_query.filter(
            EInvoice.invoice_category == 'incoming-archive'
        ).with_entities(func.count(EInvoice.id)).scalar() or 0
        
        incoming_archive_amount = base_query.filter(
            EInvoice.invoice_category == 'incoming-archive'
        ).with_entities(func.sum(EInvoice.payable_amount)).scalar() or 0
        
        outgoing_count = base_query.filter(
            EInvoice.invoice_category == 'outgoing'
        ).with_entities(func.count(EInvoice.id)).scalar() or 0
        
        outgoing_amount = base_query.filter(
            EInvoice.invoice_category == 'outgoing'
        ).with_entities(func.sum(EInvoice.payable_amount)).scalar() or 0
        
        outgoing_archive_count = base_query.filter(
            EInvoice.invoice_category == 'outgoing-archive'
        ).with_entities(func.count(EInvoice.id)).scalar() or 0
        
        outgoing_archive_amount = base_query.filter(
            EInvoice.invoice_category == 'outgoing-archive'
        ).with_entities(func.sum(EInvoice.payable_amount)).scalar() or 0
        
        return {
            'total_count': total_count or 0,
            'total_amount': float(total_amount),
            'parsed_count': parsed_count or 0,
            'imported_count': imported_count or 0,
            'error_count': error_count or 0,
            'pending_count': pending_count or 0,
            'incoming_count': incoming_count,
            'incoming_amount': float(incoming_amount),
            'incoming_archive_count': incoming_archive_count,
            'incoming_archive_amount': float(incoming_archive_amount),
            'outgoing_count': outgoing_count,
            'outgoing_amount': float(outgoing_amount),
            'outgoing_archive_count': outgoing_archive_count,
            'outgoing_archive_amount': float(outgoing_archive_amount),
        }
    
    def get_filtered(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 50,
        invoice_category: Optional[str] = None,
        processing_status: Optional[str] = None,
        supplier_name: Optional[str] = None,
        invoice_number: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        sort_by: str = 'issue_date',
        sort_order: str = 'desc'
    ) -> List[EInvoice]:
        """Filtrelenmiş fatura listesi"""
        query = db.query(EInvoice)
        
        if invoice_category:
            query = query.filter(EInvoice.invoice_category == invoice_category)
        
        if processing_status:
            query = query.filter(EInvoice.processing_status == processing_status)
        
        if supplier_name:
            query = query.filter(EInvoice.supplier_name.ilike(f'%{supplier_name}%'))
        
        if invoice_number:
            query = query.filter(EInvoice.invoice_number.ilike(f'%{invoice_number}%'))
        
        if date_from:
            query = query.filter(EInvoice.issue_date >= date_from)
        
        if date_to:
            query = query.filter(EInvoice.issue_date <= date_to)
        
        # Sorting
        if sort_order == 'desc':
            query = query.order_by(desc(getattr(EInvoice, sort_by)))
        else:
            query = query.order_by(getattr(EInvoice, sort_by))
        
        return query.offset(skip).limit(limit).all()


# Singleton instance
einvoice_repo = EInvoiceRepository(EInvoice)
