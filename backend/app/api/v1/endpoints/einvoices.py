from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_, text
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
import pandas as pd
import io
import zipfile
import os

from app.core.database import get_db
from app.core.config import Settings
from app.models.einvoice import EInvoice
from app.models.contact import Contact
from app.schemas.einvoice import (
    EInvoice as EInvoiceSchema,
    EInvoiceCreate,
    EInvoiceUpdate,
    EInvoiceSummary
)
from app.services.einvoice_xml_service import parse_xml_invoice, create_einvoice_from_xml
from app.services.einvoice_preview_service import preview_xml_invoices
from app.services.invoice_mapping_service import create_mapping, get_transaction_for_invoice
from app.services.einvoice_accounting_service import (
    create_or_get_contact,
    create_accounting_transaction,
    create_custom_transaction,
    generate_transaction_preview
)

router = APIRouter(prefix='/einvoices', tags=['E-Fatura'])


@router.get('/summary', response_model=EInvoiceSummary)
def get_einvoices_summary(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    '''E-fatura Ãzet istatistikleri'''
    # Base query with date filters
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
    
    # Kategorilere göre sayılar
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
        'total_count': total_count,
        'total_amount': total_amount,
        'parsed_count': parsed_count,
        'imported_count': imported_count,
        'error_count': error_count,
        'pending_count': pending_count,
        'incoming_count': incoming_count,
        'incoming_amount': incoming_amount,
        'incoming_archive_count': incoming_archive_count,
        'incoming_archive_amount': incoming_archive_amount,
        'outgoing_count': outgoing_count,
        'outgoing_amount': outgoing_amount,
        'outgoing_archive_count': outgoing_archive_count,
        'outgoing_archive_amount': outgoing_archive_amount
    }


@router.get('/', response_model=List[EInvoiceSchema])
def get_einvoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    import_status: Optional[str] = None,
    supplier_tax_number: Optional[str] = None,
    invoice_uuid: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
    invoice_category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    '''E-faturaları listele'''
    query = db.query(EInvoice)
    
    if invoice_uuid:
        query = query.filter(EInvoice.invoice_uuid == invoice_uuid)
    
    if invoice_category:
        query = query.filter(EInvoice.invoice_category == invoice_category)
    
    if status:
        query = query.filter(EInvoice.processing_status == status)
    
    if import_status:
        query = query.filter(EInvoice.processing_status == import_status)
    
    if supplier_tax_number:
        query = query.filter(EInvoice.supplier_tax_number == supplier_tax_number)
    
    if date_from:
        query = query.filter(EInvoice.issue_date >= date_from)
    
    if date_to:
        query = query.filter(EInvoice.issue_date <= date_to)
    
    if search:
        search_filter = or_(
            EInvoice.invoice_number.like(f'%{search}%'),
            EInvoice.supplier_name.like(f'%{search}%'),
            EInvoice.supplier_tax_number.like(f'%{search}%')
        )
        query = query.filter(search_filter)
    
    # signing_time (imza zamanı - gerçek geliş tarihi) varsa ona göre, yoksa issue_date'e göre sırala
    query = query.order_by(
        desc(EInvoice.signing_time),
        desc(EInvoice.issue_date)
    )
    items = query.offset(skip).limit(limit).all()
    
    # Contact IBAN'larını ekle
    from app.models.contact import Contact
    result = []
    for item in items:
        item_dict = {
            **{c.name: getattr(item, c.name) for c in item.__table__.columns},
            'contact_iban': None
        }
        
        # Contact'tan IBAN al
        if item.contact_id:
            contact = db.query(Contact).filter(Contact.id == item.contact_id).first()
            if contact and contact.iban:
                item_dict['contact_iban'] = contact.iban
        
        result.append(item_dict)
    
    return result


@router.get('/{invoice_id}')
def get_einvoice(invoice_id: int, db: Session = Depends(get_db)):
    '''E-fatura detayı'''
    from app.models.invoice_tax import InvoiceTax
    
    einvoice = db.query(EInvoice).filter(EInvoice.id == invoice_id).first()
    
    if not einvoice:
        raise HTTPException(status_code=404, detail='E-fatura bulunamadı')
    
    # === VERGİ DETAYLARINI YUKLE ===
    tax_details = db.query(InvoiceTax).filter(
        InvoiceTax.einvoice_id == einvoice.id
    ).all()
    
    tax_details_list = []
    for tax in tax_details:
        tax_details_list.append({
            'id': tax.id,
            'tax_type_code': tax.tax_type_code,
            'tax_name': tax.tax_name,
            'tax_percent': float(tax.tax_percent) if tax.tax_percent else 0,
            'taxable_amount': float(tax.taxable_amount) if tax.taxable_amount else 0,
            'tax_amount': float(tax.tax_amount) if tax.tax_amount else 0,
            'currency_code': tax.currency_code,
            'exemption_reason_code': tax.exemption_reason_code,
            'exemption_reason': tax.exemption_reason
        })
    
    # raw_data'dan satırları parse et (XML ise)
    invoice_lines = []
    
    # XML namespace ile InvoiceLine kontrolü - hem <InvoiceLine hem cac:InvoiceLine olabilir
    if einvoice.raw_data and ('<InvoiceLine' in einvoice.raw_data or 'cac:InvoiceLine' in einvoice.raw_data):
        import xml.etree.ElementTree as ET
        import html
        print(f"DEBUG: raw_data var, InvoiceLine tagi bulundu")
        try:
            # XML escaped ise unescape et
            xml_data = einvoice.raw_data
            if '&quot;' in xml_data or '&lt;' in xml_data:
                xml_data = html.unescape(xml_data)
                print(f"DEBUG: XML unescaped")
            
            root = ET.fromstring(xml_data)
            print(f"DEBUG: XML parsed, root: {root.tag}")
            # Namespace tanımla
            ns = {
                'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
            }
            
            # InvoiceLine'lari parse et
            lines_found = root.findall('.//cac:InvoiceLine', ns)
            print(f"DEBUG: InvoiceLine bulundu: {len(lines_found)}")
            
            for line in lines_found:
                line_data = {}
                
                # ID
                id_elem = line.find('cbc:ID', ns)
                line_data['id'] = id_elem.text if id_elem is not None else None
                
                # Miktar
                qty_elem = line.find('cbc:InvoicedQuantity', ns)
                if qty_elem is not None:
                    line_data['quantity'] = float(qty_elem.text) if qty_elem.text else 0
                    line_data['unit'] = qty_elem.get('unitCode', '')
                
                # Ürün adı
                item_elem = line.find('.//cac:Item/cbc:Name', ns)
                line_data['item_name'] = item_elem.text if item_elem is not None else None
                
                # Birim fiyat
                price_elem = line.find('.//cac:Price/cbc:PriceAmount', ns)
                if price_elem is not None:
                    line_data['unit_price'] = float(price_elem.text) if price_elem.text else 0
                    line_data['currency'] = price_elem.get('currencyID', 'TRY')
                
                # Satır toplamı
                total_elem = line.find('cbc:LineExtensionAmount', ns)
                if total_elem is not None:
                    line_data['line_total'] = float(total_elem.text) if total_elem.text else 0
                
                # KDV
                tax_total = line.find('.//cac:TaxTotal/cbc:TaxAmount', ns)
                if tax_total is not None:
                    line_data['tax_amount'] = float(tax_total.text) if tax_total.text else 0
                
                # KDV oranı (TaxSubtotal'ın direkt çocuğu)
                tax_percent = line.find('.//cac:TaxSubtotal/cbc:Percent', ns)
                if tax_percent is not None:
                    line_data['tax_percent'] = float(tax_percent.text) if tax_percent.text else 0
                
                invoice_lines.append(line_data)
            
            print(f"DEBUG: Toplam {len(invoice_lines)} satir parse edildi")
            
        except Exception as e:
            print(f"ERROR: XML parse hatasi: {e}")
            import traceback
            traceback.print_exc()
    else:
        if not einvoice.raw_data:
            print(f"DEBUG: raw_data YOK!")
        elif '<InvoiceLine' not in einvoice.raw_data and 'cac:InvoiceLine' not in einvoice.raw_data:
            print(f"DEBUG: raw_data var ama InvoiceLine tagi YOK!")
    
    # Response'a satırları ve vergi detaylarını ekle
    response_data = {
        **{c.name: getattr(einvoice, c.name) for c in einvoice.__table__.columns},
        'invoice_lines': invoice_lines,
        'tax_details': tax_details_list
    }
    
    # Contact IBAN ekle
    if einvoice.contact_id:
        from app.models.contact import Contact
        contact = db.query(Contact).filter(Contact.id == einvoice.contact_id).first()
        if contact and contact.iban:
            response_data['contact_iban'] = contact.iban
    
    return response_data


