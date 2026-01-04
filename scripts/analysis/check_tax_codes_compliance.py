"""
Mevcut vergi kodlarını resmi UBL-TR listesiyle karşılaştır
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from app.core.database import SessionLocal
from app.models.invoice_tax import InvoiceTax
from sqlalchemy import func

# UBL-TR Resmi Vergi Kodları Listesi
OFFICIAL_TAX_CODES = {
    '0003': 'Gelir Vergisi Stopajı',
    '0011': 'Kurumlar Vergisi Stopajı',
    '0015': 'Gerçek Usulde Katma Değer Vergisi',
    '0021': 'Banka Muameleleri Vergisi',
    '0022': 'Sigorta Muameleleri Vergisi',
    '0059': 'Konaklama Vergisi',  # Yeni eklenen (1.40)
    '0061': 'Kaynak Kullanımı Destekleme Fonu Kesintisi',
    '0071': 'Petrol Ve Doğalgaz Ürünlerine İlişkin Özel Tüketim Vergisi',
    '0073': 'Kolalı Gazoz, Alkollü İçeçekler Ve Tütün Mamüllerine İlişkin Özel Tüketim Vergisi',
    '0074': 'Dayanıklı Tüketim Ve Diğer Mallara İlişkin Özel Tüketim Vergisi',
    '0075': 'Alkollü İçeçeklere İlişkin Özel Tüketim Vergisi',
    '0076': 'Tütün Mamüllerine İlişkin Özel Tüketim Vergisi',
    '0077': 'Kolalı Gazozlara İlişkin Özel Tüketim Vergisi',
    '1047': 'Damga Vergisi',
    '1048': '5035 Sayılı Kanuna Göre Damga Vergisi',
    '4071': 'Elektrik Ve Havagazi Tüketim Vergisi',
    '4080': 'Özel İletişim Vergisi',
    '4081': '5035 Sayılı Kanuna Göre Özel İletişim Vergisi',
    '4171': 'Petrol Ve Doğalgaz Ürünlerine İlişkin Ötv Tevkifatı',
    '8001': 'Borsa Tescil Ücreti',
    '8002': 'Enerji Fonu',
    '8004': 'Trt Payı',
    '8005': 'Elektrik Tüketim Vergisi',
    '8006': 'Telsiz Kullanım Ücreti',
    '8007': 'Telsiz Ruhsat Ücreti',
    '8008': 'Çevre Temizlik Vergisi',
    '9021': '4961 Banka Sigorta Muameleleri Vergisi',
    '9040': 'Mera Fonu',
    '9077': 'Motorlu Taşıt Araçlarına İlişkin Özel Tüketim Vergisi (Tescile Tabi Olanlar)',
    '9944': 'Belediyelere Ödenen Hal Rüsumu',
}

def check_compliance():
    """Vergi kodlarını kontrol et"""
    db = SessionLocal()
    
    try:
        # Mevcut vergi kodlarını al
        result = db.query(
            InvoiceTax.tax_type_code,
            InvoiceTax.tax_name,
            func.count(InvoiceTax.id).label('count')
        ).group_by(
            InvoiceTax.tax_type_code,
            InvoiceTax.tax_name
        ).order_by(
            InvoiceTax.tax_type_code
        ).all()
        
        print("=" * 100)
        print("VERGİ KODLARI UYUMLULUK KONTROLÜ")
        print("=" * 100)
        
        print("\n=== MEVCUT VERGİ KODLARI ===")
        compliant = 0
        non_compliant = 0
        
        for r in result:
            code = r.tax_type_code
            name = r.tax_name
            count = r.count
            
            if code in OFFICIAL_TAX_CODES:
                official_name = OFFICIAL_TAX_CODES[code]
                
                # İsim eşleşmesini kontrol et (normalize edilmiş)
                name_normalized = name.upper().replace('Ğ', 'G').replace('Ü', 'U').replace('Ş', 'S').replace('İ', 'I').replace('Ö', 'O').replace('Ç', 'C')
                official_normalized = official_name.upper().replace('Ğ', 'G').replace('Ü', 'U').replace('Ş', 'S').replace('İ', 'I').replace('Ö', 'O').replace('Ç', 'C')
                
                if name_normalized in official_normalized or official_normalized in name_normalized:
                    print(f"✓ {code}: {name} ({count} kayıt)")
                    compliant += 1
                else:
                    print(f"⚠ {code}: {name} ({count} kayıt)")
                    print(f"  → Resmi: {official_name}")
                    non_compliant += 1
            else:
                print(f"✗ {code}: {name} ({count} kayıt) - RESMİ LİSTEDE YOK!")
                non_compliant += 1
        
        print(f"\n=== ÖZET ===")
        print(f"✓ Uyumlu: {compliant}")
        print(f"⚠ Uyumsuz/Düzeltilmesi Gereken: {non_compliant}")
        
        # Kullanılan kodlar
        used_codes = set([r.tax_type_code for r in result])
        
        # Kullanılmayan resmi kodlar
        unused_codes = set(OFFICIAL_TAX_CODES.keys()) - used_codes
        
        if unused_codes:
            print(f"\n=== KULLANILMAYAN RESMİ KODLAR ===")
            for code in sorted(unused_codes):
                print(f"  {code}: {OFFICIAL_TAX_CODES[code]}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_compliance()
