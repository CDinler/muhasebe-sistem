import pandas as pd
from app.core.database import SessionLocal
from sqlalchemy import text

csv_file = r"C:\Users\CAGATAY\OneDrive\Desktop\MUHASEBE_ANALIZ_v2\muhasebe kayıtları PERSONEL HESAPNOLAR DUZELTILMIS.csv"

print("=" * 80)
print("DÜZELTİLMİŞ CSV vs DATABASE KARŞILAŞTIRMASI")
print("=" * 80)

# Düzeltilmiş CSV'yi oku - account_id'yi STRING olarak oku!
df = pd.read_csv(csv_file, sep=';', encoding='utf-8-sig', dtype={'account_id': str})
print(f"\n📄 CSV Satır Sayısı: {len(df):,}")

# CSV'den 335 hesapları çıkar
csv_accounts = set()
csv_transactions = {}

for idx, row in df.iterrows():
    account = str(row['account_id']).strip()
    if account.startswith('335.'):
        csv_accounts.add(account)
        
        # Transaction sayısını say
        if account not in csv_transactions:
            csv_transactions[account] = 0
        csv_transactions[account] += 1

print(f"📊 CSV'deki farklı 335 hesap: {len(csv_accounts)}")
print(f"📊 CSV'deki toplam 335 satır: {sum(csv_transactions.values())}")

# Database'den 335 hesapları al
db = SessionLocal()

db_accounts = db.execute(text("""
    SELECT code, name, id
    FROM accounts
    WHERE code LIKE '335.%'
    ORDER BY code
""")).fetchall()

db_account_codes = {acc.code for acc in db_accounts}

print(f"💾 Database'deki 335 hesap: {len(db_account_codes)}")

# KARŞILAŞTIRMA
print("\n" + "=" * 80)
print("KARŞILAŞTIRMA SONUÇLARI")
print("=" * 80)

# 1. CSV'de olup DB'de OLMAYAN
csv_only = csv_accounts - db_account_codes
if csv_only:
    print(f"\n❌ CSV'de var, DB'de YOK: {len(csv_only)} hesap")
    for acc in sorted(csv_only)[:20]:
        print(f"   {acc} (CSV'de {csv_transactions[acc]} satır)")
    if len(csv_only) > 20:
        print(f"   ... ve {len(csv_only) - 20} hesap daha")
else:
    print("\n✅ CSV'deki TÜM hesaplar DB'de mevcut!")

# 2. DB'de olup CSV'de OLMAYAN
db_only = db_account_codes - csv_accounts
if db_only:
    print(f"\n⚠️ DB'de var, CSV'de YOK: {len(db_only)} hesap")
    
    # Bu hesaplarda transaction var mı?
    db_only_with_tx = []
    for code in sorted(db_only)[:10]:
        tx_count = db.execute(text("""
            SELECT COUNT(*) 
            FROM transaction_lines tl 
            JOIN accounts a ON tl.account_id = a.id 
            WHERE a.code = :code
        """), {'code': code}).scalar()
        
        if tx_count > 0:
            db_only_with_tx.append((code, tx_count))
    
    if db_only_with_tx:
        print(f"\n   ⚠️ DB'de olup CSV'de OLMAYAN ama TRANSACTION olan hesaplar:")
        for code, tx_count in db_only_with_tx:
            print(f"      {code}: {tx_count} transaction")
    
    print(f"\n   İlk 10 örnek:")
    for code in sorted(db_only)[:10]:
        acc_info = next((a for a in db_accounts if a.code == code), None)
        if acc_info:
            print(f"      {code} - {acc_info.name}")
else:
    print("\n✅ DB'deki TÜM hesaplar CSV'de mevcut!")

# 3. Her iki tarafta da olan
common = csv_accounts & db_account_codes
print(f"\n✅ Her iki tarafta da var: {len(common)} hesap")

# ÖZET
print("\n" + "=" * 80)
print("ÖZET")
print("=" * 80)
print(f"CSV'deki 335 hesap:     {len(csv_accounts):,}")
print(f"DB'deki 335 hesap:      {len(db_account_codes):,}")
print(f"Ortak hesap:            {len(common):,}")
print(f"CSV'de fazla:           {len(csv_only):,}")
print(f"DB'de fazla:            {len(db_only):,}")

# Transaction karşılaştırması
print("\n" + "=" * 80)
print("TRANSACTION KARŞILAŞTIRMASI (Ortak hesaplar)")
print("=" * 80)

# Ortak hesaplardan 10 tanesini kontrol et
sample_accounts = sorted(common)[:10]
print(f"\nİlk 10 ortak hesabın transaction sayısı:")
print("-" * 80)
print(f"{'Hesap Kodu':<20} {'CSV Satır':<12} {'DB TX':<12} {'Fark':<12}")
print("-" * 80)

for code in sample_accounts:
    csv_count = csv_transactions.get(code, 0)
    
    db_count = db.execute(text("""
        SELECT COUNT(*) 
        FROM transaction_lines tl 
        JOIN accounts a ON tl.account_id = a.id 
        WHERE a.code = :code
    """), {'code': code}).scalar()
    
    diff = csv_count - db_count
    status = "✅" if diff == 0 else "⚠️"
    print(f"{code:<20} {csv_count:<12} {db_count:<12} {diff:<12} {status}")

db.close()

print("\n" + "=" * 80)
