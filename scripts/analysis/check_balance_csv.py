import pandas as pd

csv_file = r"C:\Users\CAGATAY\OneDrive\Desktop\MUHASEBE_ANALIZ_v2\muhasebe kayıtları PERSONEL HESAPNOLAR DUZELTILMIS.csv"

print("=" * 80)
print("FİŞ DENGESİ KONTROLÜ")
print("=" * 80)

# CSV'yi oku
df = pd.read_csv(csv_file, sep=';', encoding='utf-8-sig', dtype={'account_id': str})
print(f"\n📄 Toplam Satır: {len(df):,}")

# Kolon isimlerini kontrol et
print(f"\n📊 Kolonlar: {list(df.columns)}")

# Fiş numarasına göre grupla ve borç-alacak kontrolü
# transaction_numbe (kesilmiş) veya transaction_number
fis_col = None
for col in df.columns:
    if 'transaction' in col.lower() and ('number' in col.lower() or 'numbe' in col.lower()):
        fis_col = col
        break
if not fis_col and 'fiş_no' in df.columns:
    fis_col = 'fiş_no'

if fis_col:
    
    # Borç/Alacak kolonları
    debit_col = next((col for col in df.columns if 'borç' in col.lower() or 'debit' in col.lower()), None)
    credit_col = next((col for col in df.columns if 'alacak' in col.lower() or 'credit' in col.lower()), None)
    
    print(f"\n🔍 Fiş kolonu: {fis_col}")
    print(f"🔍 Borç kolonu: {debit_col}")
    print(f"🔍 Alacak kolonu: {credit_col}")
    
    if debit_col and credit_col:
        # NaN'leri 0'a çevir
        df[debit_col] = pd.to_numeric(df[debit_col], errors='coerce').fillna(0)
        df[credit_col] = pd.to_numeric(df[credit_col], errors='coerce').fillna(0)
        
        # Fiş numarasına göre grupla
        grouped = df.groupby(fis_col).agg({
            debit_col: 'sum',
            credit_col: 'sum'
        })
        
        # Farkı hesapla
        grouped['fark'] = grouped[debit_col] - grouped[credit_col]
        grouped['fark_abs'] = grouped['fark'].abs()
        
        # Dengesi tutmayanlar (0.01'den büyük fark)
        unbalanced = grouped[grouped['fark_abs'] > 0.01]
        
        print(f"\n✅ Toplam Fiş: {len(grouped):,}")
        print(f"✅ Dengesi Tutar Fiş: {len(grouped[grouped['fark_abs'] <= 0.01]):,}")
        print(f"❌ Dengesi Tutmayan Fiş: {len(unbalanced):,}")
        
        if len(unbalanced) > 0:
            print(f"\n❌ Dengesi TUTMAYAN İlk 20 Fiş:")
            print("-" * 80)
            print(f"{'Fiş No':<20} {'Borç':>15} {'Alacak':>15} {'Fark':>15}")
            print("-" * 80)
            for fis_no, row in unbalanced.head(20).iterrows():
                print(f"{str(fis_no):<20} {row[debit_col]:>15,.2f} {row[credit_col]:>15,.2f} {row['fark']:>15,.2f}")
        
        # Toplam borç-alacak
        total_debit = df[debit_col].sum()
        total_credit = df[credit_col].sum()
        total_diff = total_debit - total_credit
        
        print(f"\n" + "=" * 80)
        print("GENEL TOPLAM")
        print("=" * 80)
        print(f"Toplam Borç:   {total_debit:>20,.2f}")
        print(f"Toplam Alacak: {total_credit:>20,.2f}")
        print(f"Fark:          {total_diff:>20,.2f}")
        
        if abs(total_diff) < 0.01:
            print("\n✅ GENEL TOPLAM DENGEDE!")
        else:
            print("\n❌ GENEL TOPLAM DENGEDE DEĞİL!")
    else:
        print("\n❌ Borç/Alacak kolonları bulunamadı!")
else:
    print("\n❌ Fiş numarası kolonu bulunamadı!")

# 335 hesapları kontrolü
print(f"\n" + "=" * 80)
print("335 HESAPLARI KONTROLÜ")
print("=" * 80)

df_335 = df[df['account_id'].str.startswith('335.', na=False)]
print(f"335 hesap satırları: {len(df_335):,}")

# Farklı 335 hesapları
unique_335 = df_335['account_id'].unique()
print(f"Farklı 335 hesap: {len(unique_335):,}")

# İlk 20 örnek
print(f"\nİlk 20 örnek:")
for i, acc in enumerate(sorted(unique_335)[:20]):
    count = len(df_335[df_335['account_id'] == acc])
    print(f"{i+1}. {acc} ({count} satır)")

print("\n" + "=" * 80)
