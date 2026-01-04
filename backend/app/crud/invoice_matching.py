"""
CRUD operations for invoice-payment matching
Fatura-Ödeme Eşleştirme İşlemleri
"""
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_
from datetime import datetime, timedelta
import re
import pandas as pd
from typing import List, Dict, Any, Optional


def extract_invoice_number_from_text(text: str) -> List[str]:
    """Açıklama metninden fatura numarası çıkar"""
    if not text:
        return []
    
    patterns = [
        r'([A-Z]{3}\d{13})',  # ABC1234567890123 (13 digit)
        r'([A-Z]{3}\d{12})',  # ABC123456789012 (12 digit)
        r'([A-Z]{3}\d{10})',  # ABC1234567890 (10 digit)
        r'([A-Z]{2,4}\d{4}[\d]{6,})',  # OSE2025000016671 gibi
        r'(\d{16})',  # 1234567890123456 (16 digit sayısal)
    ]
    
    found = []
    text_upper = text.upper()
    
    for pattern in patterns:
        matches = re.findall(pattern, text_upper)
        found.extend(matches)
    
    return list(set(found))  # Unique values


def extract_dates_from_text(text: str) -> List[datetime]:
    """Açıklama metninden tarih çıkar"""
    if not text:
        return []
    
    patterns = [
        r'(\d{2})[./](\d{2})[./](\d{4})',  # DD.MM.YYYY veya DD/MM/YYYY
        r'(\d{4})[/-](\d{2})[/-](\d{2})',  # YYYY-MM-DD
    ]
    
    found = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                if len(match[0]) == 4:  # YYYY-MM-DD
                    date_obj = datetime(int(match[0]), int(match[1]), int(match[2]))
                else:  # DD.MM.YYYY
                    date_obj = datetime(int(match[2]), int(match[1]), int(match[0]))
                found.append(date_obj)
            except ValueError:
                continue
    
    return list(set(found))


