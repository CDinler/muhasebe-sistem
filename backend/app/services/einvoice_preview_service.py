"""
E-Fatura XML Preview/Validation Service

Yükleme öncesi analiz yapar:
- VKN eşleşme kontrolü
- Yeni cari tespiti
- Benzer isimli cari önerileri
- Başarı oranı tahmini
"""

from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import Dict, List, Tuple
from difflib import SequenceMatcher

from app.models.contact import Contact


def clean_company_name_for_match(name: str) -> str:
    """Şirket ismini eşleştirme için temizle"""
    if not name:
        return ""
    
    # Küçük harfe çevir
    name = name.lower()
    
    # Yaygın şirket uzantılarını kaldır
    removals = [
        'a.ş.', 'a.ş', 'as', 'anonim şirketi', 'anonim sirketi',
        'ltd.', 'ltd', 'ltd.şti.', 'ltd.sti.', 'limited şirketi', 'limited sirketi',
        'san.', 'tic.', 'san.tic.', 'sanayi', 'ticaret',
        've', 'dış', 'iç', 'pazarlama', 'ithalat', 'ihracat'
    ]
    
    for removal in removals:
        name = name.replace(removal, '')
    
    # Fazla boşlukları temizle
    name = ' '.join(name.split())
    
    return name.strip()


def calculate_similarity(str1: str, str2: str) -> float:
    """İki string arasındaki benzerlik oranını hesapla (0-1)"""
    return SequenceMatcher(None, str1, str2).ratio()


def find_contact_by_vkn(db: Session, vkn: str) -> Tuple[Contact, str]:
    """
    VKN ile cari bul
    
    Returns:
        (contact, match_type) tuple
        match_type: 'exact', 'not_found'
    """
    if not vkn:
        return None, 'not_found'
    
    # VKN'yi temizle
    clean_vkn = vkn.replace('.', '').replace(' ', '').strip()
    
    # Numeric karşılaştırma
    try:
        contact = db.execute(text("""
            SELECT * FROM contacts 
            WHERE CAST(tax_number AS UNSIGNED) = CAST(:vkn AS UNSIGNED)
            LIMIT 1
        """), {"vkn": clean_vkn}).first()
        
        if contact:
            # Contact object'e dönüştür
            contact_obj = db.query(Contact).filter(Contact.id == contact.id).first()
            return contact_obj, 'exact'
    except:
        pass
    
    return None, 'not_found'


def find_similar_contacts_by_name(db: Session, name: str, limit: int = 5) -> List[Dict]:
    """
    İsme göre benzer cariler bul
    
    Returns:
        List of {id, code, name, tax_number, similarity}
    """
    if not name or len(name) < 3:
        return []
    
    # İsmi temizle
    clean_name = clean_company_name_for_match(name)
    
    # Tüm aktif carileri al (SUPPLIER, CUSTOMER, both)
    contacts = db.query(Contact).filter(
        Contact.contact_type.in_(['SUPPLIER', 'CUSTOMER', 'both']),
        Contact.is_active == True
    ).all()
    
    # Benzerlik hesapla
    matches = []
    for contact in contacts:
        contact_clean_name = clean_company_name_for_match(contact.name)
        similarity = calculate_similarity(clean_name, contact_clean_name)
        
        # En az %60 benzerlik
        if similarity >= 0.6:
            matches.append({
                'id': contact.id,
                'code': contact.code,
                'name': contact.name,
                'tax_number': contact.tax_number,
                'similarity': round(similarity, 2)
            })
    
    # Benzerliğe göre sırala
    matches.sort(key=lambda x: x['similarity'], reverse=True)
    
    return matches[:limit]


def preview_xml_invoices(db: Session, invoices_data: List[Dict]) -> Dict:
    """
    XML faturalarını analiz et, hiçbir şey kaydetme
    
    Args:
        invoices_data: parse_xml_invoice'den dönen invoice_data list'i
    
    Returns:
        {
            'total_files': 50,
            'summary': {...},
            'details': [...],
            'success_estimate': '90%'
        }
    """
    total = len(invoices_data)
    
    matched_count = 0
    new_contact_count = 0
    missing_vkn_count = 0
    possible_match_count = 0
    
    details = []
    
    for invoice_data in invoices_data:
        filename = invoice_data.get('source_file', 'Unknown')
        invoice_number = invoice_data.get('invoice_number')
        invoice_category = invoice_data.get('invoice_category', 'incoming')
        
        # GELEN vs GİDEN FATURA - doğru tarafa bak
        if 'incoming' in invoice_category:
            # Gelen fatura → Supplier cari olacak
            contact_vkn = invoice_data.get('supplier_tax_number')
            contact_name = invoice_data.get('supplier_name')
            contact_type = 'SUPPLIER'
        else:
            # Giden fatura → Customer cari olacak
            contact_vkn = invoice_data.get('customer_tax_number')
            contact_name = invoice_data.get('customer_name')
            contact_type = 'CUSTOMER'
        
        detail = {
            'filename': filename,
            'invoice_number': invoice_number,
            'supplier_name': contact_name,
            'supplier_vkn': contact_vkn,
            'invoice_type': 'Gelen' if 'incoming' in invoice_category else 'Giden',
        }
        
        # VKN var mı?
        if contact_vkn:
            # VKN ile ara
            contact, match_type = find_contact_by_vkn(db, contact_vkn)
            
            if contact:
                # ✅ Eşleşti
                detail['status'] = 'matched'
                detail['contact_id'] = contact.id
                detail['contact_code'] = contact.code
                detail['contact_name'] = contact.name
                matched_count += 1
            else:
                # ➕ Yeni cari eklenecek
                detail['status'] = 'new_contact'
                detail['will_create'] = True
                detail['contact_type'] = contact_type
                new_contact_count += 1
                
                # Benzer isimli var mı kontrol et
                if contact_name:
                    similar = find_similar_contacts_by_name(db, contact_name, limit=3)
                    if similar:
                        detail['possible_matches'] = similar
                        detail['has_similar'] = True
                        possible_match_count += 1
        
        else:
            # ⚠️ VKN yok
            detail['status'] = 'missing_vkn'
            detail['warning'] = 'VKN bulunamadı'
            missing_vkn_count += 1
            
            # İsme göre benzer ara
            if contact_name:
                similar = find_similar_contacts_by_name(db, contact_name, limit=5)
                if similar:
                    detail['possible_matches'] = similar
                    detail['needs_user_selection'] = True
                    possible_match_count += 1
        
        details.append(detail)
    
    # Başarı tahmini
    success_rate = ((matched_count + new_contact_count) / total * 100) if total > 0 else 0
    
    return {
        'total_files': total,
        'summary': {
            'matched_contacts': matched_count,
            'new_contacts': new_contact_count,
            'missing_vkn': missing_vkn_count,
            'possible_matches': possible_match_count,
        },
        'details': details,
        'success_estimate': f'{success_rate:.0f}%',
        'ready_to_import': matched_count + new_contact_count,
        'needs_attention': missing_vkn_count + possible_match_count,
    }
