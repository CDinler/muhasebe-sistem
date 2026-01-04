"""
Debug: Bölüm adı karşılaştırması kontrolü
"""
import pandas as pd
from app.core.database import SessionLocal

# Test için örnek Bölüm adları (loglardan)
test_bolum_adlari = [
    '26-TAŞERON 21 ALİAĞA-HABAŞ 6                      ',
    '27-TAŞERON22 ASSAN AŞ. ORHANLI TUZLA ŞANTİYE      ',
    '28-TAŞERON 23 UZUNBEY-HABAŞ 7                     ',
    'MERKEZ OFİS                                       ',
    '34-HABAŞ 9 ALİAĞA'  # Excel'den
]

print("=== Bölüm Adı Analizi ===\n")

for bolum in test_bolum_adlari:
    print(f"Orijinal: '{bolum}'")
    print(f"Uzunluk: {len(bolum)}")
    print(f"Repr: {repr(bolum)}")
    print(f"Sağdan boşluk temizlenmiş: '{bolum.rstrip()}'")
    print(f"Yeni uzunluk: {len(bolum.rstrip())}")
    print(f"Trailing spaces: {len(bolum) - len(bolum.rstrip())}")
    print("-" * 80)

# Database'deki 2025-01 kayıtlarını kontrol et
print("\n=== Database Kontrolü ===\n")
db = SessionLocal()
try:
    from app.models.monthly_personnel_record import MonthlyPersonnelRecord
    
    records = db.query(MonthlyPersonnelRecord).filter(
        MonthlyPersonnelRecord.donem == '2025-01'
    ).all()
    
    print(f"2025-01 döneminde kayıt sayısı: {len(records)}")
    
    if records:
        print("\nİlk 5 kayıt:")
        for r in records[:5]:
            print(f"  ID: {r.id}, Personnel: {r.personnel_id}, Bölüm: '{r.bolum_adi}'")
    else:
        print("❌ Hiç kayıt yok!")
        
finally:
    db.close()

print("\n=== Excel'den Bölüm Okuma Testi ===\n")

# Excel dosyasını oku
try:
    df = pd.read_excel('personel_sicil_listesi_kadiogulla (18).xlsx')
    
    print(f"Excel'de toplam satır: {len(df)}")
    print(f"\nİlk 5 satırın 'Bölüm' değerleri:")
    
    for idx, bolum in df['Bölüm'].head(5).items():
        if pd.notna(bolum):
            bolum_str = str(bolum)
            print(f"  Satır {idx+2}: '{bolum_str}' (len={len(bolum_str)}, trailing={len(bolum_str) - len(bolum_str.rstrip())})")
        else:
            print(f"  Satır {idx+2}: NaN")
    
except Exception as e:
    print(f"Excel okuma hatası: {e}")
