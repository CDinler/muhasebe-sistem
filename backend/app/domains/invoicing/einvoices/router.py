"""
E-Invoice Router (V2 API)

DDD mimarisine uygun yeni API endpoint'leri.
Mevcut V1 endpoint'leri backward compatibility için korunur.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.domains.invoicing.einvoices.service import einvoice_service
from app.schemas.einvoice import (
    EInvoice as EInvoiceSchema,
    EInvoiceCreate,
    EInvoiceUpdate,
    EInvoiceSummary
)
from app.services.einvoice_accounting_service import generate_transaction_preview
from app.models.einvoice import EInvoice


router = APIRouter(tags=['E-Invoice (V2)'])


@router.get('/summary', response_model=EInvoiceSummary)
def get_summary(
    date_from: Optional[date] = Query(None, description='Başlangıç tarihi'),
    date_to: Optional[date] = Query(None, description='Bitiş tarihi'),
    db: Session = Depends(get_db)
):
    """
    E-fatura özet istatistikleri
    
    - **date_from**: Başlangıç tarihi (opsiyonel)
    - **date_to**: Bitiş tarihi (opsiyonel)
    """
    summary_data = einvoice_service.get_summary(
        db,
        date_from=date_from,
        date_to=date_to
    )
    return summary_data


@router.get('/', response_model=List[EInvoiceSchema])
def get_invoices(
    skip: int = Query(0, ge=0, description='Atlanacak kayıt sayısı'),
    limit: int = Query(50, ge=1, le=500, description='Maksimum kayıt sayısı'),
    invoice_category: Optional[str] = Query(None, description='Fatura kategorisi'),
    processing_status: Optional[str] = Query(None, description='İşlem durumu'),
    supplier_name: Optional[str] = Query(None, description='Tedarikçi adı'),
    invoice_number: Optional[str] = Query(None, description='Fatura numarası'),
    date_from: Optional[date] = Query(None, description='Başlangıç tarihi'),
    date_to: Optional[date] = Query(None, description='Bitiş tarihi'),
    sort_by: str = Query('issue_date', description='Sıralama alanı'),
    sort_order: str = Query('desc', regex='^(asc|desc)$', description='Sıralama yönü'),
    db: Session = Depends(get_db)
):
    """
    Filtrelenmiş e-fatura listesi
    
    - **invoice_category**: incoming, outgoing, incoming-archive, outgoing-archive
    - **processing_status**: PENDING, IMPORTED, TRANSACTION_CREATED, ERROR
    - **sort_by**: issue_date, invoice_number, payable_amount, vb.
    - **sort_order**: asc veya desc
    """
    invoices = einvoice_service.get_invoices(
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
    return invoices


@router.get('/{invoice_id}', response_model=EInvoiceSchema)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    """
    ID ile fatura detayı
    """
    invoice = einvoice_service.get_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail='Fatura bulunamadı')
    return invoice


@router.post('/', response_model=EInvoiceSchema, status_code=201)
def create_invoice(
    invoice_data: EInvoiceCreate,
    db: Session = Depends(get_db)
):
    """
    Yeni e-fatura oluştur
    """
    try:
        invoice = einvoice_service.create_invoice(db, invoice_data=invoice_data)
        return invoice
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put('/{invoice_id}', response_model=EInvoiceSchema)
def update_invoice(
    invoice_id: int,
    invoice_data: EInvoiceUpdate,
    db: Session = Depends(get_db)
):
    """
    Fatura güncelle
    """
    invoice = einvoice_service.update_invoice(
        db,
        invoice_id=invoice_id,
        invoice_data=invoice_data
    )
    if not invoice:
        raise HTTPException(status_code=404, detail='Fatura bulunamadı')
    return invoice


@router.delete('/{invoice_id}', status_code=204)
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    """
    Fatura sil
    """
    success = einvoice_service.delete_invoice(db, invoice_id)
    if not success:
        raise HTTPException(status_code=404, detail='Fatura bulunamadı')
    return None


@router.post('/{invoice_id}/preview-import')
def preview_import(
    invoice_id: int,
    category_data: Optional[dict] = None,
    cost_center_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Import önizleme - Kullanıcıya muhasebe kaydını göster (kayıt oluşturmaz)
    
    Args:
        invoice_id: E-fatura ID
        category_data: Opsiyonel kategorizasyon verisi
        cost_center_id: Opsiyonel maliyet merkezi ID
    
    Returns:
        - Cari bilgisi (mevcut/yeni)
        - Fiş satırları (hesap, borç, alacak)
        - Uyarılar (eksik hesap vb.)
    """
    einvoice = db.query(EInvoice).filter(EInvoice.id == invoice_id).first()
    if not einvoice:
        raise HTTPException(status_code=404, detail='E-fatura bulunamadı')
    
    if einvoice.processing_status == 'COMPLETED':
        raise HTTPException(status_code=400, detail='Bu fatura zaten import edilmiş')
    
    # Service'den önizleme al
    return generate_transaction_preview(db, einvoice, category_data, cost_center_id)
