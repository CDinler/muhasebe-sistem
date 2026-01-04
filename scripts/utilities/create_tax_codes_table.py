"""
Vergi Kodları Referans Tablosunu Oluştur ve Doldur
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from sqlalchemy import create_engine, inspect
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.tax_code import TaxCode

# UBL-TR V1.40 Resmi Vergi Kodları
TAX_CODES_DATA = [
    # VERGİ KODLARI LİSTESİ
    ('0003', 'Gelir Vergisi Stopajı', 'GV STOPAJI', False),
    ('0011', 'Kurumlar Vergisi Stopajı', 'KV STOPAJI', False),
    ('0015', 'Gerçek Usulde Katma Değer Vergisi', 'KDV GERCEK', False),
    ('0021', 'Banka Muameleleri Vergisi', 'BMV', False),
    ('0022', 'Sigorta Muameleleri Vergisi', 'SMV', False),
    ('0059', 'Konaklama Vergisi', 'KONAKLAMA', False),
    ('0061', 'Kaynak Kullanımı Destekleme Fonu Kesintisi', 'KKDF KESİNTİ', False),
    ('0071', 'Petrol Ve Doğalgaz Ürünlerine İlişkin Özel Tüketim Vergisi', 'ÖTV 1.LİSTE', False),
    ('0073', 'Kolalı Gazoz, Alkollü İçeçekler Ve Tütün Mamüllerine İlişkin Özel Tüketim Vergisi', 'ÖTV 3.LİSTE', False),
    ('0074', 'Dayanıklı Tüketim Ve Diğer Mallara İlişkin Özel Tüketim Vergisi', 'ÖTV 4.LİSTE', False),
    ('0075', 'Alkollü İçeçeklere İlişkin Özel Tüketim Vergisi', 'ÖTV 3A LİSTE', False),
    ('0076', 'Tütün Mamüllerine İlişkin Özel Tüketim Vergisi', 'ÖTV 3B LİSTE', False),
    ('0077', 'Kolalı Gazozlara İlişkin Özel Tüketim Vergisi', 'ÖTV 3C LİSTE', False),
    ('1047', 'Damga Vergisi', 'DAMGA V', False),
    ('1048', '5035 Sayılı Kanuna Göre Damga Vergisi', '5035SKDAMGAV', False),
    ('4071', 'Elektrik Ve Havagazi Tüketim Vergisi', 'ELK.HAVAGAZ.TÜK.VER.', False),
    ('4080', 'Özel İletişim Vergisi', 'Ö.İLETİŞİM V', False),
    ('4081', '5035 Sayılı Kanuna Göre Özel İletişim Vergisi', '5035ÖZİLETV.', False),
    ('4171', 'Petrol Ve Doğalgaz Ürünlerine İlişkin Ötv Tevkifatı', 'PTR-DGZ ÖTV TEVKİFAT', False),
    ('8001', 'Borsa Tescil Ücreti', 'BORSA TES.ÜC.', False),
    ('8002', 'Enerji Fonu', 'ENERJİ FONU', False),
    ('8004', 'Trt Payı', 'TRT PAYI', False),
    ('8005', 'Elektrik Tüketim Vergisi', 'ELK.TÜK.VER.', False),
    ('8006', 'Telsiz Kullanım Ücreti', 'TK KULLANIM', False),
    ('8007', 'Telsiz Ruhsat Ücreti', 'TK RUHSAT', False),
    ('8008', 'Çevre Temizlik Vergisi', 'ÇEV. TEM .VER.', False),
    ('9021', '4961 Banka Sigorta Muameleleri Vergisi', '4961BANKASMV', False),
    ('9040', 'Mera Fonu', 'MERA FONU', False),
    ('9077', 'Motorlu Taşıt Araçlarına İlişkin Özel Tüketim Vergisi (Tescile Tabi Olanlar)', 'ÖTV 2.LİSTE', False),
    ('9944', 'Belediyelere Ödenen Hal Rüsumu', 'BEL.ÖD.HAL RÜSUM', False),
]

def create_and_fill_tax_codes():
    """Referans tablosunu oluştur ve doldur"""
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    # Tablo kontrolü
    if 'tax_codes' in inspector.get_table_names():
        print("✓ tax_codes tablosu zaten mevcut")
    else:
        print("✗ tax_codes tablosu yok, oluşturuluyor...")
        TaxCode.__table__.create(engine)
        print("✓ Tablo oluşturuldu!")
    
    db = SessionLocal()
    
    try:
        # Mevcut kayıt sayısı
        existing_count = db.query(TaxCode).count()
        print(f"\nMevcut kayıt sayısı: {existing_count}")
        
        if existing_count > 0:
            print("⚠ Tablo dolu, önce temizleniyor...")
            db.query(TaxCode).delete()
            db.commit()
            print("✓ Tablo temizlendi")
        
        # Verileri ekle
        print(f"\n=== {len(TAX_CODES_DATA)} VERGİ KODU EKLENİYOR ===")
        
        for code, name, short_name, is_withholding in TAX_CODES_DATA:
            tax_code = TaxCode(
                code=code,
                name=name,
                short_name=short_name,
                is_withholding=is_withholding
            )
            db.add(tax_code)
            print(f"  + {code}: {name}")
        
        db.commit()
        print(f"\n✓ {len(TAX_CODES_DATA)} kod başarıyla eklendi!")
        
        # Kontrol
        total = db.query(TaxCode).count()
        print(f"\n✓ Toplam kayıt: {total}")
        
        # Örnek sorgulama
        kdv = db.query(TaxCode).filter(TaxCode.code == '0015').first()
        print(f"\nÖrnek: {kdv.code} -> {kdv.name} ({kdv.short_name})")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 80)
    print("VERGİ KODLARI REFERANS TABLOSU")
    print("=" * 80)
    
    create_and_fill_tax_codes()
