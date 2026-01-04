"""
E-Fatura API Endpoints - Optimized Version

Özellikler:
- Import önizleme (preview) özelliği
- Temiz ve okunabilir kod yapısı
- Helper fonksiyonlar ayrılmış
- Duplicate kodlar temizlenmiş
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
import pandas as pd
import io
import zipfile
import os
import hashlib
from pathlib import Path

from app.core.database import get_db
from app.core.config import Settings
from app.models.einvoice import EInvoice
from app.models.contact import Contact
from app.models.transaction import Transaction
from app.models.transaction_line import TransactionLine
from app.models.account import Account
from app.models.invoice_tax import InvoiceTax
from app.utils.data_cleaner import (
    clean_company_name, clean_tax_number, clean_phone, 
    clean_email, clean_address, extract_iban_from_text
)
from app.schemas.einvoice import (
    EInvoice as EInvoiceSchema,
    EInvoiceCreate,
    EInvoiceUpdate,
    EInvoiceSummary
)
from app.services.einvoice_xml_service import parse_xml_invoice, create_einvoice_from_xml
from app.services.einvoice_preview_service import preview_xml_invoices
from app.services.invoice_mapping_service import create_mapping, get_transaction_for_invoice

router = APIRouter(prefix='/einvoices', tags=['E-Fatura'])


# ============================================================================
# HELPER FUNCTIONS - Kod Tekrarını Önlemek İçin
# ============================================================================

def normalize_column_name(col: str) -> str:
    """Excel sütun isimlerini normalize et (Türkçe karakter desteği)"""
    col = str(col).strip().upper()
    # Türkçe karakterleri düzelt
    replacements = {'İ': 'I', 'Ş': 'S', 'Ğ': 'G', 'Ü': 'U', 'Ö': 'O', 'Ç': 'C', 'ı': 'I', 'i̇': 'I'}
    for old, new in replacements.items():
        col = col.replace(old, new)
    # Özel karakterleri temizle
    col = col.replace(' ', '_').replace('/', '_').replace('.', '').replace('-', '_')
    return col


def get_decimal_value(col: Optional[str], row: pd.Series) -> Decimal:
    """Pandas satırından Decimal değer çıkar"""
    if col and pd.notna(row.get(col)):
        val = str(row.get(col)).replace(',', '.').replace(' ', '')
        try:
            return Decimal(val) if val else Decimal('0')
        except:
            return Decimal('0')
    return Decimal('0')


def generate_contact_code(db: Session, contact_type: str) -> str:
    """Otomatik cari kodu üret (Müşteri: 120.xxxxx, Satıcı: 320.xxxxx)"""
    prefix = '120' if contact_type == 'customer' else '320'
    
    last_contact = db.query(Contact).filter(
        Contact.code.like(f'{prefix}.%')
    ).order_by(Contact.code.desc()).first()
    
    if last_contact and last_contact.code:
        try:
            last_num = int(last_contact.code.split('.')[-1])
            new_num = last_num + 1
        except:
            new_num = 1
    else:
        new_num = 1
    
    return f'{prefix}.{new_num:05d}'


def create_or_get_contact(
    db: Session, 
    einvoice: EInvoice,
    notes_text: str = None,
    phone: str = None,
    email: str = None
) -> Contact:
    """E-faturadan cari oluştur veya mevcut cariyi getir"""
    
    # VKN ile ara
    contact = db.query(Contact).filter(
        Contact.tax_number == einvoice.supplier_tax_number
    ).first()
    
    # NOTLAR'dan IBAN çıkar
    iban = extract_iban_from_text(notes_text) if notes_text else None
    
    if contact:
        # Mevcut cariyi güncelle (manually_edited=False ise)
        if not contact.manually_edited and einvoice.supplier_name:
            cleaned_name = clean_company_name(einvoice.supplier_name)
            if cleaned_name and cleaned_name != "Bilinmiyor":
                contact.name = cleaned_name
        
        # Eksik alanları doldur
        if not contact.address and einvoice.supplier_address:
            contact.address = clean_address(einvoice.supplier_address)
        if not contact.city and einvoice.supplier_city:
            contact.city = einvoice.supplier_city
        if not contact.district and einvoice.supplier_district:
            contact.district = einvoice.supplier_district
        if not contact.tax_office and einvoice.supplier_tax_office:
            contact.tax_office = einvoice.supplier_tax_office
        if not contact.iban and iban:
            contact.iban = iban
        if not contact.phone and phone:
            contact.phone = clean_phone(phone)
        if not contact.email and email:
            contact.email = clean_email(email)
        
        db.flush()
        return contact
    
    # Yeni cari oluştur
    cleaned_name = clean_company_name(einvoice.supplier_name)
    if not cleaned_name or cleaned_name == "Bilinmiyor":
        cleaned_name = einvoice.supplier_name
    
    contact = Contact(
        code=generate_contact_code(db, 'supplier'),
        name=cleaned_name,
        tax_number=clean_tax_number(einvoice.supplier_tax_number),
        tax_office=einvoice.supplier_tax_office,
        address=clean_address(einvoice.supplier_address) if einvoice.supplier_address else None,
        city=einvoice.supplier_city,
        district=einvoice.supplier_district,
        phone=clean_phone(phone) if phone else None,
        email=clean_email(email) if email else None,
        iban=iban,
        contact_type='supplier',
        is_active=True,
        manually_edited=False
    )
    db.add(contact)
    db.flush()
    
    return contact


def calculate_total_vat(einvoice: EInvoice) -> Decimal:
    """Toplam KDV hesapla (tüm oranlar)"""
    return (
        einvoice.vat_0_amount +
        einvoice.vat_1_amount +
        einvoice.vat_8_amount +
        einvoice.vat_10_amount +
        einvoice.vat_18_amount +
        einvoice.vat_20_amount
    )


def get_or_create_accounts(db: Session) -> Dict[str, Account]:
    """Muhasebe fişi için gerekli hesapları getir"""
    
    # Gider hesabı (153 - Ticari Mallar veya 600)
    expense_account = db.query(Account).filter(
        Account.code.like('153%')
    ).first() or db.query(Account).filter(
        Account.code == '600'
    ).first()
    
    # KDV hesabı (191 - İndirilecek KDV)
    vat_account = db.query(Account).filter(
        Account.code == '191'
    ).first()
    
    # Cari hesabı (320 - Satıcılar)
    supplier_account = db.query(Account).filter(
        Account.code.like('320%')
    ).first()
    
    # Tevkifat hesabı (360 - Ödenecek Vergi ve Fonlar)
    withholding_account = db.query(Account).filter(
        Account.code.like('360%')
    ).first()
    
    if not expense_account or not vat_account or not supplier_account:
        raise HTTPException(
            status_code=400,
            detail='Gerekli hesaplar bulunamadı (153/600, 191, 320)'
        )
    
    return {
        'expense': expense_account,
        'vat': vat_account,
        'supplier': supplier_account,
        'withholding': withholding_account
    }


def generate_transaction_number(db: Session, period: str) -> str:
    """Fiş numarası oluştur (EFT-YYYY-MM-XXXX)"""
    last_trans = db.query(Transaction).filter(
        Transaction.accounting_period == period
    ).order_by(desc(Transaction.id)).first()
    
    if last_trans and last_trans.transaction_number:
        try:
            last_num = int(last_trans.transaction_number.split('-')[-1])
            return f'EFT-{period}-{last_num + 1:04d}'
        except:
            return f'EFT-{period}-0001'
    
    return f'EFT-{period}-0001'


def create_accounting_transaction(db: Session, einvoice: EInvoice, contact: Contact) -> Transaction:
    """E-faturadan muhasebe fişi oluştur"""
    
    period = einvoice.issue_date.strftime('%Y-%m')
    accounts = get_or_create_accounts(db)
    
    # Belge türü ve alt türünü bul
    from app.models.document_type import DocumentType, DocumentSubtype
    doc_type = db.query(DocumentType).filter(DocumentType.name == 'Alış Faturası').first()
    doc_subtype = db.query(DocumentSubtype).filter(
        DocumentSubtype.name == 'E-Fatura',
        DocumentSubtype.document_type_id == doc_type.id if doc_type else None
    ).first()
    
    # Fiş oluştur
    transaction = Transaction(
        transaction_number=generate_transaction_number(db, period),
        transaction_date=einvoice.issue_date,
        accounting_period=period,
        document_number=einvoice.invoice_number,
        description=f'{contact.name} - {einvoice.invoice_number}',
        document_type_id=doc_type.id if doc_type else None,
        document_subtype_id=doc_subtype.id if doc_subtype else None
    )
    db.add(transaction)
    db.flush()
    
    # Satır 1: BORÇ - Gider/Mal (KDV Hariç)
    db.add(TransactionLine(
        transaction_id=transaction.id,
        account_id=accounts['expense'].id,
        contact_id=contact.id,
        description=f'{einvoice.supplier_name} - Mal/Hizmet',
        debit=float(einvoice.line_extension_amount),
        credit=0,
        vat_base=float(einvoice.line_extension_amount)
    ))
    
    # Satır 2: BORÇ - KDV
    total_vat = calculate_total_vat(einvoice)
    if total_vat > 0:
        db.add(TransactionLine(
            transaction_id=transaction.id,
            account_id=accounts['vat'].id,
            description='İndirilecek KDV',
            debit=float(total_vat),
            credit=0
        ))
    
    # Satır 3: ALACAK - Tevkifat (Varsa)
    if einvoice.withholding_total and einvoice.withholding_total > 0 and accounts['withholding']:
        db.add(TransactionLine(
            transaction_id=transaction.id,
            account_id=accounts['withholding'].id,
            description=f'Tevkifat - {einvoice.supplier_name}',
            debit=0,
            credit=float(einvoice.withholding_total)
        ))
    
    # Satır 4: ALACAK - Cari
    net_payable = einvoice.payable_amount
    if einvoice.withholding_total:
        net_payable = net_payable - einvoice.withholding_total
    
    db.add(TransactionLine(
        transaction_id=transaction.id,
        account_id=accounts['supplier'].id,
        contact_id=contact.id,
        description=f'{einvoice.supplier_name} - Borç',
        debit=0,
        credit=float(net_payable)
    ))
    
    return transaction


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get('/summary', response_model=EInvoiceSummary)
def get_einvoices_summary(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """E-fatura özet istatistikleri (Optimize edildi - tek sorgu)"""
    
    # Base query
    base_query = db.query(EInvoice)
    if date_from:
        base_query = base_query.filter(EInvoice.issue_date >= date_from)
    if date_to:
        base_query = base_query.filter(EInvoice.issue_date <= date_to)
    
    # Tek sorgu ile tüm istatistikler
    stats = db.query(
        func.count(EInvoice.id).label('total_count'),
        func.sum(EInvoice.payable_amount).label('total_amount'),
        func.sum(func.case((EInvoice.processing_status == 'IMPORTED', 1), else_=0)).label('parsed_count'),
        func.sum(func.case((EInvoice.processing_status == 'TRANSACTION_CREATED', 1), else_=0)).label('imported_count'),
        func.sum(func.case((EInvoice.processing_status == 'ERROR', 1), else_=0)).label('error_count'),
        func.sum(func.case((EInvoice.processing_status.in_(['MATCHED', 'PENDING']), 1), else_=0)).label('pending_count'),
        # Kategoriler
        func.sum(func.case((EInvoice.invoice_category == 'incoming', 1), else_=0)).label('incoming_count'),
        func.sum(func.case((EInvoice.invoice_category == 'incoming', EInvoice.payable_amount), else_=0)).label('incoming_amount'),
        func.sum(func.case((EInvoice.invoice_category == 'incoming-archive', 1), else_=0)).label('incoming_archive_count'),
        func.sum(func.case((EInvoice.invoice_category == 'incoming-archive', EInvoice.payable_amount), else_=0)).label('incoming_archive_amount'),
        func.sum(func.case((EInvoice.invoice_category == 'outgoing', 1), else_=0)).label('outgoing_count'),
        func.sum(func.case((EInvoice.invoice_category == 'outgoing', EInvoice.payable_amount), else_=0)).label('outgoing_amount'),
        func.sum(func.case((EInvoice.invoice_category == 'outgoing-archive', 1), else_=0)).label('outgoing_archive_count'),
        func.sum(func.case((EInvoice.invoice_category == 'outgoing-archive', EInvoice.payable_amount), else_=0)).label('outgoing_archive_amount'),
    ).filter(
        *([EInvoice.issue_date >= date_from] if date_from else []),
        *([EInvoice.issue_date <= date_to] if date_to else [])
    ).first()
    
    return {
        'total_count': stats.total_count or 0,
        'total_amount': stats.total_amount or 0,
        'parsed_count': stats.parsed_count or 0,
        'imported_count': stats.imported_count or 0,
        'error_count': stats.error_count or 0,
        'pending_count': stats.pending_count or 0,
        'incoming_count': stats.incoming_count or 0,
        'incoming_amount': stats.incoming_amount or 0,
        'incoming_archive_count': stats.incoming_archive_count or 0,
        'incoming_archive_amount': stats.incoming_archive_amount or 0,
        'outgoing_count': stats.outgoing_count or 0,
        'outgoing_amount': stats.outgoing_amount or 0,
        'outgoing_archive_count': stats.outgoing_archive_count or 0,
        'outgoing_archive_amount': stats.outgoing_archive_amount or 0,
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
    """E-faturaları listele"""
    
    query = db.query(EInvoice)
    
    # Filtreler
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
    
    # Sıralama: signing_time (gerçek geliş) > issue_date
    query = query.order_by(
        desc(EInvoice.signing_time),
        desc(EInvoice.issue_date)
    )
    
    items = query.offset(skip).limit(limit).all()
    
    # Contact IBAN'larını ekle
    result = []
    for item in items:
        item_dict = {c.name: getattr(item, c.name) for c in item.__table__.columns}
        item_dict['contact_iban'] = None
        
        if item.contact_id:
            contact = db.query(Contact).filter(Contact.id == item.contact_id).first()
            if contact and contact.iban:
                item_dict['contact_iban'] = contact.iban
        
        result.append(item_dict)
    
    return result


@router.get('/{invoice_id}', response_model=EInvoiceSchema)
def get_einvoice(invoice_id: int, db: Session = Depends(get_db)):
    """E-fatura detayı (invoice_lines ve tax_details dahil)"""
    
    einvoice = db.query(EInvoice).filter(EInvoice.id == invoice_id).first()
    if not einvoice:
        raise HTTPException(status_code=404, detail='E-fatura bulunamadı')
    
    # Vergi detaylarını yükle
    tax_details = db.query(InvoiceTax).filter(
        InvoiceTax.einvoice_id == einvoice.id
    ).all()
    
    tax_details_list = [{
        'id': tax.id,
        'tax_type_code': tax.tax_type_code,
        'tax_name': tax.tax_name,
        'tax_percent': float(tax.tax_percent) if tax.tax_percent else 0,
        'taxable_amount': float(tax.taxable_amount) if tax.taxable_amount else 0,
        'tax_amount': float(tax.tax_amount) if tax.tax_amount else 0,
        'currency_code': tax.currency_code,
        'exemption_reason_code': tax.exemption_reason_code,
        'exemption_reason': tax.exemption_reason
    } for tax in tax_details]
    
    # Invoice lines parse et (XML'den)
    invoice_lines = []
    if einvoice.raw_data and ('<InvoiceLine' in einvoice.raw_data or 'cac:InvoiceLine' in einvoice.raw_data):
        import xml.etree.ElementTree as ET
        import html
        
        try:
            # XML unescape
            xml_data = html.unescape(einvoice.raw_data) if '&quot;' in einvoice.raw_data or '&lt;' in einvoice.raw_data else einvoice.raw_data
            
            root = ET.fromstring(xml_data)
            ns = {
                'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
            }
            
            for line in root.findall('.//cac:InvoiceLine', ns):
                line_data = {}
                
                id_elem = line.find('cbc:ID', ns)
                line_data['id'] = id_elem.text if id_elem is not None else None
                
                qty_elem = line.find('cbc:InvoicedQuantity', ns)
                if qty_elem is not None:
                    line_data['quantity'] = float(qty_elem.text) if qty_elem.text else 0
                    line_data['unit'] = qty_elem.get('unitCode', '')
                
                item_elem = line.find('.//cac:Item/cbc:Name', ns)
                line_data['item_name'] = item_elem.text if item_elem is not None else None
                
                price_elem = line.find('.//cac:Price/cbc:PriceAmount', ns)
                if price_elem is not None:
                    line_data['unit_price'] = float(price_elem.text) if price_elem.text else 0
                    line_data['currency'] = price_elem.get('currencyID', 'TRY')
                
                total_elem = line.find('cbc:LineExtensionAmount', ns)
                if total_elem is not None:
                    line_data['line_total'] = float(total_elem.text) if total_elem.text else 0
                
                tax_total = line.find('.//cac:TaxTotal/cbc:TaxAmount', ns)
                if tax_total is not None:
                    line_data['tax_amount'] = float(tax_total.text) if tax_total.text else 0
                
                tax_percent = line.find('.//cac:TaxSubtotal/cbc:Percent', ns)
                if tax_percent is not None:
                    line_data['tax_percent'] = float(tax_percent.text) if tax_percent.text else 0
                
                invoice_lines.append(line_data)
        
        except Exception as e:
            print(f"ERROR: XML parse hatası: {e}")
    
    # Response
    response_data = {
        **{c.name: getattr(einvoice, c.name) for c in einvoice.__table__.columns},
        'invoice_lines': invoice_lines,
        'tax_details': tax_details_list
    }
    
    # Contact IBAN ekle
    if einvoice.contact_id:
        contact = db.query(Contact).filter(Contact.id == einvoice.contact_id).first()
        if contact and contact.iban:
            response_data['contact_iban'] = contact.iban
    
    return response_data


@router.get('/{invoice_id}/import-preview')
def preview_import(invoice_id: int, db: Session = Depends(get_db)):
    """
    🆕 Import önizleme - Kullanıcıya muhasebe kaydını göster (kayıt oluşturmaz)
    
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
    
    warnings = []
    
    # 1. Cari kontrolü
    contact = db.query(Contact).filter(
        Contact.tax_number == einvoice.supplier_tax_number
    ).first()
    
    contact_info = {
        'exists': bool(contact),
        'name': contact.name if contact else (einvoice.supplier_name or 'Bilinmiyor'),
        'tax_number': einvoice.supplier_tax_number,
        'code': contact.code if contact else generate_contact_code(db, 'supplier'),
        'will_create': not bool(contact),
        'iban': contact.iban if contact else None
    }
    
    if not contact:
        warnings.append('⚠️  Yeni cari oluşturulacak')
    
    # 2. Hesapları kontrol et
    try:
        accounts = get_or_create_accounts(db)
    except HTTPException as e:
        raise e
    
    # Hesap uyarıları
    expense_acc = db.query(Account).filter(Account.code.like('153%')).first()
    if not expense_acc:
        warnings.append('⚠️  153 hesabı bulunamadı, 600 kullanılacak')
    
    # 3. Fiş satırlarını hazırla
    period = einvoice.issue_date.strftime('%Y-%m')
    total_vat = calculate_total_vat(einvoice)
    net_payable = einvoice.payable_amount
    if einvoice.withholding_total:
        net_payable = net_payable - einvoice.withholding_total
    
    lines = [
        {
            'line_no': 1,
            'account_code': accounts['expense'].code,
            'account_name': accounts['expense'].name,
            'description': f'{einvoice.supplier_name} - Mal/Hizmet',
            'debit': float(einvoice.line_extension_amount),
            'credit': 0.0
        },
        {
            'line_no': 2,
            'account_code': accounts['vat'].code,
            'account_name': accounts['vat'].name,
            'description': 'İndirilecek KDV',
            'debit': float(total_vat),
            'credit': 0.0
        }
    ]
    
    line_no = 3
    
    # Tevkifat varsa
    if einvoice.withholding_total and einvoice.withholding_total > 0 and accounts.get('withholding'):
        lines.append({
            'line_no': line_no,
            'account_code': accounts['withholding'].code,
            'account_name': accounts['withholding'].name,
            'description': f'Tevkifat - {einvoice.supplier_name}',
            'debit': 0.0,
            'credit': float(einvoice.withholding_total)
        })
        line_no += 1
    
    # Cari satır
    lines.append({
        'line_no': line_no,
        'account_code': accounts['supplier'].code,
        'account_name': accounts['supplier'].name,
        'description': f'{einvoice.supplier_name} - Borç',
        'debit': 0.0,
        'credit': float(net_payable)
    })
    
    # Toplam kontrol
    total_debit = sum(line['debit'] for line in lines)
    total_credit = sum(line['credit'] for line in lines)
    
    if abs(total_debit - total_credit) > 0.01:
        warnings.append(f'❌ Denklik hatası: Borç={total_debit:.2f}, Alacak={total_credit:.2f}')
    
    return {
        'invoice': {
            'id': einvoice.id,
            'invoice_number': einvoice.invoice_number,
            'invoice_date': str(einvoice.issue_date),
            'supplier_name': einvoice.supplier_name,
            'payable_amount': float(einvoice.payable_amount),
            'currency_code': einvoice.currency_code or 'TRY'
        },
        'contact': contact_info,
        'transaction': {
            'number': f'EFT-{period}-XXXX (önizleme)',
            'date': str(einvoice.issue_date),
            'period': period,
            'document_type': 'E-FATURA',
            'document_number': einvoice.invoice_number,
            'lines': lines,
            'total_debit': round(total_debit, 2),
            'total_credit': round(total_credit, 2),
            'is_balanced': abs(total_debit - total_credit) < 0.01
        },
        'warnings': warnings,
        'can_import': abs(total_debit - total_credit) < 0.01
    }


