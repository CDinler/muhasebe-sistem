import csv
import pandas as pd
from app.core.database import SessionLocal
from sqlalchemy import text

# CSV dosyasını oku (Excel noktalı virgül kullanıyor)
csv_file = r"C:\Users\CAGATAY\OneDrive\Desktop\MUHASEBE_ANALIZ_v2\muhasebe kayıtları PERSONEL HESAPNOLAR GUCEL.csv"

print("=" * 80)
print("PERSONEL HESAP KARŞILAŞTIRMA")
print("=" * 80)

# CSV'yi pandas ile oku (noktalı virgül separator)
df = pd.read_csv(csv_file, sep=';', encoding='utf-8-sig')

print(f"\n📄 CSV Kolonları: {list(df.columns)}")
print(f"📄 CSV Satır Sayısı: {len(df)}")
print("\n📄 İlk 3 satır:")
print(df.head(3))

# Hesap kodu kolonunu bul - CSV'de 'account_id' aslında hesap KODU
hesap_kodu_col = 'account_id'

print(f"\n✅ Hesap Kodu Kolonu: '{hesap_kodu_col}'")

# CSV'den 335 hesapları çıkar
csv_335_accounts = {}
for idx, row in df.iterrows():
    hesap_kod = str(row[hesap_kodu_col]).strip()
    if hesap_kod.startswith('335.'):
        # Diğer bilgileri de kaydet
        csv_335_accounts[hesap_kod] = {
            'row_index': idx + 2,  # Excel satır numarası (başlık + 1)
            'data': row.to_dict()
        }

print(f"\n📊 CSV'de 335 Hesap Sayısı: {len(csv_335_accounts)}")

# Database'den 335 hesapları al
db = SessionLocal()

db_accounts = db.execute(text("""
    SELECT code, name, id
    FROM accounts
    WHERE code LIKE '335.%'
    ORDER BY code
""")).fetchall()

db_335_accounts = {acc.code: {'name': acc.name, 'id': acc.id} for acc in db_accounts}

print(f"💾 Database'de 335 Hesap Sayısı: {len(db_335_accounts)}")

# KARŞILAŞTIRMA
print("\n" + "=" * 80)
print("KARŞILAŞTIRMA SONUÇLARI")
print("=" * 80)

# 1. CSV'de olup DB'de OLMAYAN hesaplar
csv_only = set(csv_335_accounts.keys()) - set(db_335_accounts.keys())
if csv_only:
    print(f"\n❌ CSV'de var, DB'de YOK ({len(csv_only)} adet):")
    for code in sorted(csv_only)[:10]:  # İlk 10
        print(f"   {code} (CSV satır: {csv_335_accounts[code]['row_index']})")
    if len(csv_only) > 10:
        print(f"   ... ve {len(csv_only) - 10} adet daha")
else:
    print("\n✅ CSV'deki tüm hesaplar DB'de mevcut")

# 2. DB'de olup CSV'de OLMAYAN hesaplar
db_only = set(db_335_accounts.keys()) - set(csv_335_accounts.keys())
if db_only:
    print(f"\n❌ DB'de var, CSV'de YOK ({len(db_only)} adet):")
    for code in sorted(db_only)[:10]:  # İlk 10
        print(f"   {code} - {db_335_accounts[code]['name']}")
    if len(db_only) > 10:
        print(f"   ... ve {len(db_only) - 10} adet daha")
else:
    print("\n✅ DB'deki tüm hesaplar CSV'de mevcut")

# 3. Her iki tarafta da olan hesaplar
common = set(csv_335_accounts.keys()) & set(db_335_accounts.keys())
print(f"\n✅ Her iki tarafta da var: {len(common)} hesap")

# 4. Transaction kontrolü - CSV'deki hesaplarda transaction var mı?
if csv_only:
    print(f"\n🔍 CSV'de olup DB'de OLMAYAN hesaplarda transaction kontrolü...")
    # Transaction_lines'da bu hesapları arayan kod var mı?
    
    # Önce bu kodların hangi account_id'lere denk geldiğini bul
    # (Belki eski kodlar transaction_lines'da hala var?)
    
print("\n" + "=" * 80)
print("ÖZET")
print("=" * 80)
print(f"CSV'deki 335 hesap: {len(csv_335_accounts)}")
print(f"DB'deki 335 hesap: {len(db_335_accounts)}")
print(f"Ortak hesap: {len(common)}")
print(f"CSV'de fazla: {len(csv_only)}")
print(f"DB'de fazla: {len(db_only)}")

# Transaction_lines kontrolü
print("\n🔍 DB'deki 335 hesaplarda transaction var mı?")
tx_check = db.execute(text("""
    SELECT 
        a.code,
        COUNT(tl.id) as tx_count
    FROM accounts a
    LEFT JOIN transaction_lines tl ON tl.account_id = a.id
    WHERE a.code LIKE '335.%'
    GROUP BY a.code
    HAVING COUNT(tl.id) > 0
    ORDER BY tx_count DESC
    LIMIT 10
""")).fetchall()

print("\nEn çok transaction olan 10 hesap:")
for acc in tx_check:
    in_csv = "✅ CSV'de var" if acc.code in csv_335_accounts else "❌ CSV'de YOK"
    print(f"  {acc.code}: {acc.tx_count} transaction | {in_csv}")

db.close()

print("\n" + "=" * 80)
