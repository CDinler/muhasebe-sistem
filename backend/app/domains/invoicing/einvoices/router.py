"""
E-Invoice Router (V2 API)

DDD mimarisine uygun yeni API endpoint'leri.
Mevcut V1 endpoint'leri backward compatibility için korunur.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body, UploadFile, File
from fastapi.responses import Response, FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pathlib import Path

from app.core.database import get_db
from app.core.config import settings
from app.domains.auth.dependencies import get_current_user
from app.schemas.auth import UserInDB
from app.domains.invoicing.einvoices.service import einvoice_service
from app.domains.invoicing.einvoices.schemas import (
    EInvoice as EInvoiceSchema,
    EInvoiceCreate,
    EInvoiceUpdate,
    EInvoiceSummary
)
from app.services.einvoice_accounting_service import generate_transaction_preview
from app.models import EInvoice


router = APIRouter(tags=['E-Invoice (V2)'])


@router.get('/summary', response_model=EInvoiceSummary)
def get_summary(
    date_from: Optional[date] = Query(None, description='Başlangıç tarihi'),
    date_to: Optional[date] = Query(None, description='Bitiş tarihi'),
    current_user: UserInDB = Depends(get_current_user),
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


@router.get('/unpaid', response_model=List[EInvoiceSchema])
def get_unpaid_invoices(
    invoice_category: Optional[str] = Query('incoming', description='Fatura kategorisi'),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ödenmeyen veya kısmi ödenmiş faturaları getir
    
    payment_status IN ('UNPAID', 'PARTIALLY_PAID') olan faturaları döner
    """
    invoices = einvoice_service.get_unpaid_invoices(db, invoice_category=invoice_category)
    return invoices


