import csv
import pandas as pd
from app.core.database import SessionLocal
from sqlalchemy import text

csv_file = r"C:\Users\CAGATAY\OneDrive\Desktop\MUHASEBE_ANALIZ_v2\muhasebe kayıtları PERSONEL HESAPNOLAR GUCEL.csv"

print("=" * 80)
print("CSV'DE OLUP DB'DE OLMAYAN HESAPLARIN ANALİZİ")
print("=" * 80)

# CSV oku
df = pd.read_csv(csv_file, sep=';', encoding='utf-8-sig')
csv_accounts = set()
for idx, row in df.iterrows():
    hesap = str(row['account_id']).strip()
    if hesap.startswith('335.'):
        csv_accounts.add(hesap)

# DB oku
db = SessionLocal()
db_result = db.execute(text("SELECT code FROM accounts WHERE code LIKE '335.%'")).fetchall()
db_accounts = {row.code for row in db_result}

# Fark bul
csv_only = csv_accounts - db_accounts

print(f"\nCSV'de olup DB'de OLMAYAN: {len(csv_only)} hesap\n")

# TCKN uzunluğu analizi
print("TCKN Uzunluğu Analizi:")
print("-" * 80)

lengths = {}
for acc in csv_only:
    tckn = acc.replace('335.', '')
    length = len(tckn)
    if length not in lengths:
        lengths[length] = []
    lengths[length].append(acc)

for length in sorted(lengths.keys()):
    print(f"\n{length} haneli TCKN: {len(lengths[length])} adet")
    print("Örnekler:")
    for acc in sorted(lengths[length])[:5]:
        tckn = acc.replace('335.', '')
        # Bu TCKN'in 11 haneli versiyonu DB'de var mı?
        tckn_11 = tckn.ljust(11, '0')  # Sağa 0 ekle
        test_code = f"335.{tckn_11}"
        exists = test_code in db_accounts
        print(f"  {acc} (TCKN: {tckn}) → {test_code} {'✅ DB\'de VAR!' if exists else '❌ DB\'de YOK'}")

# En çok tekrar eden 10 haneli hesapları kontrol et
if 10 in lengths:
    print(f"\n🔍 10 haneli TCKN'lerin detaylı kontrolü:")
    print("-" * 80)
    
    for acc in sorted(lengths[10])[:20]:  # İlk 20
        tckn_10 = acc.replace('335.', '')
        
        # Farklı varyasyonları kontrol et
        variants = [
            f"335.{tckn_10}0",  # Sona 0 ekle
            f"335.0{tckn_10}",  # Başa 0 ekle
            f"335.{tckn_10}",   # Olduğu gibi
        ]
        
        found = None
        for variant in variants:
            if variant in db_accounts:
                found = variant
                break
        
        # CSV'de bu hesapta kaç transaction var?
        tx_count = len(df[df['account_id'] == acc])
        
        status = f"✅ {found}" if found else "❌ BULUNAMADI"
        print(f"  {acc} ({tx_count} tx) → {status}")

print("\n" + "=" * 80)
print("SONUÇ:")
print("=" * 80)
print(f"CSV'de toplam 335 hesap: {len(csv_accounts)}")
print(f"DB'de toplam 335 hesap: {len(db_accounts)}")
print(f"CSV'de olup DB'de yok: {len(csv_only)}")

if 10 in lengths:
    print(f"\n⚠️ {len(lengths[10])} hesap 10 haneli TCKN formatında!")
    print("Bu hesaplar muhtemelen DB'de 11 haneli olarak var ama eşleşmiyor.")

db.close()