def calculate_match_score(
    payment: Dict[str, Any],
    invoice: Dict[str, Any]
) -> Dict[str, Any]:
    """
    YENİ SKORLAMA SİSTEMİ - Cari ve tutar bazlı eşleştirme
    
    Mantık:
    1. CARİ EŞLEŞMEK ZORUNLU - Farklı firma ise score = 0
    2. TUTAR EŞLEŞMEK ZORUNLU (±%1 tolerans) - Farklı tutar ise score = 0
    3. TARİH FARKLARINA GÖRE SKORLAMA:
       - ±10 gün: 100 puan (kesin eşleşme)
       - ±20 gün: 90 puan
       - ±30 gün: 85 puan
       - ±60 gün: 80 puan (2 ay tolerans)
       - >60 gün: 70 puan (şüpheli)
    4. BONUS: Açıklamada fatura numarası varsa +10 puan
    
    Maksimum: 110 puan
    """
    from datetime import datetime
    
    reasons = []
    
    # Payment bilgileri
    payment_amount = float(payment.get('amount', 0))
    payment_date_str = payment.get('date')
    payment_desc = payment.get('description', '')
    payment_contact_tax = payment.get('contact_tax_number')
    
    # Invoice bilgileri
    invoice_amount = float(invoice.get('payable_amount', 0))
    invoice_date_str = invoice.get('invoice_date')
    invoice_number = invoice.get('invoice_number', '')
    invoice_supplier_tax = invoice.get('supplier_tax_number')
    invoice_customer_tax = invoice.get('customer_tax_number')
    
    # Tarihleri datetime.date objesine çevir
    payment_date = None
    invoice_date = None
    
    if payment_date_str:
        if isinstance(payment_date_str, str):
            payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
        elif hasattr(payment_date_str, 'date'):
            payment_date = payment_date_str.date() if callable(getattr(payment_date_str, 'date')) else payment_date_str
        else:
            payment_date = payment_date_str
    
    if invoice_date_str:
        if isinstance(invoice_date_str, str):
            invoice_date = datetime.strptime(invoice_date_str, '%Y-%m-%d').date()
        elif hasattr(invoice_date_str, 'date'):
            invoice_date = invoice_date_str.date() if callable(getattr(invoice_date_str, 'date')) else invoice_date_str
        else:
            invoice_date = invoice_date_str
    
    # 1. CARİ KONTROL - ZORUNLU
    if not payment_contact_tax:
        return {
            'score': 0,
            'reasons': ['❌ Ödeme kaydında cari bilgisi yok'],
            'invoice_numbers_in_desc': [],
            'dates_in_desc': []
        }
    
    cari_match = (payment_contact_tax == invoice_supplier_tax or 
                  payment_contact_tax == invoice_customer_tax)
    
    if not cari_match:
        return {
            'score': 0,
            'reasons': [f'❌ Cari eşleşmedi (Ödeme: {payment_contact_tax}, Fatura: {invoice_supplier_tax})'],
            'invoice_numbers_in_desc': [],
            'dates_in_desc': []
        }
    
    reasons.append('✓ Cari eşleşti')
    
    # 2. TUTAR KONTROL - ZORUNLU (±%1 tolerans)
    if invoice_amount == 0:
        return {
            'score': 0,
            'reasons': reasons + ['❌ Fatura tutarı 0'],
            'invoice_numbers_in_desc': [],
            'dates_in_desc': []
        }
    
    diff_percent = abs(payment_amount - invoice_amount) / invoice_amount * 100
    
    if diff_percent > 1.0:
        return {
            'score': 0,
            'reasons': reasons + [f'❌ Tutar farkı çok yüksek (%{diff_percent:.2f})'],
            'invoice_numbers_in_desc': [],
            'dates_in_desc': []
        }
    
    reasons.append(f'✓ Tutar eşleşti (Fark: %{diff_percent:.2f})')
    
    # 3. TARİH FARKLARINA GÖRE SKORLAMA
    score = 0
    
    if not payment_date or not invoice_date:
        score = 75  # Tarih bilgisi eksik ama cari+tutar eşleşti
        reasons.append('⚠️ Tarih bilgisi eksik')
    else:
        days_diff = abs((payment_date - invoice_date).days)
        
        if days_diff <= 10:
            score = 100
            reasons.append(f'✓ Tarih mükemmel (±{days_diff} gün)')
        elif days_diff <= 20:
            score = 90
            reasons.append(f'✓ Tarih çok iyi (±{days_diff} gün)')
        elif days_diff <= 30:
            score = 85
            reasons.append(f'✓ Tarih iyi (±{days_diff} gün)')
        elif days_diff <= 60:
            score = 80
            reasons.append(f'⚠️ Tarih makul (±{days_diff} gün)')
        else:
            score = 70
            reasons.append(f'⚠️ Tarih uzak (±{days_diff} gün)')
    
    # 4. BONUS: Açıklamada fatura numarası varsa +10 puan → TAM EŞLEŞME
    desc_invoice_numbers = extract_invoice_number_from_text(payment_desc)
    desc_dates = extract_dates_from_text(payment_desc)
    
    if desc_invoice_numbers:
        for desc_inv in desc_invoice_numbers:
            if desc_inv.upper() == invoice_number.upper():
                # TAM EŞLEŞME: Cari + Tutar + Fatura No
                score = 100
                reasons.insert(0, f'🎯 TAM EŞLEŞME: Fatura no açıklamada ({desc_inv})')
                break
    
    return {
        'score': score,
        'reasons': reasons,
        'invoice_numbers_in_desc': desc_invoice_numbers,
        'dates_in_desc': [d.strftime('%Y-%m-%d') for d in desc_dates]
    }


