"""
E-Fatura Muhasebe Servisi

E-faturalardan otomatik muhasebe kaydı oluşturma mantığı.
Hesap mapping kuralları ve fiş oluşturma işlemleri burada yönetilir.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
import json
import os

from app.models.einvoice import EInvoice
from app.models.contact import Contact
from app.models.transaction import Transaction
from app.models.transaction_line import TransactionLine
from app.models.account import Account
from app.models.document_type import DocumentType, DocumentSubtype
from app.models.cost_center import CostCenter
from app.utils.data_cleaner import (
    clean_company_name, clean_tax_number, clean_phone, 
    clean_email, clean_address, extract_iban_from_text
)
from app.utils.transaction_numbering import get_next_transaction_number
from app.utils.category_mapping import categorize_invoice_line, get_account_for_category
from app.services.einvoice_xml_service import parse_xml_invoice

# EINVOICE_DIR sabitini tanımla
EINVOICE_DIR = "c:/Projects/muhasebe-sistem/data/einvoice"


def generate_contact_code(db: Session, contact_type: str) -> str:
    """
    Otomatik cari kodu üret (Luca/Zirve tarzı)
    
    Args:
        db: Database session
        contact_type: 'customer' veya 'supplier'
    
    Returns:
        str: Cari kodu (örn: 120.00001, 320.00001)
    """
    # Müşteriler: 120.xxxxx, Satıcılar: 320.xxxxx (5 hane)
    prefix = '120' if contact_type == 'customer' else '320'
    
    # Son kodu bul
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
    
    return f'{prefix}.{new_num:05d}'  # 5 haneli: 00001, 00002...


def generate_fixed_asset_account(db: Session, category: str, asset_name: str) -> str:
    """
    Demirbaş veya taşıt için yeni hesap kodu oluştur
    
    Args:
        db: Database session
        category: Demirbaş kategorisi (Konteyner, Makine, İnşaat Kalıpları, vb.) veya 'Taşıt'
        asset_name: Demirbaş/Taşıt adı
    
    Returns:
        str: Yeni hesap kodu (örn: 255.01.001, 255.02.002)
    """
    # Kategori kodları
    category_codes = {
        'Konteynerler': '255.01',
        'Makine Ve Ekipmanlar': '255.02',
        'İnşaat Kalıpları': '255.03',
        'Şantiyeye Ait Alet Ve Gereçleri': '255.04',
        'İş Makinası Ekipmanları': '255.05',
        'Taşıt': '255.06'  # Taşıtlar için özel kod
    }
    
    prefix = category_codes.get(category)
    if not prefix:
        raise HTTPException(status_code=400, detail=f"Geçersiz demirbaş kategorisi: {category}")
    
    # Son kodu bul
    last_account = db.query(Account).filter(
        Account.code.like(f'{prefix}.%')
    ).order_by(Account.code.desc()).first()
    
    if last_account and last_account.code:
        try:
            # 255.01.001 -> 001 -> 1 -> 2
            last_num = int(last_account.code.split('.')[-1])
            new_num = last_num + 1
        except:
            new_num = 1
    else:
        new_num = 1
    
    new_code = f'{prefix}.{new_num:03d}'  # 3 haneli: 001, 002...
    
    # Yeni hesap oluştur
    new_account = Account(
        code=new_code,
        name=asset_name,
        account_type='ASSET',  # Demirbaş/Taşıt = Varlık
        is_active=True
    )
    db.add(new_account)
    db.flush()  # ID'yi al ama henüz commit etme
    
    return new_code


def create_or_get_contact(
    db: Session, 
    einvoice: EInvoice,
    notes_text: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None
) -> Contact:
    """
    E-faturadan cari oluştur veya mevcut cariyi getir
    
    Args:
        db: Database session
        einvoice: E-fatura kaydı
        notes_text: NOTLAR sütunundan gelen metin (IBAN çıkarılacak)
        phone: Telefon numarası
        email: E-posta adresi
    
    Returns:
        Contact: Oluşturulan veya bulunan cari kayıt
    """
    # VKN ile ara
    contact = db.query(Contact).filter(
        Contact.tax_number == einvoice.supplier_tax_number
    ).first()
    
    # NOTLAR'dan IBAN çıkar (varsa)
    iban = None
    if notes_text:
        iban = extract_iban_from_text(notes_text)
    
    if contact:
        # Mevcut cariyi güncelle (eksik bilgiler varsa VE manually_edited=False ise)
        
        # Ünvanı güncelle (manually_edited değilse)
        if not contact.manually_edited and einvoice.supplier_name:
            cleaned_name = clean_company_name(einvoice.supplier_name)
            if cleaned_name and cleaned_name != "Bilinmiyor":
                contact.name = cleaned_name
        
        # Eksik alanları doldur (her zaman)
        if not contact.address and einvoice.supplier_address:
            contact.address = clean_address(einvoice.supplier_address)
        if not contact.city and einvoice.supplier_city:
            contact.city = einvoice.supplier_city
        if not contact.district and einvoice.supplier_district:
            contact.district = einvoice.supplier_district
        if not contact.tax_office and einvoice.supplier_tax_office:
            contact.tax_office = einvoice.supplier_tax_office
        
        # IBAN bilgisi ekle (boşsa)
        if not contact.iban and iban:
            contact.iban = iban
        
        # Telefon ve email (boşsa)
        if not contact.phone and phone:
            contact.phone = clean_phone(phone)
        if not contact.email and email:
            contact.email = clean_email(email)
        
        db.flush()
        return contact
    
    # Yeni cari oluştur
    contact_code = generate_contact_code(db, 'supplier')
    
    # Ünvan temizle
    cleaned_name = clean_company_name(einvoice.supplier_name)
    if not cleaned_name or cleaned_name == "Bilinmiyor":
        cleaned_name = einvoice.supplier_name  # Orijinali kullan
    
    contact = Contact(
        code=contact_code,
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
        manually_edited=False  # Otomatik oluşturuldu
    )
    db.add(contact)
    db.flush()  # ID almak için
    
    return contact


class AccountMapper:
    """Hesap mapping kurallarını yöneten sınıf"""
    
    @staticmethod
    def get_expense_account(db: Session) -> Account:
        """Gider hesabı bul (153 - Ticari Mallar veya 600 - Yurt İçi Satışlar)"""
        account = db.query(Account).filter(Account.code.like('153%')).first()
        if not account:
            account = db.query(Account).filter(Account.code == '600').first()
        if not account:
            raise HTTPException(
                status_code=400,
                detail='Gider hesabı bulunamadı (153 veya 600)'
            )
        return account
    
    @staticmethod
    def get_vat_account(db: Session) -> Account:
        """KDV hesabı bul (191 - İndirilecek KDV)"""
        account = db.query(Account).filter(Account.code == '191').first()
        if not account:
            raise HTTPException(
                status_code=400,
                detail='KDV hesabı bulunamadı (191 - İndirilecek KDV)'
            )
        return account
    
    @staticmethod
    def get_supplier_account(db: Session) -> Account:
        """Satıcı hesabı bul (320 - Satıcılar)"""
        account = db.query(Account).filter(Account.code.like('320%')).first()
        if not account:
            raise HTTPException(
                status_code=400,
                detail='Satıcı hesabı bulunamadı (320 - Satıcılar)'
            )
        return account
    
    @staticmethod
    def get_withholding_account(db: Session) -> Optional[Account]:
        """Tevkifat hesabı bul (360 - Ödenecek Vergi ve Fonlar)"""
        return db.query(Account).filter(Account.code.like('360%')).first()


def create_accounting_transaction(
    db: Session, 
    einvoice: EInvoice, 
    contact: Contact
) -> Transaction:
    """
    E-faturadan otomatik muhasebe fişi oluştur (YENİ VERSİYON)
    
    generate_transaction_lines_from_invoice() kullanarak tüm detayları kaydet:
    - Transaction: cost_center_id, document_type_id, document_subtype_id
    - TransactionLine: quantity, unit, vat_rate, withholding_rate, vat_base
    
    Args:
        db: Database session
        einvoice: E-fatura kaydı
        contact: Cari kayıt
    
    Returns:
        Transaction: Oluşturulan muhasebe fişi
    """
    # XML dosyasını oku ve parse et
    xml_path = os.path.join(EINVOICE_DIR, einvoice.filename)
    if not os.path.exists(xml_path):
        raise HTTPException(status_code=404, detail="E-fatura XML dosyası bulunamadı")
    
    with open(xml_path, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    # XML'i parse et
    invoice_data = parse_xml_invoice(xml_content, einvoice.filename)
    
    # Fiş satırlarını üret (generate_transaction_lines_from_invoice - tüm detayları içerir)
    lines_data = generate_transaction_lines_from_invoice(
        db=db,
        invoice_data=invoice_data,
        contact=contact,
        einvoice=einvoice
    )
    
    # Fiş numarası oluştur (commit=True - Kısa lock, hemen serbest bırak)
    transaction_number = get_next_transaction_number(db, prefix="F", commit=True)
    period = einvoice.issue_date.strftime('%Y-%m')
    
    # Belge türü ve alt türünü bul
    doc_type = db.query(DocumentType).filter(DocumentType.name == 'Alış Faturası').first()
    doc_subtype = db.query(DocumentSubtype).filter(
        DocumentSubtype.name == 'E-Fatura',
        DocumentSubtype.document_type_id == doc_type.id if doc_type else None
    ).first()
    
    # Varsayılan cost center (Merkez)
    cost_center = db.query(CostCenter).filter(CostCenter.name == 'Merkez').first()
    
    # Ana fiş oluştur - TÜM ALANLARI DOLDUR
    transaction = Transaction(
        transaction_number=transaction_number,
        transaction_date=einvoice.issue_date,
        accounting_period=period,
        document_number=einvoice.invoice_number,
        description=f'{contact.name} - {einvoice.invoice_number}',
        cost_center_id=cost_center.id if cost_center else None,
        document_type_id=doc_type.id if doc_type else None,
        document_subtype_id=doc_subtype.id if doc_subtype else None
    )
    db.add(transaction)
    db.flush()
    
    # Satırları ekle - TÜM ALANLARI DOLDUR
    for line_data in lines_data:
        # Hesap kodundan account_id bul
        account = db.query(Account).filter(Account.code == line_data['account_code']).first()
        if not account:
            raise HTTPException(
                status_code=400,
                detail=f"Hesap bulunamadı: {line_data['account_code']}"
            )
        
        line = TransactionLine(
            transaction_id=transaction.id,
            account_id=account.id,
            contact_id=contact.id if line_data.get('is_supplier_line') else None,
            description=line_data.get('description', ''),
            debit=float(line_data.get('debit', 0)),
            credit=float(line_data.get('credit', 0)),
            quantity=float(line_data['quantity']) if line_data.get('quantity') else None,
            unit=line_data.get('unit'),
            vat_rate=float(line_data['vat_rate']) if line_data.get('vat_rate') else None,
            withholding_rate=float(line_data['withholding_rate']) if line_data.get('withholding_rate') else None,
            vat_base=float(line_data['vat_base']) if line_data.get('vat_base') else None
        )
        db.add(line)
    
    return transaction


def create_custom_transaction(
    db: Session, 
    einvoice: EInvoice, 
    contact: Contact,
    transaction_data: dict
) -> Transaction:
    """
    Kullanıcının düzenlediği fiş verisiyle muhasebe fişi oluştur (YENİ VERSİYON)
    
    TÜM ALANLARI KAYDET:
    - Transaction: cost_center_id, document_type_id, document_subtype_id
    - TransactionLine: quantity, unit, vat_rate, withholding_rate, vat_base
    
    Args:
        db: Database session
        einvoice: E-fatura kaydı
        contact: Cari kayıt
        transaction_data: Düzenlenmiş fiş verileri
            {
                "transaction_number": "F00000123",  # Opsiyonel
                "cost_center_id": 31,  # Opsiyonel
                "document_type_id": 1,  # Opsiyonel
                "document_subtype_id": 1,  # Opsiyonel
                "lines": [
                    {
                        "account_code": "153",
                        "description": "Açıklama",
                        "debit": 1000.00,
                        "credit": 0.00,
                        "quantity": 10.0,  # Opsiyonel
                        "unit": "ADET",  # Opsiyonel
                        "vat_rate": 0.20,  # Opsiyonel
                        "withholding_rate": 0.40,  # Opsiyonel
                        "vat_base": 1000.00  # Opsiyonel
                    },
                    ...
                ]
            }
    
    Returns:
        Transaction: Oluşturulan muhasebe fişi
    """
    period = einvoice.issue_date.strftime('%Y-%m')
    
    # Fiş numarası kullanıcı tarafından belirlenmişse onu kullan, yoksa yeni oluştur
    transaction_number = transaction_data.get('transaction_number')
    if not transaction_number:
        # Counter'ı hemen commit et (kısa lock süresi)
        # Ana transaction başarısız olursa numara atlanır ama duplicate olmaz
        transaction_number = get_next_transaction_number(db, prefix="F", commit=True)
    
    # Belge türü ve alt türü - kullanıcı belirtmişse onu kullan
    cost_center_id = transaction_data.get('cost_center_id')
    document_type_id = transaction_data.get('document_type_id')
    document_subtype_id = transaction_data.get('document_subtype_id')
    
    # Eğer kullanıcı belirtmemişse varsayılanları kullan
    if not document_type_id:
        doc_type = db.query(DocumentType).filter(DocumentType.name == 'Alış Faturası').first()
        document_type_id = doc_type.id if doc_type else None
    
    if not document_subtype_id and document_type_id:
        doc_subtype = db.query(DocumentSubtype).filter(
            DocumentSubtype.name == 'E-Fatura',
            DocumentSubtype.document_type_id == document_type_id
        ).first()
        document_subtype_id = doc_subtype.id if doc_subtype else None
    
    if not cost_center_id:
        cost_center = db.query(CostCenter).filter(CostCenter.name == 'Merkez').first()
        cost_center_id = cost_center.id if cost_center else None
    
    # Fiş oluştur - TÜM ALANLARI DOLDUR
    transaction = Transaction(
        transaction_number=transaction_number,
        transaction_date=einvoice.issue_date,
        accounting_period=period,
        document_number=einvoice.invoice_number,
        description=f'{contact.name} - {einvoice.invoice_number}',
        cost_center_id=cost_center_id,
        document_type_id=document_type_id,
        document_subtype_id=document_subtype_id
    )
    db.add(transaction)
    db.flush()
    
    # Kullanıcının düzenlediği satırları ekle - TÜM ALANLARI DOLDUR
    for line_data in transaction_data.get('lines', []):
        # Hesap ID'sini bul
        account = db.query(Account).filter(
            Account.code == line_data.get('account_code')
        ).first()
        
        if not account:
            raise HTTPException(
                status_code=400,
                detail=f"Hesap bulunamadı: {line_data.get('account_code')}"
            )
        
        line = TransactionLine(
            transaction_id=transaction.id,
            account_id=account.id,
            contact_id=contact.id if line_data.get('account_code', '').startswith('320') else None,
            description=line_data.get('description', ''),
            debit=float(line_data.get('debit', 0)),
            credit=float(line_data.get('credit', 0)),
            quantity=float(line_data['quantity']) if line_data.get('quantity') else None,
            unit=line_data.get('unit'),
            vat_rate=float(line_data['vat_rate']) if line_data.get('vat_rate') else None,
            withholding_rate=float(line_data['withholding_rate']) if line_data.get('withholding_rate') else None,
            vat_base=float(line_data['vat_base']) if line_data.get('vat_base') else None
        )
        db.add(line)
    
    return transaction


def generate_transaction_preview(
    db: Session,
    einvoice: EInvoice,
    category_data: dict = None,
    cost_center_id: int = None
) -> dict:
    """
    E-fatura için muhasebe kaydı önizlemesi oluştur (kayıt yapmadan)
    
    YENİ: generate_transaction_lines_from_invoice() kullanarak
    YEVMIYE_KAYDI_SABLONU.md kararlarına göre otomatik satırlar oluşturur.
    
    Args:
        db: Database session
        einvoice: E-fatura kaydı
        category_data: Frontend'ten gelen kategorizasyon verisi (opsiyonel)
        cost_center_id: Maliyet merkezi ID (opsiyonel)
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
        dict: Önizleme verisi (cari, fiş satırları, uyarılar)
    """
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
        # Geçici contact objesi oluştur (önizleme için)
        contact = Contact(
            code=contact_info['code'],
            name=einvoice.supplier_name,
            type='supplier',
            tax_number=einvoice.supplier_tax_number
        )
    
    # 2. Mock transaction objesi (önizleme için ID gerekmiyor)
    transaction = Transaction(
        transaction_number='PREVIEW',
        transaction_date=einvoice.issue_date,
        description=f'{einvoice.supplier_name} - E-Fatura'
    )
    
    # 3. Cost center bilgisini al
    cost_center_name = None
    cost_center_code = None
    if cost_center_id:
        from ..models.cost_center import CostCenter
        cost_center = db.query(CostCenter).filter(CostCenter.id == cost_center_id).first()
        if cost_center:
            cost_center_name = cost_center.name
            cost_center_code = cost_center.code
    
    # Cost center boş geliyorsa varsayılan al
    if not cost_center_id or not cost_center_name:
        from ..models.cost_center import CostCenter
        default_cc = db.query(CostCenter).filter(CostCenter.code == 'MERKEZ').first()
        if default_cc:
            cost_center_name = default_cc.name
            cost_center_code = default_cc.code
            cost_center_id = default_cc.id
    
    # 4. YENİ FONKSİYONU KULLAN: Otomatik satırlar oluştur (kategori mapping ile)
    try:
        raw_lines = generate_transaction_lines_from_invoice(db, einvoice, transaction, contact, category_data, cost_center_id)
    except Exception as e:
        warnings.append(f'❌ Satır oluşturma hatası: {str(e)}')
        # Fallback: Boş satırlar
        raw_lines = []
    
    # 5. Satırları formatlayıp hesap isimleri ekle
    lines = []
    for i, line_data in enumerate(raw_lines, start=1):
        # Hesap adını database'den al
        account = db.query(Account).filter(Account.code == line_data['account_code']).first()
        account_name = account.name if account else line_data.get('description', 'Bilinmiyor')
        
        # Contact ID ve name - HER SATIRDA (cari hesap olsun olmasın)
        contact_id = contact.id if contact and hasattr(contact, 'id') else None
        contact_name = contact.name if contact else None
        
        # Unit - raw_data'dan çekmeye çalış (şimdilik None)
        # TODO: einvoice.raw_data JSON'ından unit bilgisini parse et
        unit = line_data.get('unit') or 'ADET'  # Varsayılan birim
        
        lines.append({
            'line_no': i,
            'account_code': line_data['account_code'],
            'account_name': account_name,
            'contact_id': contact_id,
            'contact_name': contact_name,
            'description': line_data['description'],
            'debit': float(line_data['debit']),
            'credit': float(line_data['credit']),
            'quantity': float(line_data['quantity']) if line_data.get('quantity') else None,
            'unit': unit,
            'vat_rate': float(line_data['vat_rate']) if line_data.get('vat_rate') else None,
            'withholding_rate': float(line_data['withholding_rate']) if line_data.get('withholding_rate') else None,
            'vat_base': float(line_data['vat_base']) if line_data.get('vat_base') else None
        })
        
        # Hesap bulunamazsa uyarı
        if not account:
            warnings.append(f'⚠️  {line_data["account_code"]} hesabı bulunamadı')
    
    # 6. Toplam kontrol
    total_debit = sum(line['debit'] for line in lines)
    total_credit = sum(line['credit'] for line in lines)
    
    if abs(total_debit - total_credit) > 0.01:
        warnings.append(f'❌ Denklik hatası: Borç={total_debit:.2f}, Alacak={total_credit:.2f}')
    
    # 7. Fiş numarası (önizleme için - commit=False)
    next_transaction_number = get_next_transaction_number(db, prefix="F", commit=False)
    db.rollback()  # Numarayı tüketmeyelim
    
    # 8. Belge tipi ve alt tipi - ID ve name döndür
    from ..models.document_type import DocumentType, DocumentSubtype
    
    # Ana evrak türü: ALIS_FATURA (ID=1)
    doc_type = db.query(DocumentType).filter(DocumentType.code == 'ALIS_FATURA').first()
    document_type_id = doc_type.id if doc_type else 1
    document_type_name = doc_type.name if doc_type else 'Alış Faturası'
    
    # Alt evrak türü: invoice_type'a göre
    if einvoice.invoice_type == 'E_ARSIV':
        doc_subtype = db.query(DocumentSubtype).filter(DocumentSubtype.code == 'E_ARSIV').first()
        document_subtype_id = doc_subtype.id if doc_subtype else 2
        document_subtype_name = doc_subtype.name if doc_subtype else 'E-Arşiv'
    else:
        doc_subtype = db.query(DocumentSubtype).filter(DocumentSubtype.code == 'E_FATURA').first()
        document_subtype_id = doc_subtype.id if doc_subtype else 1
        document_subtype_name = doc_subtype.name if doc_subtype else 'E-Fatura'
    
    period = einvoice.issue_date.strftime('%Y-%m')
    
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
            'number': next_transaction_number,
            'date': str(einvoice.issue_date),
            'period': period,
            'document_type_id': document_type_id,
            'document_type': document_type_name,
            'document_subtype_id': document_subtype_id,
            'document_subtype': document_subtype_name,
            'document_number': einvoice.invoice_number,
            'description': f'{einvoice.supplier_name} - {einvoice.invoice_number}',
            'cost_center_id': cost_center_id,
            'cost_center_name': cost_center_name,
            'lines': lines,
            'total_debit': round(total_debit, 2),
            'total_credit': round(total_credit, 2),
            'is_balanced': abs(total_debit - total_credit) < 0.01
        },
        'warnings': warnings,
        'can_import': abs(total_debit - total_credit) < 0.01 and len(lines) > 0
    }


# ============================================================================
# YENİ YARDIMCI FONKSİYONLAR - 2026-01-01
# ============================================================================

from decimal import Decimal

def get_191_account_code(vat_rate: Decimal, has_withholding: bool) -> str:
    """
    KDV oranı ve tevkifat durumuna göre 191 hesap kodunu döndürür.
    
    Args:
        vat_rate: KDV oranı (0.01, 0.08, 0.10, 0.18, 0.20)
        has_withholding: Tevkifat var mı?
    
    Returns:
        str: Hesap kodu (örn: '191.20.001', '191.10.002')
    
    Examples:
        >>> get_191_account_code(Decimal('0.20'), False)
        '191.20001'
        >>> get_191_account_code(Decimal('0.01'), True)
        '191.01002'
    """
    # KDV oranını yüzdelik sayıya çevir (0.20 -> 20)
    vat_pct = int(vat_rate * 100)
    
    # 2 haneli string (1 -> "01", 20 -> "20")
    vat_str = str(vat_pct).zfill(2)
    
    # Tevkifat durumuna göre son 3 hane
    suffix = '002' if has_withholding else '001'
    
    return f"191.{vat_str}{suffix}"


def get_withholding_rate_from_code(withholding_code: str) -> Optional[Decimal]:
    """
    GİB tevkifat kodundan tevkifat oranını döndürür.
    
    Args:
        withholding_code: GİB tevkifat kodu (601-627, 801-825)
    
    Returns:
        Decimal: Tevkifat oranı (0.20 = %20) veya None
    
    Examples:
        >>> get_withholding_rate_from_code('601')  # 4/10
        Decimal('0.40')
        >>> get_withholding_rate_from_code('602')  # 9/10
        Decimal('0.90')
    """
    # GİB tevkifat kodları mapping (şablondan alındı)
    withholding_rates = {
        # 6XX serisi (kısmi tevkifat)
        '601': Decimal('0.40'),  # 4/10
        '602': Decimal('0.90'),  # 9/10
        '603': Decimal('0.70'),  # 7/10
        '604': Decimal('0.50'),  # 5/10
        '605': Decimal('0.50'),  # 5/10
        '606': Decimal('0.90'),  # 9/10
        '607': Decimal('0.90'),  # 9/10
        '608': Decimal('0.90'),  # 9/10
        '609': Decimal('0.70'),  # 7/10
        '610': Decimal('0.90'),  # 9/10
        '611': Decimal('0.90'),  # 9/10
        '612': Decimal('0.90'),  # 9/10
        '613': Decimal('0.90'),  # 9/10
        '614': Decimal('0.50'),  # 5/10
        '615': Decimal('0.70'),  # 7/10
        '616': Decimal('0.50'),  # 5/10
        '617': Decimal('0.70'),  # 7/10
        '618': Decimal('0.70'),  # 7/10
        '619': Decimal('0.70'),  # 7/10
        '620': Decimal('0.70'),  # 7/10
        '621': Decimal('0.90'),  # 9/10
        '622': Decimal('0.90'),  # 9/10
        '623': Decimal('0.50'),  # 5/10
        '624': Decimal('0.20'),  # 2/10
        '625': Decimal('0.30'),  # 3/10
        '626': Decimal('0.20'),  # 2/10
        '627': Decimal('0.50'),  # 5/10
        # 8XX serisi (tam tevkifat - 10/10)
        '801': Decimal('1.00'),  # 10/10
        '802': Decimal('1.00'),
        '803': Decimal('1.00'),
        '804': Decimal('1.00'),
        '805': Decimal('1.00'),
        '806': Decimal('1.00'),
        '807': Decimal('1.00'),
        '808': Decimal('1.00'),
        '809': Decimal('1.00'),
        '810': Decimal('1.00'),
        '811': Decimal('1.00'),
        '812': Decimal('1.00'),
        '813': Decimal('1.00'),
        '814': Decimal('1.00'),
        '815': Decimal('1.00'),
        '816': Decimal('1.00'),
        '817': Decimal('1.00'),
        '818': Decimal('1.00'),
        '819': Decimal('1.00'),
        '820': Decimal('1.00'),
        '821': Decimal('1.00'),
        '822': Decimal('1.00'),
        '823': Decimal('1.00'),
        '824': Decimal('1.00'),
        '825': Decimal('1.00'),
    }
    
    return withholding_rates.get(withholding_code)


def parse_special_taxes_from_invoice(raw_data: dict) -> dict:
    """
    E-fatura XML'inden özel vergileri parse eder (ÖİV, Telsiz, Konaklama).
    
    Args:
        raw_data: einvoices.raw_data JSON veya XML string
    
    Returns:
        dict: {
            'oiv': Decimal,  # Özel İletişim Vergisi (ÖİV) - Tax Code 4081
            'telsiz': Decimal,  # Telsiz Kullanım Ücreti - Tax Code 8006
            'konaklama': Decimal,  # Konaklama Vergisi - Tax Code 4080
            'aracilik': Decimal,  # Tahsilatına Aracılık Edilen - Invoice Line (item_name içinde 'Aracılık')
            'duzeltme': Decimal,  # Düzeltme - Invoice Line (item_name içinde 'Düzeltme')
            'diger_masraflar': List[Dict],  # Diğer masraflar (item_name + amount)
        }
    
    Tax Code Mapping (GIB UBL-TR Standardı):
        - 0015: KDV %20
        - 0061: KDV %10
        - 0071: KDV %1
        - 0073: KDV %8
        - 4080: Konaklama Vergisi
        - 4081: Özel İletişim Vergisi (ÖİV)
        - 8006: Telsiz Kullanım Ücreti
        - 9077: KDV İstisnası
    
    Examples:
        Turkcell faturası:
        - Tarife: 666.15 TL
        - KDV %20 (0015): 133.23 TL
        - ÖİV %10 (4081): 66.62 TL
        - Telsiz (8006): 21.50 TL
        - Aracılık (Invoice Line): 134.00 TL
        - Düzeltme (Invoice Line): -0.05 TL
        - Toplam: 1021.50 TL
    """
    # Varsayılan değerler
    result = {
        'oiv': Decimal('0'),
        'telsiz': Decimal('0'),
        'konaklama': Decimal('0'),
        'aracilik': Decimal('0'),
        'duzeltme': Decimal('0'),
        'diger_masraflar': [],  # [{'description': '...', 'amount': Decimal}]
    }
    
    if not raw_data:
        return result
    
    try:
        # String ise JSON parse et (database'de JSON string olarak saklanmış olabilir)
        if isinstance(raw_data, str):
            import json
            try:
                raw_data = json.loads(raw_data)
            except:
                # JSON değilse XML olabilir
                pass
        
        # Eğer hala string ise (XML), parse et
        if isinstance(raw_data, str):
            import xml.etree.ElementTree as ET
            
            root = ET.fromstring(raw_data)
            ns = {
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
                'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'
            }
            
            # 1. Tax Total'dan özel vergileri parse et
            for tax_total in root.findall('.//cac:TaxTotal', ns):
                for subtotal in tax_total.findall('cac:TaxSubtotal', ns):
                    tax_scheme = subtotal.find('.//cbc:TaxTypeCode', ns)
                    tax_amount = subtotal.find('cbc:TaxAmount', ns)
                    
                    if tax_scheme is not None and tax_amount is not None:
                        tax_code = tax_scheme.text
                        amount = Decimal(str(tax_amount.text))
                        
                        # Tax code mapping
                        if tax_code == '4081':
                            result['oiv'] += amount  # Özel İletişim Vergisi
                        elif tax_code == '8006':
                            result['telsiz'] += amount  # Telsiz Kullanım Ücreti
                        elif tax_code == '4080':
                            result['konaklama'] += amount  # Konaklama Vergisi
            
            # 2. Invoice Line'lardan özel masrafları parse et
            for line in root.findall('.//cac:InvoiceLine', ns):
                item_name_elem = line.find('.//cbc:Name', ns)
                line_amount_elem = line.find('cbc:LineExtensionAmount', ns)
                
                if item_name_elem is not None and line_amount_elem is not None:
                    item_name = item_name_elem.text.lower()
                    line_amount = Decimal(str(line_amount_elem.text))
                    
                    # Özel açıklamalara göre eşleştir
                    if 'aracılık' in item_name or 'araciliki' in item_name:
                        result['aracilik'] += line_amount
                    elif 'düzeltme' in item_name or 'duzeltme' in item_name:
                        result['duzeltme'] += line_amount
                    elif 'diğer ücret' in item_name or 'diger ucret' in item_name:
                        # Diğer masraflar listesine ekle
                        result['diger_masraflar'].append({
                            'description': item_name_elem.text,
                            'amount': line_amount
                        })
        
        # Test verisi için direkt alanları kontrol et (eski uyumluluk)
        elif isinstance(raw_data, dict):
            if 'oiv' in raw_data:
                result['oiv'] = Decimal(str(raw_data['oiv']))
            if 'telsiz' in raw_data:
                result['telsiz'] = Decimal(str(raw_data['telsiz']))
            if 'konaklama' in raw_data:
                result['konaklama'] = Decimal(str(raw_data['konaklama']))
            if 'aracilik' in raw_data:
                result['aracilik'] = Decimal(str(raw_data['aracilik']))
            if 'duzeltme' in raw_data:
                result['duzeltme'] = Decimal(str(raw_data['duzeltme']))
        
    except Exception as e:
        # Parse hatası olursa varsayılan değerleri dön
        import traceback
        print(f"⚠️  parse_special_taxes_from_invoice hatası: {str(e)}")
        traceback.print_exc()
    
    return result


def calculate_invoice_balance_adjustment(total_lines: Decimal, payable_amount: Decimal) -> Decimal:
    """
    Fatura satırları toplamı ile ödenecek tutar arasındaki farkı hesaplar.
    
    Bu fark düzeltme hesabına (679 veya 659) kaydedilir.
    
    Args:
        total_lines: Satırlar toplamı (matrah + KDV + vergiler + ücretler)
        payable_amount: Ödenecek tutar (fatura toplamı)
    
    Returns:
        Decimal: Fark (pozitif ise 659, negatif ise 679)
    
    Examples:
        >>> calculate_invoice_balance_adjustment(Decimal('795.896'), Decimal('795.90'))
        Decimal('0.004')  # 659 hesaba BORÇ (pozitif fark)
        >>> calculate_invoice_balance_adjustment(Decimal('795.90'), Decimal('795.896'))
        Decimal('-0.004')  # 679 hesaba ALACAK (negatif fark)
    """
    return payable_amount - total_lines

def generate_transaction_lines_from_invoice(
    db: Session,
    invoice: EInvoice,
    transaction: Transaction,
    contact: Contact,
    category_data: dict = None,
    cost_center_id: int = None
) -> List[Dict[str, Any]]:
    """
    E-faturadan otomatik yevmiye kayıtları oluşturur.
    
    Kullanıcının YEVMIYE_KAYDI_SABLONU.md'deki kararlarına göre:
    - DETAYLI 191 yapısı (191.XX.00X)
    - TOPLU KDV (oranına göre tek satır)
    - İadeler için 602.00002
    - İstisnalar için 191 yok
    - Özel vergiler (ÖİV, Telsiz, Konaklama)
    - Düzeltmeler (679/659)
    
    Args:
        db: Database session
        invoice: E-fatura kaydı
        transaction: Transaction kaydı
        contact: Cari hesap
        category_data: Frontend'ten gelen kategorizasyon verisi
            {
                "invoice_lines_mapping": [
                    {
                        "line_id": "1",
                        "account_code": "740.00204",
                        "item_name": "..."
                    }
                ]
            }
    
    Returns:
        List[Dict]: transaction_line verileri
        
    Example Output:
        [
            {'account_code': '600.01.001', 'debit': 538.46, 'credit': 0, 'description': 'Tarife'},
            {'account_code': '191.20.001', 'debit': 107.69, 'credit': 0, 'vat_rate': 0.20},
            {'account_code': '689.00001', 'debit': 53.85, 'credit': 0, 'description': 'ÖİV'},
            {'account_code': '689.00005', 'debit': 14.94, 'credit': 0, 'description': 'Telsiz'},
            {'account_code': '360.01.001', 'debit': 0, 'credit': 81.00, 'description': 'Aracılık'},
            {'account_code': '659.00003', 'debit': 0.004, 'credit': 0, 'description': 'Düzeltme'},
            {'account_code': '320.00001', 'debit': 0, 'credit': 795.90, 'description': 'Turkcell'},
        ]
    """
    lines = []
    
    # İade faturası kontrolü (invoice_type alanını kullan)
    is_return = invoice.invoice_type in ['IADE', 'İADE', 'IRSALIYEDENIADE']
    
    # Maliyet merkezi adını al
    cost_center_name = None
    if cost_center_id:
        from app.models.cost_center import CostCenter
        cost_center = db.query(CostCenter).filter(CostCenter.id == cost_center_id).first()
        if cost_center:
            cost_center_name = cost_center.name
    
    # Tevkifat kontrolü
    has_withholding = False
    withholding_code = None
    if invoice.raw_data:
        try:
            raw = json.loads(invoice.raw_data) if isinstance(invoice.raw_data, str) else invoice.raw_data
            # XML'den tevkifat kodunu al (WithholdingTaxTotal/TaxSubtotal/TaxCategory/TaxScheme/TaxTypeCode)
            withholding_code = raw.get('withholding_tax_code')  # Bu alan XML parse edildiğinde eklenir
            has_withholding = withholding_code is not None
        except:
            pass
    
    # Matrah alanı (line_extension_amount veya tax_exclusive_amount)
    matrah = invoice.line_extension_amount or invoice.tax_exclusive_amount or Decimal('0')
    
    # ÖNEMLİ: Önce özel vergileri parse et (aracılık, düzeltme vs. invoice_lines içinde olabilir)
    special_taxes = parse_special_taxes_from_invoice(invoice.raw_data)
    
    # 1. MATRAH SATIRLARI
    # Frontend'ten gelen invoice_lines_mapping'i kullan (XML'i tekrar parse etme!)
    invoice_lines_data = []
    
    # Frontend'ten gelen mapping'i önce kontrol et
    if category_data and 'invoice_lines_mapping' in category_data:
        # Frontend'ten gelen satırları kullan (item_name, line_total vs. zaten var)
        for mapping in category_data['invoice_lines_mapping']:
            invoice_lines_data.append({
                'line_id': mapping.get('line_id', '1'),
                'item_name': mapping.get('item_name', ''),
                'quantity': Decimal(str(mapping.get('quantity', 1))) if mapping.get('quantity') else Decimal('1'),
                'price': Decimal(str(mapping.get('unit_price', 0))) if mapping.get('unit_price') else Decimal('0'),
                'total': Decimal(str(mapping.get('line_total', 0))) if mapping.get('line_total') else Decimal('0')
            })
    
    # Frontend mapping yoksa fallback: XML'den satırları parse et
    if not invoice_lines_data:
        # XML'den invoice lines parse et
        try:
            from ..services.einvoice_xml_service import parse_xml_invoice
            
            # raw_data JSON string ise decode et
            raw_xml = invoice.raw_data
            if isinstance(raw_xml, str):
                try:
                    import json
                    raw_xml = json.loads(raw_xml)
                except:
                    pass  # Zaten XML string
            
            # XML parse et
            if raw_xml:
                # parse_xml_invoice 2 parametre bekliyor: (xml_content, filename)
                # filename sadece error message için kullanılıyor, dummy değer verebiliriz
                invoice_data, errors = parse_xml_invoice(raw_xml, filename=f"{invoice.invoice_number}.xml")
                
                # XML'den gelen lines'ı kullan
                for line in invoice_data.get('lines', []):
                    invoice_lines_data.append({
                        'line_id': line.get('line_id', '1'),
                        'item_name': line.get('item_name', ''),
                        'quantity': line.get('quantity', Decimal('1')),
                        'price': line.get('unit_price', Decimal('0')),
                        'total': line.get('line_amount', Decimal('0'))
                    })
        except Exception as e:
            import traceback
            # XML parse hatası - fallback kullanılacak
            pass
        
        # Hala boşsa tek satır kullan (son fallback)
        if not invoice_lines_data and matrah > 0:
            # tax_exclusive_amount kullan (aracılık, düzeltme vs. olmadan)
            net_matrah = invoice.tax_exclusive_amount or matrah
            invoice_lines_data = [{
                'line_id': '1',
                'item_name': invoice.supplier_name or 'Mal/Hizmet',
                'quantity': Decimal('1'),
                'price': net_matrah,
                'total': net_matrah
            }]
    
    # Frontend'ten gelen hesap mapping'ini hazırla
    line_account_map = {}
    if category_data and 'invoice_lines_mapping' in category_data:
        for mapping in category_data['invoice_lines_mapping']:
            line_id = mapping.get('line_id')
            account_code = mapping.get('account_code')
            if line_id and account_code:
                line_account_map[line_id] = account_code
    
    # Her satır için hesap kodu belirle ve ekle
    for line_data in invoice_lines_data:
        line_id = line_data.get('line_id', '1')
        item_name = line_data['item_name']
        line_total = line_data['total']
        
        # Özel satırları ATLA (bunlar ayrı kategorilerde işlenecek)
        item_name_lower = item_name.lower()
        if any(keyword in item_name_lower for keyword in ['aracılık', 'araciligi', 'düzeltme', 'duzeltme']):
            # Bu satırlar parse_special_taxes_from_invoice ile ayrı işlenecek
            continue
        
        # Önce frontend mapping'den hesap kodu al
        if line_id in line_account_map:
            account_code = line_account_map[line_id]
        else:
            # Frontend mapping yoksa otomatik kategorize et (cost_center'a göre varsayılan)
            category = categorize_invoice_line(item_name)
            account_code = get_account_for_category(category, item_name, cost_center_name)
        
        if is_return:
            # İade: 602.00002 hesaba
            lines.append({
                'account_code': '602.00002',
                'debit': 0,
                'credit': abs(line_total),
                'description': item_name or 'Alıştan İadeler',
                'quantity': line_data.get('quantity'),
                'unit': None,  # Unit bilgisi raw_data'dan gelecek (gelecekte iyileştirilecek)
                'unit_price': line_data.get('price'),
                'vat_rate': None,
                'withholding_rate': None,
                'vat_base': None  # Mal/hizmet satırlarında matrah yok
            })
        else:
            # Normal alış: Kategoriye göre hesap
            lines.append({
                'account_code': account_code,
                'debit': line_total,
                'credit': 0,
                'description': item_name or 'Mal/Hizmet',
                'quantity': line_data.get('quantity'),
                'unit': None,  # Unit bilgisi raw_data'dan gelecek (gelecekte iyileştirilecek)
                'unit_price': line_data.get('price'),
                'vat_rate': None,
                'withholding_rate': None,
                'vat_base': None  # Mal/hizmet satırlarında matrah yok
            })
    
    # 2. KDV SATIRLARI - XML'den direkt al (hesaplama yapma!)
    # İstisna/Muafiyet kontrolü (raw_data'dan)
    is_exempt = False
    vat_amount = Decimal('0')
    vat_rate = Decimal('0.20')  # Varsayılan
    
    if invoice.raw_data:
        try:
            import xml.etree.ElementTree as ET
            raw_xml = invoice.raw_data
            
            # JSON string ise decode et
            if isinstance(raw_xml, str):
                try:
                    import json
                    raw_xml = json.loads(raw_xml)
                except:
                    pass
            
            # XML parse et
            if isinstance(raw_xml, str):
                root = ET.fromstring(raw_xml)
                ns = {
                    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
                    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'
                }
                
                # Tax Code 0015 (KDV) tutarını bul
                for tax_total in root.findall('.//cac:TaxTotal', ns):
                    for subtotal in tax_total.findall('cac:TaxSubtotal', ns):
                        tax_scheme = subtotal.find('.//cbc:TaxTypeCode', ns)
                        tax_amount_elem = subtotal.find('cbc:TaxAmount', ns)
                        percent_elem = subtotal.find('.//cbc:Percent', ns)
                        
                        if tax_scheme is not None and tax_scheme.text == '0015':  # KDV
                            if tax_amount_elem is not None:
                                vat_amount = Decimal(str(tax_amount_elem.text))
                            if percent_elem is not None:
                                vat_rate = Decimal(str(percent_elem.text)) / Decimal('100')
                            break
                    if vat_amount > 0:
                        break
                
                # İstisna kontrolü
                exemption_reason = root.find('.//cbc:TaxExemptionReasonCode', ns)
                if exemption_reason is not None:
                    is_exempt = True
        except:
            # XML parse hatası - fallback: invoice.total_tax_amount kullan
            if invoice.total_tax_amount:
                vat_amount = invoice.total_tax_amount
    
    # KDV tutarı varsa (iade için de negatif tutar olabilir)
    if vat_amount and abs(vat_amount) > 0 and not is_exempt:
        # 191 hesabını belirle
        account_191 = get_191_account_code(vat_rate, has_withholding)
        
        if is_return:
            # İade: 191 ALACAK
            lines.append({
                'account_code': account_191,
                'debit': 0,
                'credit': abs(vat_amount),
                'description': f'İndirilecek KDV %{int(vat_rate*100)}',
                'quantity': vat_rate,  # KDV satırında quantity = KDV oranı
                'unit': None,
                'unit_price': None,
                'vat_rate': vat_rate,
                'withholding_rate': None,
                'vat_base': float(matrah) if matrah else None  # KDV matrahı
            })
        else:
            # Normal: 191 BORÇ
            lines.append({
                'account_code': account_191,
                'debit': abs(vat_amount),
                'credit': 0,
                'description': f'İndirilecek KDV %{int(vat_rate*100)}',
                'quantity': vat_rate,  # KDV satırında quantity = KDV oranı
                'unit': None,
                'unit_price': None,
                'vat_rate': vat_rate,
                'withholding_rate': None,
                'vat_base': float(matrah) if matrah else None  # KDV matrahı
            })
    
    # 3. TEVKİFAT SATIRLARI
    if has_withholding and withholding_code and invoice.withholding_tax_amount:
        withholding_rate = get_withholding_rate_from_code(withholding_code)
        
        # 360.01.001 - Ödenecek Vergi ve Fonlar / KDV Tevkifatı
        lines.append({
            'account_code': '360.01.001',
            'debit': 0,
            'credit': invoice.withholding_tax_amount,
            'description': f'KDV Tevkifatı %{int(withholding_rate*100) if withholding_rate else ""}',
            'quantity': withholding_rate,  # Tevkifat satırında quantity = tevkifat oranı
            'unit': None,
            'unit_price': None,
            'vat_rate': None,
            'withholding_rate': withholding_rate,
            'vat_base': None  # Tevkifat için matrah belirtmeye gerek yok
        })
    
    # 4. ÖZEL VERGİLER (ÖİV, Telsiz, Konaklama) ve MASRAFLAR (Aracılık)
    # special_taxes zaten yukarıda parse edildi
    
    if special_taxes['oiv'] > 0:
        lines.append({
            'account_code': '689.00001',
            'debit': special_taxes['oiv'],
            'credit': 0,
            'description': 'Özel İletişim Vergisi',
            'quantity': None,
            'unit': None,
            'unit_price': None,
            'vat_rate': None,
            'withholding_rate': None,
            'vat_base': None
        })
    
    if special_taxes['telsiz'] > 0:
        lines.append({
            'account_code': '689.00005',
            'debit': special_taxes['telsiz'],
            'credit': 0,
            'description': 'Telsiz Kullanım Ücreti',
            'quantity': None,
            'unit': None,
            'unit_price': None,
            'vat_rate': None,
            'withholding_rate': None,
            'vat_base': None
        })
    
    if special_taxes['konaklama'] > 0:
        lines.append({
            'account_code': '740.00209',
            'debit': special_taxes['konaklama'],
            'credit': 0,
            'description': 'Konaklama Vergisi',
            'quantity': None,
            'unit': None,
            'unit_price': None,
            'vat_rate': None,
            'withholding_rate': None,
            'vat_base': None
        })
    
    if special_taxes['aracilik'] > 0:
        # Aracılık: 689.00005 (Kanunen Kabul Edilmeyen Giderler) BORÇ
        lines.append({
            'account_code': '689.00005',
            'debit': special_taxes['aracilik'],
            'credit': 0,
            'description': 'Tahsilatına Aracılık Edilen',
            'quantity': None,
            'unit': None,
            'unit_price': None,
            'vat_rate': None,
            'withholding_rate': None,
            'vat_base': None
        })
    
    # Diğer masraflar (invoice line'da "Diğer Ücretler" gibi satırlar)
    for masraf in special_taxes.get('diger_masraflar', []):
        if masraf['amount'] > 0:
            lines.append({
                'account_code': '689.00005',  # Diğer Ücretler
                'debit': masraf['amount'],
                'credit': 0,
                'description': masraf['description'],
                'quantity': None,
                'unit': None,
                'unit_price': None,
                'vat_rate': None,
                'withholding_rate': None,
                'vat_base': None
            })
    
    # 5. DÜZELTME (679/659)
    # Not: special_taxes['duzeltme'] invoice line'dan gelebilir ama çoğu zaman
    # fatura dengesi için otomatik hesaplanan düzeltme kullanılır
    
    # Satırlar toplamı ile ödenecek tutar farkı
    total_lines = sum(line['debit'] - line['credit'] for line in lines)
    adjustment = calculate_invoice_balance_adjustment(total_lines, invoice.payable_amount or invoice.total_amount)
    
    # Eğer invoice line'da düzeltme varsa onu da ekle
    if special_taxes.get('duzeltme') and special_taxes['duzeltme'] != Decimal('0'):
        duzeltme_amount = special_taxes['duzeltme']
        if duzeltme_amount > 0:
            # Pozitif: 659 BORÇ
            lines.append({
                'account_code': '659.00003',
                'debit': duzeltme_amount,
                'credit': 0,
                'description': 'Düzeltme',
                'quantity': None,
                'unit': None,
                'unit_price': None,
                'vat_rate': None,
                'withholding_rate': None,
                'vat_base': None
            })
        else:
            # Negatif: 679 ALACAK
            lines.append({
                'account_code': '679.00001',
                'debit': 0,
                'credit': abs(duzeltme_amount),
                'description': 'Düzeltme',
                'quantity': None,
                'unit': None,
                'unit_price': None,
                'vat_rate': None,
                'withholding_rate': None,
                'vat_base': None
            })
        
        # Toplam yeniden hesapla (düzeltme eklendikten sonra)
        total_lines = sum(line['debit'] - line['credit'] for line in lines)
        adjustment = calculate_invoice_balance_adjustment(total_lines, invoice.payable_amount or invoice.total_amount)
    
    # Eğer hala fark varsa, otomatik düzeltme ekle
    if adjustment != Decimal('0'):
        if adjustment > 0:
            # Pozitif fark: 659 BORÇ
            lines.append({
                'account_code': '659.00003',
                'debit': adjustment,
                'credit': 0,
                'description': 'Düzeltme',
                'quantity': None,
                'unit': None,
                'unit_price': None,
                'vat_rate': None,
                'withholding_rate': None,
                'vat_base': None
            })
        else:
            # Negatif fark: 679 ALACAK
            lines.append({
                'account_code': '679.00001',
                'debit': 0,
                'credit': abs(adjustment),
                'description': 'Düzeltme',
                'quantity': None,
                'unit': None,
                'unit_price': None,
                'vat_rate': None,
                'withholding_rate': None,
                'vat_base': None
            })
    
    # 6. CARİ HESAP (320 veya 120)
    account_cari = contact.code or ('320.00001' if contact.type == 'supplier' else '120.00001')
    
    if is_return:
        # İade: Cari BORÇ (pozitif tutar)
        lines.append({
            'account_code': account_cari,
            'debit': abs(invoice.payable_amount or invoice.total_amount),
            'credit': 0,
            'description': contact.name or 'Cari',
            'quantity': None,
            'unit': None,
            'unit_price': None,
            'vat_rate': None,
            'withholding_rate': None,
            'vat_base': None
        })
    else:
        # Normal: Cari ALACAK
        lines.append({
            'account_code': account_cari,
            'debit': 0,
            'credit': abs(invoice.payable_amount or invoice.total_amount),
            'description': contact.name or 'Cari',
            'quantity': None,
            'unit': None,
            'unit_price': None,
            'vat_rate': None,
            'withholding_rate': None,
            'vat_base': None
        })
    
    return lines