@router.post('/{invoice_id}/import')
def import_einvoice_to_accounting(invoice_id: int, db: Session = Depends(get_db)):
    """E-faturayı muhasebe kaydına dönüştür (Gerçek import)"""
    
    einvoice = db.query(EInvoice).filter(EInvoice.id == invoice_id).first()
    if not einvoice:
        raise HTTPException(status_code=404, detail='E-fatura bulunamadı')
    
    if einvoice.processing_status == 'COMPLETED':
        raise HTTPException(status_code=400, detail='Bu fatura zaten import edilmiş')
    
    try:
        # 1. Cari oluştur/getir
        contact = create_or_get_contact(db, einvoice)
        
        # 2. Muhasebe fişi oluştur
        transaction = create_accounting_transaction(db, einvoice, contact)
        
        # 3. Mapping oluştur
        create_mapping(
            db=db,
            einvoice_id=einvoice.id,
            transaction_id=transaction.id,
            mapping_type='manual',
            confidence_score=1.00
        )
        
        # 4. E-fatura güncelle
        einvoice.contact_id = contact.id
        einvoice.processing_status = 'COMPLETED'
        einvoice.error_message = None
        einvoice.transaction_id = transaction.id
        
        db.commit()
        db.refresh(einvoice)
        
        return {
            'message': 'E-fatura başarıyla import edildi',
            'contact_id': contact.id,
            'transaction_id': transaction.id,
            'transaction_number': transaction.transaction_number
        }
        
    except Exception as e:
        db.rollback()
        einvoice.processing_status = 'ERROR'
        einvoice.error_message = str(e)
        db.commit()
        
        raise HTTPException(status_code=500, detail=f'Import hatası: {str(e)}')


# Diğer endpoint'ler eski dosyadan devam edecek (create, update, delete, pdf, upload vb.)
# Bu dosya sadece core fonksiyonları ve import önizleme özelliğini içeriyor