def get_matching_suggestions(
    db: Session,
    min_score: int = 60,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Eşleştirme önerilerini getir
    
    Args:
        db: Database session
        min_score: Minimum skor (default: 60 - MEDIUM confidence)
        limit: Maksimum sonuç sayısı
        
    Returns:
        Liste of {payment, invoice, score, reasons, confidence}
    """
    
    # Ödemeler - Basit ve hızlı: 320 veya 102 satırlarını al
    # 320 credit = Cari bilgisi + tutar
    # 102 debit = Banka ödemesi (şimdilik 320 kullanıyoruz, daha hızlı)
    payment_query = text("""
        SELECT DISTINCT
            t.id as transaction_id,
            t.transaction_number,
            t.transaction_date,
            COALESCE(tl.description, t.description) as description,
            t.related_invoice_number,
            tl.contact_id,
            c.tax_number as contact_tax_number,
            ABS(tl.credit) as amount,
            a.code as account_code
        FROM transactions t
        JOIN transaction_lines tl ON t.id = tl.transaction_id
        JOIN accounts a ON tl.account_id = a.id
        LEFT JOIN contacts c ON tl.contact_id = c.id
        JOIN einvoices e ON (
            c.tax_number = e.supplier_tax_number
            AND ABS(ABS(tl.credit) - e.payable_amount) / e.payable_amount <= 0.01
            AND e.issue_date >= '2025-11-01'
            AND e.invoice_category = 'incoming'
            AND e.supplier_name IS NOT NULL
            AND e.transaction_id IS NULL
        )
        WHERE 
            YEAR(t.transaction_date) = 2025
            AND a.code LIKE '320%'
            AND tl.credit > 0
            AND t.related_invoice_number IS NULL
            AND tl.contact_id IS NOT NULL
            AND c.tax_number IS NOT NULL
            AND c.tax_number != ''
        ORDER BY t.transaction_date
        LIMIT 100
    """)
    
    payments = db.execute(payment_query).mappings().all()
    
    # Faturalar (Kasım 2025+)
    # SADECE supplier_name dolu olanları getir (kalite kontrol)
    invoice_query = text("""
        SELECT 
            id,
            invoice_number,
            issue_date as invoice_date,
            payable_amount,
            supplier_tax_number,
            customer_tax_number,
            supplier_name,
            transaction_id
        FROM einvoices
        WHERE 
            issue_date >= '2025-11-01'
            AND invoice_category = 'incoming'
            AND supplier_name IS NOT NULL
            AND supplier_name != ''
            AND transaction_id IS NULL
        ORDER BY issue_date DESC
    """)
    
    invoices = db.execute(invoice_query).mappings().all()
    
    # Eşleştirme hesapla
    suggestions = []
    
    for payment in payments:
        payment_dict = {
            'transaction_id': payment['transaction_id'],
            'transaction_number': payment['transaction_number'],
            'date': payment['transaction_date'].strftime('%Y-%m-%d') if payment['transaction_date'] else None,
            'description': payment['description'],
            'contact_tax_number': payment['contact_tax_number'],
            'amount': float(payment['amount']) if payment['amount'] else 0,
            'bank_account': payment['bank_account']
        }
        
        for invoice in invoices:
            invoice_dict = {
                'id': invoice['id'],
                'invoice_number': invoice['invoice_number'],
                'invoice_date': invoice['invoice_date'].strftime('%Y-%m-%d') if invoice['invoice_date'] else None,
                'payable_amount': float(invoice['payable_amount']) if invoice['payable_amount'] else 0,
                'supplier_tax_number': invoice['supplier_tax_number'],
                'customer_tax_number': invoice['customer_tax_number'],
                'supplier_title': invoice['supplier_name'],
                'transaction_id': invoice['transaction_id']
            }
            
            match_result = calculate_match_score(payment_dict, invoice_dict)
            
            if match_result['score'] >= min_score:
                # Confidence level - YENİ SKORLAMA SİSTEMİ
                if match_result['score'] >= 100:
                    confidence = 'HIGH'  # Kesin eşleşme
                elif match_result['score'] >= 85:
                    confidence = 'MEDIUM'  # Çok güçlü
                else:
                    confidence = 'LOW'  # Güçlü ama kesin değil
                
                suggestions.append({
                    'payment': payment_dict,
                    'invoice': invoice_dict,
                    'score': match_result['score'],
                    'reasons': match_result['reasons'],
                    'confidence': confidence,
                    'invoice_numbers_in_desc': match_result['invoice_numbers_in_desc'],
                    'dates_in_desc': match_result['dates_in_desc']
                })
    
    # Skora göre sırala
    suggestions.sort(key=lambda x: x['score'], reverse=True)
    
    return suggestions[:limit]


def apply_automatic_matching(db: Session, min_score: int = 80) -> Dict[str, Any]:
    """
    Yüksek skorlu eşleştirmeleri otomatik uygula (≥80 puan)
    
    Returns:
        {
            'matched_count': int,
            'matches': [{'transaction_id', 'invoice_number', 'score'}]
        }
    """
    suggestions = get_matching_suggestions(db, min_score=min_score, limit=500)
    
    matched = []
    
    for suggestion in suggestions:
        transaction_id = suggestion['payment']['transaction_id']
        invoice_number = suggestion['invoice']['invoice_number']
        current_related = db.execute(
            text("SELECT related_invoice_number FROM transactions WHERE id = :tid"),
            {'tid': transaction_id}
        ).scalar()
        
        # Mevcut related_invoice_number'a ekle (virgülle ayrılmış)
        if current_related:
            invoice_numbers = [num.strip() for num in current_related.split(',')]
            if invoice_number not in invoice_numbers:
                invoice_numbers.append(invoice_number)
                new_value = ','.join(invoice_numbers)
            else:
                continue  # Zaten ekli
        else:
            new_value = invoice_number
        
        # Güncelle
        db.execute(
            text("""
                UPDATE transactions 
                SET related_invoice_number = :inv_num
                WHERE id = :tid
            """),
            {'inv_num': new_value, 'tid': transaction_id}
        )
        
        matched.append({
            'transaction_id': transaction_id,
            'transaction_number': suggestion['payment']['transaction_number'],
            'invoice_number': invoice_number,
            'score': suggestion['score']
        })
    
    db.commit()
    
    return {
        'matched_count': len(matched),
        'matches': matched
    }


def approve_match(
    db: Session,
    transaction_id: int,
    invoice_number: str
) -> Dict[str, Any]:
    """Manuel olarak bir eşleştirmeyi onayla"""
    
    # Mevcut değeri al
    current = db.execute(
        text("SELECT related_invoice_number FROM transactions WHERE id = :tid"),
        {'tid': transaction_id}
    ).scalar()
    
    # Ekle (virgülle ayrılmış)
    if current:
        invoice_numbers = [num.strip() for num in current.split(',')]
        if invoice_number not in invoice_numbers:
            invoice_numbers.append(invoice_number)
            new_value = ','.join(invoice_numbers)
        else:
            return {'success': False, 'message': 'Bu fatura zaten ekli'}
    else:
        new_value = invoice_number
    
    # Güncelle
    db.execute(
        text("""
            UPDATE transactions 
            SET related_invoice_number = :inv_num
            WHERE id = :tid
        """),
        {'inv_num': new_value, 'tid': transaction_id}
    )
    
    db.commit()
    
    return {
        'success': True,
        'transaction_id': transaction_id,
        'related_invoice_number': new_value
    }


def reject_match(
    db: Session,
    transaction_id: int,
    invoice_number: str
) -> Dict[str, Any]:
    """Bir eşleştirme önerisini reddet (hiçbir şey yapma, sadece log)"""
    return {
        'success': True,
        'message': 'Öneri reddedildi',
        'transaction_id': transaction_id,
        'invoice_number': invoice_number
    }


def update_related_invoices(
    db: Session,
    transaction_id: int,
    invoice_numbers: str
) -> Dict[str, Any]:
    """
    Manuel olarak related_invoice_number güncelle
    
    Args:
        invoice_numbers: Virgülle ayrılmış fatura numaraları (örn: "ABC123,DEF456")
    """
    
    # Boşsa NULL yap
    value = invoice_numbers.strip() if invoice_numbers else None
    
    db.execute(
        text("""
            UPDATE transactions 
            SET related_invoice_number = :inv_num
            WHERE id = :tid
        """),
        {'inv_num': value, 'tid': transaction_id}
    )
    
    db.commit()
    
    return {
        'success': True,
        'transaction_id': transaction_id,
        'related_invoice_number': value
    }