@router.post('/', response_model=EInvoiceSchema)
def create_einvoice(einvoice_data: EInvoiceCreate, db: Session = Depends(get_db)):
    '''Yeni e-fatura ekle'''
    existing = db.query(EInvoice).filter(
        or_(
            EInvoice.invoice_number == einvoice_data.invoice_number,
            EInvoice.invoice_ettn == einvoice_data.invoice_ettn
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail='Bu fatura zaten mevcut')
    
    einvoice = EInvoice(**einvoice_data.dict())
    db.add(einvoice)
    db.commit()
    db.refresh(einvoice)
    
    return einvoice


@router.patch('/{invoice_id}', response_model=EInvoiceSchema)
def update_einvoice(
    invoice_id: int,
    einvoice_data: EInvoiceUpdate,
    db: Session = Depends(get_db)
):
    '''E-fatura güncelle'''
    einvoice = db.query(EInvoice).filter(EInvoice.id == invoice_id).first()
    
    if not einvoice:
        raise HTTPException(status_code=404, detail='E-fatura bulunamadı')
    
    for key, value in einvoice_data.dict(exclude_unset=True).items():
        setattr(einvoice, key, value)
    
    db.commit()
    db.refresh(einvoice)
    
    return einvoice


@router.delete('/{invoice_id}')
def delete_einvoice(invoice_id: int, db: Session = Depends(get_db)):
    '''E-fatura sil'''
    einvoice = db.query(EInvoice).filter(EInvoice.id == invoice_id).first()
    
    if not einvoice:
        raise HTTPException(status_code=404, detail='E-fatura bulunamadı')
    
    db.delete(einvoice)
    db.commit()
    
    return {'message': 'E-fatura silindi'}


@router.get('/pdf/{invoice_id}')
def get_einvoice_pdf(invoice_id: int, db: Session = Depends(get_db)):
    '''E-fatura PDF dosyasını döndür'''
    einvoice = db.query(EInvoice).filter(EInvoice.id == invoice_id).first()
    
    if not einvoice:
        raise HTTPException(status_code=404, detail='E-fatura bulunamadı')
    
    if not einvoice.pdf_path:
        raise HTTPException(status_code=404, detail='Bu faturanın PDF dosyası yok')
    
    # Backend dizini - __file__'dan 5 seviye yukarı
    # einvoices.py -> endpoints -> v1 -> api -> app -> backend
    current_file = os.path.abspath(__file__)
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file)))))
    
    # PDF path'i tam yol mu kontrol et
    if os.path.isabs(einvoice.pdf_path):
        pdf_full_path = einvoice.pdf_path
    else:
        # Relative path - backend/data/ ile birleştir
        pdf_full_path = os.path.join(backend_dir, 'data', einvoice.pdf_path)
    
    if not os.path.exists(pdf_full_path):
        raise HTTPException(status_code=404, detail=f'PDF dosyası bulunamadı: {pdf_full_path}')
    
    return FileResponse(
        path=pdf_full_path,
        media_type='application/pdf',
        filename=f"{einvoice.invoice_number}.pdf"
    )


@router.get('/suppliers/list')
def get_suppliers(db: Session = Depends(get_db)):
    '''Tedarikçi listesi'''
    suppliers = db.query(
        EInvoice.supplier_name,
        EInvoice.supplier_tax_number,
        func.count(EInvoice.id).label('invoice_count'),
        func.sum(EInvoice.payable_amount).label('total_amount')
    ).group_by(
        EInvoice.supplier_name,
        EInvoice.supplier_tax_number
    ).order_by(
        desc('invoice_count')
    ).all()
    
    return [
        {
            'supplier_name': s.supplier_name,
            'supplier_tax_number': s.supplier_tax_number,
            'invoice_count': s.invoice_count,
            'total_amount': float(s.total_amount) if s.total_amount else 0
        }
        for s in suppliers
    ]


