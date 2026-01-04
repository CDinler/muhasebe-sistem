import pandas as pd
from app.core.database import SessionLocal
from sqlalchemy import text

csv_file = r"C:\Users\CAGATAY\OneDrive\Desktop\MUHASEBE_ANALIZ_v2\muhasebe kayıtları son guncel hali.csv"

print("=" * 80)
print("SON GÜNCEL CSV ANALİZİ")
print("=" * 80)

# CSV'yi oku
df = pd.read_csv(csv_file, sep=';', encoding='utf-8-sig', dtype={'account_code': str})
print(f"\n📄 Toplam Satır: {len(df):,}")
print(f"📊 Kolonlar: {list(df.columns)}")

# account_id yerine account_code kullan
account_col = 'account_code' if 'account_code' in df.columns else 'account_id'

# Fiş kolonu bul
fis_col = None
for col in df.columns:
    if 'transaction' in col.lower() and ('number' in col.lower() or 'numbe' in col.lower()):
        fis_col = col
        break
if not fis_col and 'fiş_no' in df.columns:
    fis_col = 'fiş_no'

# Borç-Alacak Dengesi
if fis_col:
    df['debit'] = pd.to_numeric(df['debit'], errors='coerce').fillna(0)
    df['credit'] = pd.to_numeric(df['credit'], errors='coerce').fillna(0)
    
    grouped = df.groupby(fis_col).agg({
        'debit': 'sum',
        'credit': 'sum'
    })
    grouped['fark'] = grouped['debit'] - grouped['credit']
    grouped['fark_abs'] = grouped['fark'].abs()
    
    unbalanced = grouped[grouped['fark_abs'] > 0.01]
    
    total_debit = df['debit'].sum()
    total_credit = df['credit'].sum()
    total_diff = total_debit - total_credit
    
    print(f"\n" + "=" * 80)
    print("FİŞ DENGESİ")
    print("=" * 80)
    print(f"Toplam Fiş: {len(grouped):,}")
    print(f"✅ Dengesi Tutar: {len(grouped[grouped['fark_abs'] <= 0.01]):,}")
    print(f"❌ Dengesi Tutmayan: {len(unbalanced):,}")
    
    print(f"\n" + "=" * 80)
    print("GENEL TOPLAM")
    print("=" * 80)
    print(f"Toplam Borç:   {total_debit:>20,.2f}")
    print(f"Toplam Alacak: {total_credit:>20,.2f}")
    print(f"FARK:          {total_diff:>20,.2f}")
    
    if abs(total_diff) < 50:
        print(f"\n✅ GENEL TOPLAM DENGEDE! (Fark: {abs(total_diff):.2f} TL)")
    else:
        print(f"\n⚠️ FARK VAR: {abs(total_diff):.2f} TL")

# 335 Hesapları
print(f"\n" + "=" * 80)
print("335 HESAPLARI")
print("=" * 80)

df_335 = df[df[account_col].str.startswith('335.', na=False)]
print(f"335 satır: {len(df_335):,}")
print(f"Farklı 335 hesap: {df_335[account_col].nunique():,}")

# TCKN uzunluk kontrolü
length_counts = {}
for acc in df_335[account_col].unique():
    tckn = acc.replace('335.', '')
    length = len(tckn)
    length_counts[length] = length_counts.get(length, 0) + 1

print(f"\nTCKN uzunluk dağılımı:")
for length in sorted(length_counts.keys()):
    print(f"  {length} haneli: {length_counts[length]:,} hesap")

# Hesap Planı Kontrolü
print(f"\n" + "=" * 80)
print("HESAP PLANI UYUMLULUĞU")
print("=" * 80)

# CSV'den tüm hesapları al
csv_accounts = set(df[account_col].dropna().unique())
print(f"CSV'deki farklı hesap: {len(csv_accounts):,}")

# Database'den hesapları al
db = SessionLocal()
try:
    result = db.execute(text("SELECT code FROM accounts"))
    db_accounts = set(row[0] for row in result)
    print(f"Database'deki hesap: {len(db_accounts):,}")
    
    # Karşılaştırma
    csv_only = csv_accounts - db_accounts
    db_only = db_accounts - csv_accounts
    common = csv_accounts & db_accounts
    
    print(f"Ortak hesap: {len(common):,}")
    print(f"\n❌ CSV'de var DB'de YOK: {len(csv_only):,} hesap")
    
    if csv_only:
        # Hesap türlerine göre grupla
        by_prefix = {}
        for acc in sorted(csv_only):
            prefix = acc.split('.')[0] if '.' in acc else acc[:3]
            if prefix not in by_prefix:
                by_prefix[prefix] = []
            by_prefix[prefix].append(acc)
        
        print(f"\n📊 Eksik hesapların dağılımı:")
        for prefix in sorted(by_prefix.keys()):
            accounts = by_prefix[prefix]
            print(f"   {prefix}: {len(accounts)} hesap")
            
            # İlk 5 örnek + kaç satırda kullanılmış
            for acc in accounts[:5]:
                count = len(df[df[account_col] == acc])
                print(f"      {acc} ({count} satır)")
            
            if len(accounts) > 5:
                print(f"      ... ve {len(accounts) - 5} hesap daha")
    
    print(f"\n⚠️ DB'de var CSV'de YOK: {len(db_only):,} hesap (normal)")
    
finally:
    db.close()

print("\n" + "=" * 80)
print("ÖZET")
print("=" * 80)
if abs(total_diff) < 50 and len(csv_only) == 0:
    print("✅ CSV HAZIR! Bakiye dengede ve tüm hesaplar mevcut")
elif abs(total_diff) < 50:
    print(f"⚠️ Bakiye OK ama {len(csv_only)} hesap eksik - önce hesapları ekle")
else:
    print(f"❌ Bakiye tutmuyor: {abs(total_diff):.2f} TL fark")

print("\n" + "=" * 80)
