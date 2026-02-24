"""
E-Invoice Service

İş mantığı ve business rules.
"""
from typing import Optional, List, Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from app.domains.invoicing.einvoices.repository import einvoice_repo
from app.domains.invoicing.einvoices.models import EInvoice
from app.domains.invoicing.einvoices.schemas import EInvoiceCreate, EInvoiceUpdate


class EInvoiceService:
    """E-Fatura business logic"""
    
    def __init__(self):
        self.repo = einvoice_repo
    
    def get_summary(
        self,
        db: Session,
        *,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """Özet istatistikler al"""
        return self.repo.get_summary(
            db,
            date_from=date_from,
            date_to=date_to
        )
    
    def get_invoices(
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
        return self.repo.get_filtered(
            db,
            skip=skip,
            limit=limit,
            invoice_category=invoice_category,
            processing_status=processing_status,
            supplier_name=supplier_name,
            invoice_number=invoice_number,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_order=sort_order
        )
    
    def get_unpaid_invoices(
        self,
        db: Session,
        *,
        invoice_category: Optional[str] = 'incoming'
    ) -> List[EInvoice]:
        """
        Ödenmeyen veya kısmi ödenmiş faturaları getir
        
        paid_amount < payable_amount olan faturaları döner
        """
        query = db.query(EInvoice).filter(
            EInvoice.invoice_category == invoice_category,
            EInvoice.payable_amount > 0
        )
        
        # paid_amount'u kontrol et
        invoices = query.all()
        unpaid_invoices = [inv for inv in invoices if inv.paid_amount < inv.payable_amount]
        
        return unpaid_invoices
    
    def get_by_id(self, db: Session, invoice_id: int) -> Optional[EInvoice]:
        """ID ile fatura getir"""
        return self.repo.get(db, id=invoice_id)
    
    def get_by_uuid(self, db: Session, invoice_uuid: str) -> Optional[EInvoice]:
        """UUID ile fatura getir"""
        return self.repo.get_by_uuid(db, invoice_uuid=invoice_uuid)
    
    def create_invoice(
        self,
        db: Session,
        *,
        invoice_data: EInvoiceCreate
    ) -> EInvoice:
        """Yeni fatura oluştur"""
        # Mükerrer kontrol (XML hash varsa)
        if invoice_data.xml_hash:
            existing = self.repo.get_by_xml_hash(db, xml_hash=invoice_data.xml_hash)
            if existing:
                raise ValueError(f"Bu fatura zaten mevcut (ID: {existing.id})")
        
        # UUID kontrolü
        existing_uuid = self.repo.get_by_uuid(db, invoice_uuid=invoice_data.invoice_uuid)
        if existing_uuid:
            raise ValueError(f"Bu UUID zaten kullanımda (ID: {existing_uuid.id})")
        
        return self.repo.create(db, obj_in=invoice_data)
    
    def update_invoice(
        self,
        db: Session,
        *,
        invoice_id: int,
        invoice_data: EInvoiceUpdate
    ) -> Optional[EInvoice]:
        """Fatura güncelle"""
        invoice = self.repo.get(db, id=invoice_id)
        if not invoice:
            return None
        
        return self.repo.update(db, db_obj=invoice, obj_in=invoice_data)
    
    def delete_invoice(self, db: Session, invoice_id: int) -> bool:
        """Fatura sil"""
        invoice = self.repo.get(db, id=invoice_id)
        if not invoice:
            return False
        
        self.repo.remove(db, id=invoice_id)
        return True
    
    def update_processing_status(
        self,
        db: Session,
        *,
        invoice_id: int,
        status: str,
        error_message: Optional[str] = None
    ) -> Optional[EInvoice]:
        """İşlem durumunu güncelle"""
        update_data = EInvoiceUpdate(
            processing_status=status,
            processing_error=error_message
        )
        return self.update_invoice(
            db,
            invoice_id=invoice_id,
            invoice_data=update_data
        )


# Singleton instance
einvoice_service = EInvoiceService()
