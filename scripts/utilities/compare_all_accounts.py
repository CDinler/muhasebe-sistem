import pandas as pd
from app.core.database import SessionLocal
from sqlalchemy import text

csv_file = r"C:\Users\CAGATAY\OneDrive\Desktop\MUHASEBE_ANALIZ_v2\muhasebe kayıtları PERSONEL HESAPNOLAR DUZELTILMIS.csv"

print("=" * 80)
print("TÜM HESAPLARI KARŞILAŞTIR (CSV vs DATABASE)")
print("=" * 80)

# CSV'yi oku - account_id'yi STRING olarak
df = pd.read_csv(csv_file, sep=';', encoding='utf-8-sig', dtype={'account_id': str})
print(f"\n📄 CSV Satır Sayısı: {len(df):,}")

# CSV'den TÜM farklı account_id'leri al
csv_accounts = set(df['account_id'].dropna().unique())
print(f"📊 CSV'deki farklı hesap: {len(csv_accounts):,}")

# Database'den TÜM hesapları al
db = SessionLocal()
try:
    result = db.execute(text("SELECT code FROM accounts ORDER BY code"))
    db_accounts = set(row[0] for row in result)
    print(f"💾 Database'deki hesap: {len(db_accounts):,}")
finally:
    db.close()

# Karşılaştırma
csv_only = csv_accounts - db_accounts
db_only = db_accounts - csv_accounts
common = csv_accounts & db_accounts

print("\n" + "=" * 80)
print("KARŞILAŞTIRMA SONUÇLARI")
print("=" * 80)

if csv_only:
    print(f"\n❌ CSV'de var, DB'de YOK: {len(csv_only)} hesap")
    
    # Hesap türlerine göre grupla
    by_prefix = {}
    for acc in sorted(csv_only):
        prefix = acc.split('.')[0] if '.' in acc else acc[:3]
        if prefix not in by_prefix:
            by_prefix[prefix] = []
        by_prefix[prefix].append(acc)
    
    print("\n📊 Hesap türlerine göre dağılım:")
    for prefix in sorted(by_prefix.keys()):
        accounts = by_prefix[prefix]
        print(f"   {prefix}: {len(accounts)} hesap")
        # İlk 5 örnek
        for acc in accounts[:5]:
            # CSV'de kaç satır var?
            count = len(df[df['account_id'] == acc])
            print(f"      {acc} ({count} satır)")
        if len(accounts) > 5:
            print(f"      ... ve {len(accounts) - 5} hesap daha")
else:
    print("\n✅ CSV'deki TÜM hesaplar DB'de mevcut!")

if db_only:
    print(f"\n⚠️ DB'de var, CSV'de YOK: {len(db_only)} hesap")
    
    # Hesap türlerine göre grupla
    by_prefix = {}
    for acc in sorted(db_only):
        prefix = acc.split('.')[0] if '.' in acc else acc[:3]
        if prefix not in by_prefix:
            by_prefix[prefix] = []
        by_prefix[prefix].append(acc)
    
    print("\n📊 Hesap türlerine göre dağılım:")
    for prefix in sorted(by_prefix.keys()):
        accounts = by_prefix[prefix]
        print(f"   {prefix}: {len(accounts)} hesap")
        # İlk 3 örnek
        for i, acc in enumerate(accounts[:3]):
            print(f"      {acc}")
        if len(accounts) > 3:
            print(f"      ... ve {len(accounts) - 3} hesap daha")

print(f"\n✅ Her iki tarafta da var: {len(common):,} hesap")

print("\n" + "=" * 80)
print("ÖZET")
print("=" * 80)
print(f"CSV'deki hesap:     {len(csv_accounts):,}")
print(f"DB'deki hesap:      {len(db_accounts):,}")
print(f"Ortak hesap:        {len(common):,}")
print(f"CSV'de fazla:       {len(csv_only):,}")
print(f"DB'de fazla:        {len(db_only):,}")

print("\n" + "=" * 80)
