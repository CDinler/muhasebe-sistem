"""
Contact model - Cari hesaplar
Luca-compatible: contacts table
"""
from sqlalchemy import Column, Integer, String, Boolean, Numeric, Text, Date
from app.core.database import Base


class Contact(Base):
    """Cari hesap (Müşteri/Tedarikçi)"""
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=True, index=True)  # Otomatik cari kodu (320.00001)
    name = Column(String(200), nullable=False, index=True)  # EVRAK UNVAN
    tax_number = Column(String(20), unique=True, nullable=True, index=True)  # VKN/TCKN
    tax_office = Column(String(100), nullable=True)  # VERGİ DAİRESİ
    
    contact_type = Column(String(50), default="Tedarikçi")  # Tedarikçi, Taşeron, Ana Firma, İş Ortağı
    is_active = Column(Boolean, default=True)
    
    # İletişim Bilgileri
    phone = Column(String(50), nullable=True)
    phone2 = Column(String(50), nullable=True)  # Alternatif telefon
    email = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    postal_code = Column(String(10), nullable=True)
    country = Column(String(100), default='TÜRKİYE')
    
    # Fatura Adresi (Farklı ise)
    invoice_address = Column(String(500), nullable=True)
    invoice_city = Column(String(100), nullable=True)
    invoice_district = Column(String(100), nullable=True)
    
    # Yetkili Kişi Bilgileri
    contact_person = Column(String(200), nullable=True)  # Yetkili adı
    contact_person_phone = Column(String(50), nullable=True)
    contact_person_email = Column(String(100), nullable=True)
    contact_person_title = Column(String(100), nullable=True)  # Ünvan (Müdür, Mali Müşavir vs.)
    
    # İş Bilgileri
    sector = Column(String(100), nullable=True)  # Sektör (İnşaat, Gıda vs.)
    region = Column(String(100), nullable=True)  # Bölge/Grup
    customer_group = Column(String(100), nullable=True)  # Müşteri grubu
    
    # Finansal Bilgiler
    risk_limit = Column(Numeric(18, 2), default=0)  # Risk limiti (TL)
    payment_term_days = Column(Integer, default=0)  # Vade günü (0=Peşin, 30=30 gün vade)
    payment_method = Column(String(50), default='Havale')  # Nakit, Çek, Havale, Kredi Kartı
    discount_rate = Column(Numeric(5, 2), default=0)  # İskonto oranı (%)
    
    # Banka Bilgileri
    bank_name = Column(String(100), nullable=True)
    bank_branch = Column(String(100), nullable=True)
    bank_account_no = Column(String(50), nullable=True)
    iban = Column(String(34), nullable=True)
    swift = Column(String(11), nullable=True)
    
    # Bakiye (Hesaplanan - salt okunur olmalı)
    current_balance = Column(Numeric(18, 2), default=0)  # Güncel bakiye (+ Alacak, - Borç)
    
    # Notlar
    notes = Column(Text, nullable=True)  # Genel notlar
    private_notes = Column(Text, nullable=True)  # Özel notlar (gizli)
    
    # Tarihler
    first_transaction_date = Column(Date, nullable=True)  # İlk işlem tarihi
    last_transaction_date = Column(Date, nullable=True)  # Son işlem tarihi
    
    # Sistem
    manually_edited = Column(Boolean, default=False)  # Manuel düzeltme yapıldı mı?
    
    def __repr__(self):
        return f"<Contact {self.code} - {self.name}>"
