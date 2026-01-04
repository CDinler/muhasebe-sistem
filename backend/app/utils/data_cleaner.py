"""Veri temizleme ve standardizasyon fonksiyonları"""
import re
from typing import Optional


def clean_company_name(name: Optional[str]) -> str:
    """
    Firma/şahıs ünvanını temizle ve standartlaştır
    
    Örnek:
    "  abc  inşaat   a.ş.  " → "ABC İNŞAAT A.Ş."
    "ABC INSAAT AS" → "ABC İNŞAAT A.Ş."
    """
    if not name:
        return "Bilinmiyor"
    
    # Başta/sonda boşluk temizle
    name = name.strip()
    
    # Çift/fazla boşlukları tek yap
    name = re.sub(r'\s+', ' ', name)
    
    # Büyük harfe çevir
    name = name.upper()
    
    # Türkçe karakter düzeltmeleri (yaygın hatalar)
    replacements = {
        'I': 'İ',  # İNŞAAT için
        'INSAAT': 'İNŞAAT',
        'MUHENDISLIK': 'MÜHENDİSLİK',
        'TICARET': 'TİCARET',
        'SIRKETI': 'ŞİRKETİ',
        'SIRKETI': 'ŞİRKETİ',
        'AS': 'A.Ş.',
        'A.S.': 'A.Ş.',
        'A S ': 'A.Ş. ',
        'LTD': 'LTD.',
        'STI': 'ŞTİ.',
        'LIMITED': 'LİMİTED',
        'SIRKET': 'ŞİRKET',
    }
    
    for old, new in replacements.items():
        name = name.replace(old, new)
    
    return name


def clean_tax_number(tax_number: Optional[str]) -> Optional[str]:
    """
    Vergi/TC kimlik numarasını temizle
    
    Örnek:
    "  123 456 7890  " → "1234567890"
    "123-456-7890" → "1234567890"
    """
    if not tax_number:
        return None
    
    # Sadece rakamları al
    cleaned = re.sub(r'[^0-9]', '', str(tax_number))
    
    # Boşsa None dön
    return cleaned if cleaned else None


def clean_phone(phone: Optional[str]) -> Optional[str]:
    """
    Telefon numarasını temizle
    
    Örnek:
    "+90 (555) 123-4567" → "05551234567"
    "0 555 123 45 67" → "05551234567"
    """
    if not phone:
        return None
    
    # Sadece rakamları al
    cleaned = re.sub(r'[^0-9]', '', str(phone))
    
    # Başındaki 90 varsa kaldır (uluslararası kod)
    if cleaned.startswith('90') and len(cleaned) == 12:
        cleaned = '0' + cleaned[2:]
    
    return cleaned if cleaned else None


def clean_email(email: Optional[str]) -> Optional[str]:
    """E-posta adresini temizle (küçük harf, boşluk temizle)"""
    if not email:
        return None
    
    # Küçük harfe çevir ve boşlukları temizle
    cleaned = email.strip().lower()
    
    # Basit email validasyonu
    if '@' in cleaned and '.' in cleaned:
        return cleaned
    
    return None


def clean_iban(iban: Optional[str]) -> Optional[str]:
    """
    IBAN'ı temizle ve standartlaştır
    
    Örnek:
    "TR00 0000 0000 0000 0000 0000 00" → "TR000000000000000000000000"
    "tr00-0000-0000" → "TR000000000000000000000000"
    """
    if not iban:
        return None
    
    # Boşluk ve tire temizle, büyük harf
    cleaned = re.sub(r'[\s\-]', '', str(iban)).upper()
    
    # TR ile başlamalı ve 26 karakter olmalı
    if cleaned.startswith('TR') and len(cleaned) == 26:
        return cleaned
    
    return None


def clean_address(address: Optional[str]) -> Optional[str]:
    """Adres temizle (çift boşluk, yeni satır düzenle)"""
    if not address:
        return None
    
    # Başta/sonda boşluk
    address = address.strip()
    
    # Çift boşluk
    address = re.sub(r'\s+', ' ', address)
    
    # Yeni satırları düzenle
    address = address.replace('\r\n', '\n').replace('\r', '\n')
    
    return address


def extract_iban_from_text(text: Optional[str]) -> Optional[str]:
    """
    Metin içinden IBAN numarasını çıkar
    
    NOTLAR sütununda "TR75 0020 6000 8704 7459 5400 01" gibi
    IBAN bilgileri olabilir. Bu fonksiyon metni tarayıp ilk
    geçerli IBAN'ı döndürür.
    
    Örnek metin:
    "HESAP NUMARASI : TR75 0020 6000 8704 7459 5400 01 - TRY - TÜRKİYE FİNANS"
    → "TR750020600087047459540001"
    
    Args:
        text: IBAN içerebilecek metin
        
    Returns:
        Bulunursa temizlenmiş IBAN (26 karakter), bulunamazsa None
    """
    if not text or not isinstance(text, str):
        return None
    
    # TR ile başlayan ve ardından rakamlar/boşluklar gelen pattern
    # IBAN formatı: TR + 2 rakam kontrol + 5 rakam banka + 1 rakam reserved + 16 rakam hesap
    # Toplam: TR + 24 rakam = 26 karakter
    
    # Önce metni büyük harfe çevir
    text_upper = text.upper()
    
    # TR ile başlayan ve sonrasında rakam/boşluk/tire olan kısımları bul
    # En az 26 karakter (boşluklar dahil daha uzun olabilir)
    pattern = r'TR[\s\-]?\d{2}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{2}'
    
    matches = re.findall(pattern, text_upper)
    
    if matches:
        # İlk eşleşmeyi al ve temizle
        iban = matches[0]
        # Boşluk ve tire kaldır
        iban = re.sub(r'[\s\-]', '', iban)
        
        # 26 karakter kontrolü
        if len(iban) == 26:
            return iban
    
    return None