@router.get('/aging-report')
def get_aging_report(
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Alacak yaşlandırma raporu
    
    Faturaları vadelerine göre gruplar:
    - 0-30 gün: Vadesi geçmemiş
    - 31-60 gün: 1 ay gecikmeli
    - 61-90 gün: 2 ay gecikmeli
    - 90+ gün: 3+ ay gecikmeli
    """
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    today = datetime.now().date()
    invoices = einvoice_service.get_unpaid_invoices(db, invoice_category='incoming')
    
    aging = {
        'current': {'count': 0, 'amount': 0},  # 0-30 gün
        '30_60': {'count': 0, 'amount': 0},    # 31-60 gün
        '60_90': {'count': 0, 'amount': 0},    # 61-90 gün
        'over_90': {'count': 0, 'amount': 0}   # 90+ gün
    }
    
    for inv in invoices:
        if not inv.issue_date:
            continue
            
        days_old = (today - inv.issue_date).days
        remaining = float(inv.remaining_amount)
        
        if days_old <= 30:
            aging['current']['count'] += 1
            aging['current']['amount'] += remaining
        elif days_old <= 60:
            aging['30_60']['count'] += 1
            aging['30_60']['amount'] += remaining
        elif days_old <= 90:
            aging['60_90']['count'] += 1
            aging['60_90']['amount'] += remaining
        else:
            aging['over_90']['count'] += 1
            aging['over_90']['amount'] += remaining
    
    return aging


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
    current_user: UserInDB = Depends(get_current_user),
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


@router.post('/', response_model=EInvoiceSchema, status_code=201)
def create_invoice(
    invoice_data: EInvoiceCreate,
    current_user: UserInDB = Depends(get_current_user),
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


@router.post('/{invoice_id}/preview-import')
def preview_import(
    invoice_id: int,
    request_body: dict = Body(default={}),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Import önizleme - Kullanıcıya muhasebe kaydını göster (kayıt oluşturmaz)
    
    Args:
        invoice_id: E-fatura ID
        request_body: {
            "invoice_lines_mapping": [...],  # Opsiyonel
            "cost_center_id": 123             # Opsiyonel
        }
    
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
    
    # Request body'den parametreleri çıkar
    category_data = request_body.get('invoice_lines_mapping') or request_body if request_body else None
    cost_center_id = request_body.get('cost_center_id')
    
    # Service'den önizleme al
    return generate_transaction_preview(db, einvoice, category_data, cost_center_id)


@router.post('/{invoice_id}/import')
async def import_to_accounting(
    invoice_id: int,
    data: dict = Body(...),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """E-faturayı muhasebeye aktar - custom transaction oluştur"""
    from app.services.einvoice_accounting_service import create_custom_transaction, create_or_get_contact
    
    # E-faturayı bul
    einvoice = db.query(EInvoice).filter(EInvoice.id == invoice_id).first()
    if not einvoice:
        raise HTTPException(status_code=404, detail="E-Invoice not found")
    
    # Contact'ı oluştur veya bul
    contact = create_or_get_contact(db, einvoice)
    
    # Custom transaction oluştur (frontend'den gelen data ile)
    try:
        transaction = create_custom_transaction(
            db=db,
            einvoice=einvoice,
            contact=contact,
            transaction_data=data
        )
        
        # E-faturanın durumunu güncelle
        einvoice.processing_status = 'COMPLETED'
        einvoice.transaction_id = transaction.id
        db.commit()
        
        return {
            'success': True,
            'transaction_id': transaction.id,
            'message': 'Muhasebe fişi oluşturuldu'
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/{invoice_id}/transaction')
async def create_transaction(
    invoice_id: int,
    data: dict = Body(...),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    E-fatura için yevmiye oluştur
    TODO: Implement transaction creation
    """
    raise HTTPException(
        status_code=501,
        detail="Transaction creation not yet implemented in V2. Please implement this feature."
    )


@router.post('/{invoice_id}/transaction/preview')
async def preview_transaction(
    invoice_id: int,
    data: dict = Body(...),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Yevmiye önizleme
    TODO: Implement transaction preview
    """
    raise HTTPException(
        status_code=501,
        detail="Transaction preview not yet implemented in V2. Please implement this feature."
    )


@router.get('/pdf/{invoice_id}')
async def get_pdf(
    invoice_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """E-fatura PDF'ini getir"""
    from app.services.einvoice_pdf_processor import EInvoicePDFProcessor
    
    # EInvoice'ı sorgula (id primary key ile)
    einvoice = db.query(EInvoice).filter(EInvoice.id == invoice_id).first()
    if not einvoice:
        raise HTTPException(status_code=404, detail=f"E-Invoice with id {invoice_id} not found")
    
    # PDF path'i al
    pdf_processor = EInvoicePDFProcessor(db)
    pdf_path = pdf_processor.get_pdf_full_path(einvoice)
    
    if not pdf_path or not pdf_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"PDF file not found for invoice {einvoice.invoice_number}"
        )
    
    # PDF'i döndür
    return FileResponse(
        path=str(pdf_path),
        media_type='application/pdf',
        filename=f"{einvoice.invoice_number}.pdf"
    )


@router.post('/pdf/upload')
async def upload_pdf(
    file: UploadFile = File(...),
    direction: str = Body(...),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """PDF e-fatura yükle ve parse et"""
    from app.services.einvoice_pdf_processor import EInvoicePDFProcessor
    import tempfile
    import os
    
    try:
        # Geçici dosyaya kaydet
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # PDF'i parse et ve kaydet
        pdf_processor = EInvoicePDFProcessor(db)
        einvoice_id = pdf_processor.save_invoice_from_pdf_only(
            pdf_path=tmp_path,
            original_filename=file.filename,
            direction=direction
        )
        
        # Geçici dosyayı sil
        os.unlink(tmp_path)
        
        if einvoice_id:
            return {
                'success': True,
                'einvoice_id': einvoice_id,
                'filename': file.filename
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="PDF could not be processed"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/upload-xml')
async def upload_xml(
    files: List[UploadFile] = File(...),
    direction: str = Body(...),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """XML e-fatura yükle ve parse et"""
    from app.services.einvoice_xml_service import parse_xml_invoice, create_einvoice_from_xml
    
    results = []
    errors_list = []
    
    for file in files:
        try:
            # XML içeriğini oku
            content = await file.read()
            
            # XML'i parse et
            invoice_data, parse_errors = parse_xml_invoice(content, file.filename)
            
            if parse_errors:
                errors_list.extend([f"{file.filename}: {err}" for err in parse_errors])
                continue
            
            # Direction ekle
            invoice_data['direction'] = direction
            
            # Veritabanına kaydet
            einvoice = create_einvoice_from_xml(db, invoice_data)
            db.commit()
            
            results.append({
                'filename': file.filename,
                'invoice_id': einvoice.id,
                'success': True
            })
            
        except Exception as e:
            errors_list.append(f"{file.filename}: {str(e)}")
    
    return {
        'success': len(results),
        'failed': len(errors_list),
        'results': results,
        'errors': errors_list
    }


@router.post('/preview-xml')
async def preview_xml(
    files: List[UploadFile] = File(...),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """XML e-fatura önizleme (kaydetmeden parse et)"""
    from app.services.einvoice_xml_service import parse_xml_invoice
    
    results = []
    
    for file in files:
        try:
            # XML içeriğini oku
            content = await file.read()
            
            # XML'i parse et
            invoice_data, parse_errors = parse_xml_invoice(content, file.filename)
            
            results.append({
                'filename': file.filename,
                'data': invoice_data,
                'errors': parse_errors,
                'success': len(parse_errors) == 0
            })
            
        except Exception as e:
            results.append({
                'filename': file.filename,
                'data': None,
                'errors': [str(e)],
                'success': False
            })
    
    return {'results': results}


# Generic /{invoice_id} routes EN SONDA - spesifik route'lar önce gelmelidir
@router.get('/{invoice_id}', response_model=EInvoiceSchema)
def get_invoice(
    invoice_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ID ile fatura detayı
    """
    invoice = einvoice_service.get_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail='Fatura bulunamadı')
    return invoice


@router.put('/{invoice_id}', response_model=EInvoiceSchema)
@router.patch('/{invoice_id}', response_model=EInvoiceSchema)
def update_invoice(
    invoice_id: int,
    invoice_data: EInvoiceUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fatura güncelle (PUT veya PATCH)
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
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fatura sil
    """
    success = einvoice_service.delete_invoice(db, invoice_id)
    if not success:
        raise HTTPException(status_code=404, detail='Fatura bulunamadı')
    return None