@router.post('/{invoice_id}/import-preview')
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
            {
                "invoice_lines_mapping": [
                    {
                        "line_id": "1",
                        "account_code": "740.00204",
                        "category": "elektrik",
                        "item_name": "..."
                    }
                ]
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
    
    # Service'den önizleme al (kategori mapping'i ve cost_center ile)
    return generate_transaction_preview(db, einvoice, category_data, cost_center_id)


@router.post('/{invoice_id}/import')
def import_einvoice_to_accounting(
    invoice_id: int, 
    transaction_data: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    '''
    E-faturayı muhasebe kaydına dönüştür
    
    Args:
        invoice_id: E-fatura ID
        transaction_data: Opsiyonel - Kullanıcının düzenlediği fiş bilgileri
            {
                "invoice_type": "Satış",  # Fatura türü
                "transaction_number": "F00000123",  # Düzenlenebilir
                "lines": [...],  # Düzenlenebilir satırlar
                "invoice_lines_mapping": [  # Fatura satırları kategorizasyonu
                    {
                        "line_id": "1",
                        "category": "hizmet_maliyet",
                        "account_code": "740.01.001",
                        "fixed_asset_category": null,
                        "item_name": "...",
                        "line_total": 1000
                    }
                ]
            }
    '''
    einvoice = db.query(EInvoice).filter(EInvoice.id == invoice_id).first()
    
    if not einvoice:
        raise HTTPException(status_code=404, detail='E-fatura bulunamadı')
    
    # Eğer zaten transaction oluşturulmuşsa, önce onu sil
    if einvoice.transaction_id:
        from app.models.transaction import Transaction
        from app.models.transaction_line import TransactionLine
        
        old_transaction = db.query(Transaction).filter(Transaction.id == einvoice.transaction_id).first()
        if old_transaction:
            # Transaction lines'ı sil
            db.query(TransactionLine).filter(TransactionLine.transaction_id == old_transaction.id).delete()
            # Mapping'i sil
            db.execute(text("DELETE FROM invoice_transaction_mappings WHERE transaction_id = :tid"), {'tid': old_transaction.id})
            # Transaction'ı sil
            db.delete(old_transaction)
            db.commit()
        
        # E-fatura kaydını resetle
        einvoice.transaction_id = None
        einvoice.processing_status = 'PENDING'
        db.commit()
    
    if einvoice.processing_status == 'COMPLETED':
        raise HTTPException(status_code=400, detail='Bu fatura zaten import edilmiş')
    
    try:
        # 1. Cari oluştur/getir
        contact = create_or_get_contact(db, einvoice)
        
        # 2. Demirbaş/Taşıt için hesap planı kayıtları oluştur (varsa)
        if transaction_data and transaction_data.get('invoice_lines_mapping'):
            for line_mapping in transaction_data['invoice_lines_mapping']:
                category = line_mapping.get('category')
                
                # Demirbaş alımı
                if category == 'demirbaş':
                    fixed_asset_cat = line_mapping.get('fixed_asset_category')
                    item_name = line_mapping.get('item_name', 'Demirbaş')
                    
                    if fixed_asset_cat:
                        # Yeni hesap oluştur ve kodu al
                        new_account_code = generate_fixed_asset_account(db, fixed_asset_cat, item_name)
                        # Mapping'e ekle (frontend'e göndermek için)
                        line_mapping['generated_account_code'] = new_account_code
                
                # Taşıt alımı
                elif category == 'taşıt':
                    item_name = line_mapping.get('item_name', 'Taşıt')
                    # Taşıt için özel kategori
                    new_account_code = generate_fixed_asset_account(db, 'Taşıt', item_name)
                    line_mapping['generated_account_code'] = new_account_code
        
        # 3. Muhasebe fişi oluştur
        if transaction_data and transaction_data.get('lines'):
            # Kullanıcı düzenlemişse, düzenlenmiş veriyi kullan
            transaction = create_custom_transaction(db, einvoice, contact, transaction_data)
        else:
            # Otomatik oluştur
            try:
                transaction = create_accounting_transaction(db, einvoice, contact)
            except Exception as create_err:
                # Duplicate transaction_number hatası olabilir
                if 'Duplicate entry' in str(create_err) or 'duplicate key' in str(create_err).lower():
                    # Fiş numarasını al ve eski transaction'ı sil
                    from app.models.transaction import Transaction
                    from app.models.transaction_line import TransactionLine
                    from app.utils.transaction_numbering import get_next_transaction_number
                    
                    # Bir sonraki fiş numarasını hesapla (duplicate olan numara)
                    duplicate_number = get_next_transaction_number(db, prefix="F")
                    
                    # Eski transaction'ı bul ve sil
                    old_transaction = db.query(Transaction).filter(
                        Transaction.transaction_number == duplicate_number
                    ).first()
                    
                    if old_transaction:
                        # Transaction lines ve mapping'i sil
                        db.query(TransactionLine).filter(
                            TransactionLine.transaction_id == old_transaction.id
                        ).delete()
                        db.execute(text(
                            "DELETE FROM invoice_transaction_mappings WHERE transaction_id = :tid"
                        ), {'tid': old_transaction.id})
                        db.delete(old_transaction)
                        db.commit()
                        
                        # Tekrar dene
                        transaction = create_accounting_transaction(db, einvoice, contact)
                    else:
                        raise create_err
                else:
                    raise create_err
        
        # 4. Junction table'a mapping ekle
        create_mapping(
            db=db,
            einvoice_id=einvoice.id,
            transaction_id=transaction.id,
            mapping_type='manual',  # Manuel import
            confidence_score=1.00
        )
        
        # 5. E-fatura kaydını güncelle
        einvoice.contact_id = contact.id
        einvoice.transaction_id = transaction.id
        einvoice.processing_status = 'COMPLETED'
        einvoice.error_message = None
        
        db.commit()
        db.refresh(einvoice)
        
        return {
            'message': 'E-fatura başarıyla import edildi',
            'contact_id': contact.id,
            'transaction_id': transaction.id,
            'transaction_number': transaction.transaction_number,
            'invoice_type': transaction_data.get('invoice_type') if transaction_data else 'Satış'
        }
        
    except Exception as e:
        db.rollback()
        einvoice.processing_status = 'ERROR'
        einvoice.error_message = str(e)
        db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f'Import hatası: {str(e)}'
        )


@router.post('/upload')
async def upload_einvoices_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    '''Excel/CSV dosyasından e-faturaları yükle'''
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(
            status_code=400,
            detail='Sadece Excel (.xlsx, .xls) veya CSV dosyaları destekleniyor'
        )
    
    try:
        contents = await file.read()
        
        # Excel dosyasını oku
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # Sütun isimlerini normalize et (Türkçe karakterler dahil)
        def normalize_column_name(col):
            # Önce strip ve upper
            col = str(col).strip().upper()
            # Türkçe karakterleri düzelt (Excel bazen i̇ olarak yazar)
            col = col.replace('İ', 'I')  # İ → I
            col = col.replace('Ş', 'S')  # Ş → S
            col = col.replace('Ğ', 'G')  # Ğ → G
            col = col.replace('Ü', 'U')  # Ü → U
            col = col.replace('Ö', 'O')  # Ö → O
            col = col.replace('Ç', 'C')  # Ç → C
            col = col.replace('ı', 'I')  # ı → I
            col = col.replace('i̇', 'I')  # i̇ → I (Excel'deki noktalı i)
            # Boşlukları alt çizgiye çevir
            col = col.replace(' ', '_')
            # Özel karakterleri temizle
            col = col.replace('/', '_')
            col = col.replace('.', '')
            col = col.replace('-', '_')
            return col
        
        df.columns = [normalize_column_name(col) for col in df.columns]
        
        # Sütun eşleştirmesi için mapping (Zirve GELEN fatura - büyük harf)
        # GELEN FATURA: ALICI = Biz, GÖNDERİCİ = Tedarikçi
        column_mapping = {
            'fatura_no': ['FATURA_NO', 'FATURANO', 'FATURA_NUMARASI', 'BELGE_NO', 'BELGENO', 'INVOICE_NUMBER', 'NO'],
            'fatura_tarihi': ['FATURA_TARIHI', 'FATURATARIHI', 'TARIH', 'BELGE_TARIHI', 'DATE', 'INVOICE_DATE'],
            # Tedarikçi = GÖNDERİCİ (gelen faturada)
            'tedarikci_adi': ['GONDERICI_UNVANI', 'TEDARIKCI_ADI', 'TEDARIKCIADI', 'SATICI_ADI', 'SATICIADI', 'SATICI', 'TEDARIKCI', 'SUPPLIER_NAME', 'SUPPLIER'],
            'vergi_no': ['GONDERICI_VKN_TCKN', 'GONDERICI_VKN', 'VERGI_NO', 'VERGINO', 'VKN', 'TCKN', 'TAX_NUMBER', 'VERGI_KIMLIK_NO'],
            'tutar': ['TUTAR', 'TOPLAM', 'TOPLAM_TUTAR', 'ODENECEK', 'ODENECEK_TUTAR', 'TOTAL', 'AMOUNT', 'PAYABLE_AMOUNT', 'MAL_HIZMET_TOPLAM_TUTARI'],
            'kdv_tutar': ['KDV_TUTAR', 'KDV', 'KDVTUTAR', 'VAT', 'VAT_AMOUNT', 'TOPLAM_KDV_TUTAR'],
            'matrah': ['MATRAH', 'KDV_MATRAH', 'KDVMATRAH', 'VAT_BASE', 'MAL_HIZMET_TOPLAM_TUTARI'],
            'ettn': ['ETTN', 'UUID', 'FATURA_ETTN', 'ZARF_ETTN'],
            'vergi_dairesi': ['GONDERICI_VERGI_DAIRESI', 'VERGI_DAIRESI', 'VERGIDAIRESI', 'TAX_OFFICE'],
            'para_birimi': ['PARA_BIRIMI', 'PARABIRIMI', 'CURRENCY', 'DOVIZ', 'DOVIZ_TIPI'],
            'kdv_0_matrah': ['TOPLAM_KDV_%0_MATRAH', 'TOPLAM_KDV_0_MATRAH', 'KDV_0_MATRAH'],
            'kdv_0_tutar': ['TOPLAM_KDV_%0_TUTAR', 'TOPLAM_KDV_0_TUTAR', 'KDV_0_TUTAR'],
            'kdv_1_matrah': ['TOPLAM_KDV_%1_MATRAH', 'TOPLAM_KDV_1_MATRAH', 'KDV_1_MATRAH'],
            'kdv_1_tutar': ['TOPLAM_KDV_%1_TUTAR', 'TOPLAM_KDV_1_TUTAR', 'KDV_1_TUTAR'],
            'kdv_8_matrah': ['TOPLAM_KDV_%8_MATRAH', 'TOPLAM_KDV_8_MATRAH', 'KDV_8_MATRAH'],
            'kdv_8_tutar': ['TOPLAM_KDV_%8_TUTAR', 'TOPLAM_KDV_8_TUTAR', 'KDV_8_TUTAR'],
            'kdv_10_matrah': ['TOPLAM_KDV_%10_MATRAH', 'TOPLAM_KDV_10_MATRAH', 'KDV_10_MATRAH'],
            'kdv_10_tutar': ['TOPLAM_KDV_%10_TUTAR', 'TOPLAM_KDV_10_TUTAR', 'KDV_10_TUTAR'],
            'kdv_18_matrah': ['TOPLAM_KDV_%18_MATRAH', 'TOPLAM_KDV_18_MATRAH', 'KDV_18_MATRAH'],
            'kdv_18_tutar': ['TOPLAM_KDV_%18_TUTAR', 'TOPLAM_KDV_18_TUTAR', 'KDV_18_TUTAR'],
            'kdv_20_matrah': ['TOPLAM_KDV_%20_MATRAH', 'TOPLAM_KDV_20_MATRAH', 'KDV_20_MATRAH'],
            'kdv_20_tutar': ['TOPLAM_KDV_%20_TUTAR', 'TOPLAM_KDV_20_TUTAR', 'KDV_20_TUTAR'],
            # Ek bilgiler (Zirve) - ADRES/IL/ILCE = ALICI (bize ait), kullanmayacağız
            # GÖNDERİCİ için ayrı adres sütunu yok, sadece NOTLAR'da olabilir
            'telefon': ['TELEFON', 'PHONE', 'TEL'],
            'email': ['E_MAIL', 'EMAIL', 'E_POSTA', 'EPOSTA'],
            'tevkifat_toplami': ['TEVKIFAT_TOPLAMI', 'TEVKIFAT'],
            'kdv_tevkifati_tutari': ['KDV_TEVKIFATI_TUTARI', 'KDV_TEVKIFAT'],
            'kdv_tevkifati_orani': ['KDV_TEVKIFATI_ORANI', 'KDV_TEVKIFAT_ORANI'],
            'iskonto': ['TOPLAM_ISKONTO', 'ISKONTO', 'DISCOUNT'],
            'notlar': ['NOTLAR', 'ACIKLAMA', 'NOTES', 'DESCRIPTION'],
            'doviz_kuru': ['DOVIZ_KURU', 'KUR', 'EXCHANGE_RATE'],
            'senaryo': ['SENARYO', 'FATURA_SENARYOSU', 'SCENARIO'],
            'tip': ['FATURA_TIPI', 'FATURA_TURU', 'TIP', 'TYPE', 'INVOICE_TYPE']
        }
        
        # Sütunları eşleştir
        def find_column(col_name):
            for col in df.columns:
                if col in column_mapping.get(col_name, []):
                    return col
            return None
        
        # Gerekli sütunları bul
        col_invoice_no = find_column('fatura_no')
        col_invoice_date = find_column('fatura_tarihi')
        col_supplier_name = find_column('tedarikci_adi')
        col_tax_no = find_column('vergi_no')
        col_amount = find_column('tutar')
        col_vat = find_column('kdv_tutar')
        col_vat_base = find_column('matrah')
        col_ettn = find_column('ettn')
        col_tax_office = find_column('vergi_dairesi')
        col_currency = find_column('para_birimi')
        col_scenario = find_column('senaryo')
        col_type = find_column('tip')
        
        # NOT: ADRES/IL/ILCE sütunları ALICI'ya (bize) ait, tedarikçiye atamayacağız
        
        # KDV oranlarına göre sütunlar (Zirve formatı)
        col_kdv_0_matrah = find_column('kdv_0_matrah')
        col_kdv_0_tutar = find_column('kdv_0_tutar')
        col_kdv_1_matrah = find_column('kdv_1_matrah')
        col_kdv_1_tutar = find_column('kdv_1_tutar')
        col_kdv_8_matrah = find_column('kdv_8_matrah')
        col_kdv_8_tutar = find_column('kdv_8_tutar')
        col_kdv_10_matrah = find_column('kdv_10_matrah')
        col_kdv_10_tutar = find_column('kdv_10_tutar')
        col_kdv_18_matrah = find_column('kdv_18_matrah')
        col_kdv_18_tutar = find_column('kdv_18_tutar')
        col_kdv_20_matrah = find_column('kdv_20_matrah')
        col_kdv_20_tutar = find_column('kdv_20_tutar')
        
        # Ek bilgiler (Zirve)
        col_telefon = find_column('telefon')
        col_email = find_column('email')
        col_tevkifat = find_column('tevkifat_toplami')
        col_kdv_tevkifat = find_column('kdv_tevkifati_tutari')
        col_kdv_tevkifat_oran = find_column('kdv_tevkifati_orani')
        col_iskonto = find_column('iskonto')
        col_notlar = find_column('notlar')
        col_doviz_kuru = find_column('doviz_kuru')
        
        if not col_invoice_no or not col_invoice_date:
            # İlk 20 sütunu göster (çok uzun olmasın)
            sample_cols = df.columns.tolist()[:20]
            raise HTTPException(
                status_code=400,
                detail=f'Gerekli sütunlar bulunamadı. Lütfen Zirve Excel formatında bir dosya yükleyin. Aranan: FATURA_NUMARASI, FATURA_TARIHI. İlk 20 sütun: {", ".join(sample_cols)}'
            )
        
        imported_count = 0
        error_count = 0
        errors = []
        contacts_created = 0
        contacts_updated = 0
        
        # VKN cache - Her VKN için sadece 1 kere sorgu
        contact_cache = {}
        
        # Önce tüm unique VKN'leri topla ve tek sorguda getir
        all_vkns = set()
        for _, invoice_rows in df.groupby(col_invoice_no):
            row = invoice_rows.iloc[0]
            supplier_tax_number = clean_tax_number(row.get(col_tax_no)) if col_tax_no else None
            if supplier_tax_number:
                all_vkns.add(supplier_tax_number)
        
        # Tüm mevcut carileri tek sorguda getir
        if all_vkns:
            existing_contacts = db.query(Contact).filter(
                Contact.tax_number.in_(list(all_vkns))
            ).all()
            for contact in existing_contacts:
                contact_cache[contact.tax_number] = contact
        
        # Her fatura için satırları grupla
        total_rows = len(df)
        invoice_groups = df.groupby(col_invoice_no)
        unique_count = len(invoice_groups)
        
        print(f"📊 Toplam {total_rows} satır, {unique_count} unique fatura")
        
        for invoice_number, invoice_rows in invoice_groups:
            try:
                # İlk satırdan fatura bilgilerini al
                row = invoice_rows.iloc[0]
                
                # Zorunlu alanları kontrol et
                if pd.isna(row.get(col_invoice_no)) or pd.isna(row.get(col_invoice_date)):
                    error_count += 1
                    errors.append(f'Fatura {invoice_number}: No veya tarihi eksik')
                    continue
                
                # Tarih parse
                invoice_date = pd.to_datetime(row.get(col_invoice_date))
                
                # Tutar parse - Excel'de sütun varsa onu kullan (0 dahil), yoksa None
                payable_amount = None
                if col_amount and pd.notna(row.get(col_amount)):
                    payable_amount = float(str(row.get(col_amount)).replace(',', '.').replace(' ', ''))
                
                # Tedarikçi adı
                supplier_name = 'Bilinmiyor'
                if col_supplier_name and pd.notna(row.get(col_supplier_name)):
                    supplier_name = clean_company_name(str(row.get(col_supplier_name)))
                
                # VKN - Temizle
                supplier_tax_number = None
                if col_tax_no and pd.notna(row.get(col_tax_no)):
                    supplier_tax_number = clean_tax_number(str(row.get(col_tax_no)))
                
                # Adres bilgileri - GÖNDERİCİ için Excel'de ayrı sütun yok
                # ADRES/IL/ILCE sütunları ALICI'ya (bize) ait, tedarikçiye atamıyoruz
                supplier_address = None
                supplier_city = None
                supplier_district = None
                supplier_tax_office = str(row.get(col_tax_office)).strip().title() if col_tax_office and pd.notna(row.get(col_tax_office)) else None
                
                # İletişim bilgileri
                phone_raw = str(row.get(col_telefon)) if col_telefon and pd.notna(row.get(col_telefon)) else None
                email_raw = str(row.get(col_email)) if col_email and pd.notna(row.get(col_email)) else None
                
                # NOTLAR sütunu - IBAN çıkarmak için
                notlar_raw = str(row.get(col_notlar)) if col_notlar and pd.notna(row.get(col_notlar)) else None
                
                # Mevcut faturayı kontrol et
                existing = db.query(EInvoice).filter(
                    EInvoice.invoice_number == str(row.get(col_invoice_no))
                ).first()
                
                if existing:
                    continue  # Zaten var, atla
                
                # KDV tutarları (Zirve formatında oran bazlı)
                def get_decimal_value(col, row):
                    if col and pd.notna(row.get(col)):
                        val = str(row.get(col)).replace(',', '.').replace(' ', '')
                        try:
                            return Decimal(val) if val else Decimal('0')
                        except:
                            return Decimal('0')
                    return Decimal('0')
                
                # Her KDV oranı için matrah ve tutar
                kdv_0_base = get_decimal_value(col_kdv_0_matrah, row)
                kdv_0_amount = get_decimal_value(col_kdv_0_tutar, row)
                kdv_1_base = get_decimal_value(col_kdv_1_matrah, row)
                kdv_1_amount = get_decimal_value(col_kdv_1_tutar, row)
                kdv_8_base = get_decimal_value(col_kdv_8_matrah, row)
                kdv_8_amount = get_decimal_value(col_kdv_8_tutar, row)
                kdv_10_base = get_decimal_value(col_kdv_10_matrah, row)
                kdv_10_amount = get_decimal_value(col_kdv_10_tutar, row)
                kdv_18_base = get_decimal_value(col_kdv_18_matrah, row)
                kdv_18_amount = get_decimal_value(col_kdv_18_tutar, row)
                kdv_20_base = get_decimal_value(col_kdv_20_matrah, row)
                kdv_20_amount = get_decimal_value(col_kdv_20_tutar, row)
                
                # Toplam matrah (MAL HİZMET TOPLAM TUTARI)
                total_base = kdv_0_base + kdv_1_base + kdv_8_base + kdv_10_base + kdv_18_base + kdv_20_base
                
                # İskonto
                total_discount = get_decimal_value(col_iskonto, row)
                
                # Tevkifat
                withholding_total = get_decimal_value(col_tevkifat, row)
                
                # Döviz kuru
                exchange_rate = get_decimal_value(col_doviz_kuru, row)
                if exchange_rate == 0:
                    exchange_rate = Decimal('1')
                
                # Eğer matrahlar boşsa, eski yöntemle doldur
                if total_base == 0:
                    if col_vat_base and pd.notna(row.get(col_vat_base)):
                        total_base = get_decimal_value(col_vat_base, row)
                        kdv_18_base = total_base  # Varsayılan olarak %18'e ata
                    
                    if col_vat and pd.notna(row.get(col_vat)):
                        kdv_18_amount = get_decimal_value(col_vat, row)
                
                # Adres bilgileri (Cari için)
                # NOT: GÖNDERİCİ için Excel'de ayrı adres sütunu yok
                # ADRES/IL/ILCE sütunları ALICI'ya ait, kullanmıyoruz
                supplier_address = None
                supplier_city = None
                supplier_district = None
                
                # İletişim bilgileri (Cari için - notlarda saklanacak)
                contact_info = []
                if col_telefon and pd.notna(row.get(col_telefon)):
                    contact_info.append(f"Tel: {row.get(col_telefon)}")
                if col_email and pd.notna(row.get(col_email)):
                    contact_info.append(f"E-mail: {row.get(col_email)}")
                
                # Notlar
                notes = []
                if col_notlar and pd.notna(row.get(col_notlar)):
                    notes.append(str(row.get(col_notlar)))
                if contact_info:
                    notes.extend(contact_info)
                
                # KDV Tevkifatı bilgisi
                if col_kdv_tevkifat and pd.notna(row.get(col_kdv_tevkifat)):
                    kdv_tevk = get_decimal_value(col_kdv_tevkifat, row)
                    if kdv_tevk > 0:
                        kdv_tevk_oran = ""
                        if col_kdv_tevkifat_oran and pd.notna(row.get(col_kdv_tevkifat_oran)):
                            kdv_tevk_oran = f" (%{row.get(col_kdv_tevkifat_oran)})"
                        notes.append(f"KDV Tevkifatı: {kdv_tevk}{kdv_tevk_oran}")
                
                notes_text = " | ".join(notes) if notes else None
                
                # Tüm satır verisini JSON olarak sakla (ilk satırdan)
                raw_row_data = {}
                for col in df.columns:
                    val = row.get(col)
                    if pd.notna(val):
                        # Pandas tiplerini Python tiplerine çevir
                        if isinstance(val, (pd.Timestamp, pd._libs.tslibs.timestamps.Timestamp)):
                            raw_row_data[col] = val.isoformat()
                        elif isinstance(val, (int, float, str, bool)):
                            raw_row_data[col] = val
                        else:
                            raw_row_data[col] = str(val)
                
                # TÜM satırları (kalemleri) array olarak ekle
                lines_data = []
                for idx, line_row in invoice_rows.iterrows():
                    line_dict = {}
                    for col in df.columns:
                        val = line_row.get(col)
                        if pd.notna(val):
                            if isinstance(val, (pd.Timestamp, pd._libs.tslibs.timestamps.Timestamp)):
                                line_dict[col] = val.isoformat()
                            elif isinstance(val, (int, float, str, bool)):
                                line_dict[col] = val
                            else:
                                line_dict[col] = str(val)
                    lines_data.append(line_dict)
                
                raw_row_data['lines'] = lines_data  # Tüm kalemleri ekle
                
                # Yeni e-fatura oluştur
                einvoice = EInvoice(
                    invoice_number=str(row.get(col_invoice_no)),
                    invoice_date=invoice_date.date(),
                    invoice_uuid=str(row.get(col_ettn)) if col_ettn and pd.notna(row.get(col_ettn)) else f'EXCEL-{str(row.get(col_invoice_no))}',  # ETTN yoksa unique ID oluştur
                    invoice_profile=str(row.get(col_scenario)) if col_scenario and pd.notna(row.get(col_scenario)) else None,
                    invoice_type=str(row.get(col_type)) if col_type and pd.notna(row.get(col_type)) else None,
                    supplier_name=supplier_name,
                    supplier_tax_number=supplier_tax_number,
                    supplier_tax_office=supplier_tax_office,
                    supplier_address=supplier_address,
                    supplier_city=supplier_city,
                    supplier_district=supplier_district,
                    currency_code=str(row.get(col_currency)) if col_currency and pd.notna(row.get(col_currency)) else 'TRY',
                    exchange_rate=exchange_rate if exchange_rate > 1 else None,
                    line_extension_amount=total_base,
                    allowance_total=total_discount if total_discount > 0 else None,
                    payable_amount=Decimal(str(payable_amount)) if payable_amount is not None else None,
                    withholding_tax_amount=withholding_total if withholding_total > 0 else None,
                    total_tax_amount=kdv_0_amount + kdv_1_amount + kdv_8_amount + kdv_10_amount + kdv_18_amount + kdv_20_amount,
                    processing_status='PARSED',
                    source='excel',
                    has_xml=0,
                    raw_data=raw_row_data  # Tüm Zirve verisi JSON olarak (KDV detayları dahil)
                )
                
                # Cari oluştur/getir (IBAN otomatik çıkarılacak) - CACHE KULLAN
                contact = None
                if supplier_tax_number:
                    # Cache'den kontrol et
                    existing_contact = contact_cache.get(supplier_tax_number)
                    
                    # Cari oluştur/güncelle
                    contact = create_or_get_contact(
                        db, 
                        einvoice,
                        notes_text=notlar_raw,  # NOTLAR sütunu - IBAN çıkarılacak
                        phone=phone_raw,
                        email=email_raw
                    )
                    
                    # İstatistik tut
                    if existing_contact:
                        contacts_updated += 1
                    else:
                        contacts_created += 1
                    
                    # Cache'e ekle
                    contact_cache[supplier_tax_number] = contact
                    
                    # E-faturaya cari ID'sini ekle
                    einvoice.contact_id = contact.id
                
                db.add(einvoice)
                imported_count += 1
                
                # Her 100 faturada bir commit (hızlandırma)
                if imported_count % 100 == 0:
                    db.commit()
                    print(f"✅ {imported_count}/{unique_count} fatura işlendi")
                
            except Exception as e:
                error_count += 1
                errors.append(f'Fatura {invoice_number}: {str(e)}')
        
        # Son commit
        db.commit()
        
        return {
            'message': f'{imported_count} e-fatura başarıyla yüklendi',
            'imported_count': imported_count,
            'error_count': error_count,
            'contacts_created': contacts_created,
            'contacts_updated': contacts_updated,
            'errors': errors[:10]  # İlk 10 hatayı göster
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Dosya işleme hatası: {str(e)}'
        )


@router.post('/upload-xml-preview')
async def upload_xml_preview(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    XML faturalarını yüklemeden önce analiz et (Preview/Doğrulama)
    
    - Hiçbir şey kaydetmez, sadece analiz yapar
    - VKN eşleşme kontrolü
    - Yeni cari tespiti
    - Benzer isimli cari önerileri
    - Başarı oranı tahmini
    
    Returns:
        {
            'total_files': 50,
            'summary': {
                'matched_contacts': 45,      // VKN ile eşleşti
                'new_contacts': 3,            // Yeni cari eklenecek
                'missing_vkn': 2,             // VKN yok
                'possible_matches': 2         // Benzer isimli var
            },
            'details': [...],
            'success_estimate': '90%'
        }
    """
    xml_files = []
    errors = []
    
    try:
        # Dosyaları topla (ZIP'ten çıkar vs)
        for file in files:
            content = await file.read()
            
            if file.filename.lower().endswith('.zip'):
                try:
                    with zipfile.ZipFile(io.BytesIO(content)) as zf:
                        for zip_info in zf.namelist():
                            if zip_info.lower().endswith('.xml'):
                                xml_content = zf.read(zip_info)
                                xml_files.append((zip_info, xml_content))
                except zipfile.BadZipFile:
                    errors.append(f'{file.filename}: Geçersiz ZIP dosyası')
            
            elif file.filename.lower().endswith('.xml'):
                xml_files.append((file.filename, content))
            
            else:
                errors.append(f'{file.filename}: Desteklenmeyen dosya tipi')
        
        # XML'leri parse et
        invoices_data = []
        
        for filename, xml_content in xml_files:
            try:
                invoice_data, parse_errors = parse_xml_invoice(xml_content, filename)
                
                if parse_errors:
                    errors.extend([f'{filename}: {err}' for err in parse_errors])
                    continue
                
                if invoice_data:
                    # CATEGORY DETECTION (gelen/giden + e-fatura/e-arşiv)
                    # .env'den şirket VKN'si
                    from app.core.config import settings
                    company_vkn = getattr(settings, 'COMPANY_TAX_NUMBER', None)
                    company_vkn_clean = company_vkn.replace('.', '').replace(' ', '').strip() if company_vkn else None
                    
                    supplier_vkn = invoice_data.get('supplier_tax_number')
                    customer_vkn = invoice_data.get('customer_tax_number')
                    
                    detected_direction = None
                    
                    # VKN karşılaştır
                    if customer_vkn and company_vkn_clean:
                        try:
                            if int(customer_vkn) == int(company_vkn_clean):
                                detected_direction = 'incoming'  # Biz alıcıyız → GELEN
                        except:
                            if customer_vkn == company_vkn_clean:
                                detected_direction = 'incoming'
                    
                    if supplier_vkn and company_vkn_clean and not detected_direction:
                        try:
                            if int(supplier_vkn) == int(company_vkn_clean):
                                detected_direction = 'outgoing'  # Biz satıcıyız → GİDEN
                        except:
                            if supplier_vkn == company_vkn_clean:
                                detected_direction = 'outgoing'
                    
                    # Tespit edilmediyse varsayılan incoming
                    final_direction = detected_direction if detected_direction else 'incoming'
                    
                    # Kategori tespiti (invoice_profile ile)
                    profile = invoice_data.get('invoice_scenario', '').upper()
                    is_archive = 'EARSIV' in profile or 'ARSIV' in profile
                    
                    if is_archive:
                        category = f'{final_direction}-archive'
                    else:
                        category = final_direction
                    
                    invoice_data['invoice_category'] = category
                    
                    invoices_data.append(invoice_data)
                else:
                    errors.append(f'{filename}: Parse edilemedi')
                    
            except Exception as e:
                errors.append(f'{filename}: {str(e)}')
        
        # Preview analizi
        preview_result = preview_xml_invoices(db, invoices_data)
        
        # Hataları ekle
        if errors:
            preview_result['parse_errors'] = errors[:20]
            preview_result['parse_error_count'] = len(errors)
        
        return preview_result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Preview hatası: {str(e)}'
        )


@router.post('/upload-xml')
async def upload_xml_invoices(
    files: List[UploadFile] = File(...),
    direction: str = Form('incoming'),  # Form parametresi olarak
    db: Session = Depends(get_db)
):
    """
    UBL-TR formatında XML e-fatura yükle
    
    - Tek XML dosyası veya ZIP (içinde XML'ler)
    - **OTOMATIK** gelen/giden tespiti (bizim VKN'ye göre)
    - **OTOMATIK** e-fatura/e-arşiv tespiti (ProfileID'ye göre)
    - Otomatik dizin organizasyonu (data/einvoices/incoming|outgoing/YYYY/MM-ayadi/)
    - Otomatik contact matching
    - Duplicate kontrolü (UUID)
    
    Parameters:
        direction: 'incoming' (gelen) veya 'outgoing' (giden) - sadece fallback için
    
    ⚠️ Direction parametresi artık sadece fallback. Sistem **otomatik tespit ediyor**:
       - Bizim VKN AccountingCustomerParty'de ise → GELEN
       - Bizim VKN AccountingSupplierParty'de ise → GİDEN
    """
    import os
    import shutil
    import hashlib
    from pathlib import Path
    
    settings = Settings()
    company_vkn = settings.COMPANY_TAX_NUMBER
    
    imported_count = 0
    updated_count = 0  # PDF'den XML'e güncellenen kayıtlar
    skipped_count = 0
    error_count = 0
    errors = []
    categorized = {
        'incoming': 0,
        'outgoing': 0,
        'incoming-archive': 0,
        'outgoing-archive': 0
    }
    direction_stats = {
        'auto_detected': 0,
        'fallback_used': 0
    }
    
    xml_files = []
    
    try:
        for file in files:
            content = await file.read()
            
            # ZIP dosyası mı kontrol et
            if file.filename.lower().endswith('.zip'):
                try:
                    with zipfile.ZipFile(io.BytesIO(content)) as zf:
                        for zip_info in zf.namelist():
                            if zip_info.lower().endswith('.xml'):
                                xml_content = zf.read(zip_info)
                                xml_files.append((zip_info, xml_content))
                except zipfile.BadZipFile:
                    errors.append(f'{file.filename}: Geçersiz ZIP dosyası')
                    error_count += 1
            
            # XML dosyası
            elif file.filename.lower().endswith('.xml'):
                xml_files.append((file.filename, content))
            
            else:
                errors.append(f'{file.filename}: Desteklenmeyen dosya tipi (sadece XML/ZIP)')
                error_count += 1
        
        # XML dosyalarını işle
        for filename, xml_content in xml_files:
            try:
                # Parse XML
                invoice_data, parse_errors = parse_xml_invoice(xml_content, filename)
                
                if parse_errors:
                    errors.extend([f'{filename}: {err}' for err in parse_errors])
                    error_count += 1
                    continue
                
                if not invoice_data:
                    errors.append(f'{filename}: Parse edilemedi')
                    error_count += 1
                    continue
                
                # ========== OTOMATIK DIRECTION TESPİTİ ==========
                # Bizim VKN'mizi kontrol et
                customer_vkn = invoice_data.get('customer_tax_number', '').replace('.', '').strip()
                supplier_vkn = invoice_data.get('supplier_tax_number', '').replace('.', '').strip()
                company_vkn_clean = company_vkn.replace('.', '').strip()
                
                detected_direction = None
                
                # VKN'leri numeric olarak karşılaştır
                if customer_vkn and company_vkn_clean:
                    try:
                        if int(customer_vkn) == int(company_vkn_clean):
                            detected_direction = 'incoming'  # Biz alıcıyız → GELEN
                    except:
                        if customer_vkn == company_vkn_clean:
                            detected_direction = 'incoming'
                
                if supplier_vkn and company_vkn_clean and not detected_direction:
                    try:
                        if int(supplier_vkn) == int(company_vkn_clean):
                            detected_direction = 'outgoing'  # Biz satıcıyız → GİDEN
                    except:
                        if supplier_vkn == company_vkn_clean:
                            detected_direction = 'outgoing'
                
                # Tespit edilmediyse fallback kullan
                if detected_direction:
                    final_direction = detected_direction
                    direction_stats['auto_detected'] += 1
                else:
                    final_direction = direction
                    direction_stats['fallback_used'] += 1
                    errors.append(f'{filename}: Direction otomatik tespit edilemedi, "{direction}" kullanıldı')
                
                # Kategori tespiti (invoice_profile ile)
                profile = invoice_data.get('invoice_scenario', '').upper()
                
                # E-Arşiv mi E-Fatura mı?
                is_archive = 'EARSIV' in profile or 'ARSIV' in profile
                
                if is_archive:
                    category = f'{final_direction}-archive'
                else:
                    category = final_direction
                
                invoice_data['invoice_category'] = category
                
                # XML'i doğru dizine kaydet
                issue_date = invoice_data.get('invoice_date')
                if issue_date:
                    year = issue_date.year
                    month = issue_date.month
                    
                    # Türkçe ay ismi
                    month_names = ['', 'ocak', 'subat', 'mart', 'nisan', 'mayis', 'haziran',
                                 'temmuz', 'agustos', 'eylul', 'ekim', 'kasim', 'aralik']
                    month_name = month_names[month]
                    
                    # Dizin: data/einvoices/{category}/YYYY/MM-ayadi/
                    base_dir = Path('data/einvoices') / category / str(year) / f'{month:02d}-{month_name}'
                    base_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Dosya yolu
                    xml_path = base_dir / filename
                    
                    # XML dosyasını kaydet
                    with open(xml_path, 'wb') as f:
                        f.write(xml_content)
                    
                    # SHA256 hash
                    xml_hash = hashlib.sha256(xml_content).hexdigest()
                    
                    invoice_data['xml_file_path'] = str(xml_path)
                    invoice_data['xml_hash'] = xml_hash
                
                # Database'e kaydet (duplicate kontrolü içinde)
                try:
                    einvoice = create_einvoice_from_xml(db, invoice_data)
                    
                    # Yeni kayıt mı güncelleme mi?
                    if einvoice.source == 'xml' and einvoice.pdf_path:
                        # PDF'den XML'e güncellendi
                        updated_count += 1
                        errors.append(f'{filename}: ✅ PDF kaydı XML ile güncellendi (UUID: {einvoice.invoice_uuid})')
                    else:
                        # Yeni kayıt
                        imported_count += 1
                    
                    categorized[category] += 1
                    
                except ValueError as ve:
                    # Duplicate UUID (zaten XML'den parse edilmiş)
                    skipped_count += 1
                    errors.append(f'{filename}: {str(ve)}')
                
            except Exception as e:
                error_count += 1
                errors.append(f'{filename}: {str(e)}')
        
        return {
            'message': f'{imported_count} yeni e-fatura yüklendi' + (f', {updated_count} PDF kaydı XML ile güncellendi' if updated_count > 0 else ''),
            'imported_count': imported_count,
            'updated_count': updated_count,
            'skipped_count': skipped_count,
            'error_count': error_count,
            'total_files': len(xml_files),
            'categorized': categorized,
            'direction_detection': direction_stats,
            'errors': errors[:20]  # İlk 20 hatayı göster
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'XML yükleme hatası: {str(e)}'
        )


@router.post('/sync-raw-data', summary='XML dosyalarından raw_data senkronize et')
def sync_raw_data_from_xml(db: Session = Depends(get_db)):
    """
    KESİN ÇÖZÜM: XML dosyalarındaki içeriği raw_data alanına yükle
    Bu sayede invoice_lines parse işlemi düzgün çalışacak
    """
    from pathlib import Path
    
    # XML file path'i olan tüm faturaları al
    invoices = db.query(EInvoice).filter(EInvoice.xml_file_path.isnot(None)).all()
    
    updated_count = 0
    error_count = 0
    errors = []
    
    for invoice in invoices:
        try:
            xml_path = Path(invoice.xml_file_path)
            
            if not xml_path.exists():
                error_count += 1
                errors.append(f'ID={invoice.id}: XML dosyası bulunamadı')
                continue
            
            # XML dosyasını oku
            with open(xml_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            # raw_data'yı güncelle
            if invoice.raw_data != xml_content:
                invoice.raw_data = xml_content
                updated_count += 1
                
                if updated_count % 100 == 0:
                    db.commit()
        
        except Exception as e:
            error_count += 1
            errors.append(f'ID={invoice.id}: {str(e)}')
    
    # Son commit
    db.commit()
    
    return {
        'message': f'{updated_count} faturanın raw_data alanı XML içeriği ile güncellendi',
        'updated_count': updated_count,
        'error_count': error_count,
        'total_invoices': len(invoices),
        'errors': errors[:20]
    }

