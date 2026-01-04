import pandas as pd

# Orijinal ve düzeltilmiş dosyaları karşılaştır
original_file = r"C:\Users\CAGATAY\OneDrive\Desktop\MUHASEBE_ANALIZ_v2\muhasebe kayıtları PERSONEL HESAPNOLAR GUCEL.csv"
fixed_file = r"C:\Users\CAGATAY\OneDrive\Desktop\MUHASEBE_ANALIZ_v2\muhasebe kayıtları PERSONEL HESAPNOLAR DUZELTILMIS.csv"

print("=" * 80)
print("ORİJİNAL vs DÜZELTİLMİŞ KARŞILAŞTIRMA")
print("=" * 80)

# Orijinal oku
df_orig = pd.read_csv(original_file, sep=';', encoding='utf-8-sig')
print(f"\n📄 Orijinal Satır: {len(df_orig):,}")

# Düzeltilmiş oku
df_fixed = pd.read_csv(fixed_file, sep=';', encoding='utf-8-sig', dtype={'account_id': str})
print(f"📄 Düzeltilmiş Satır: {len(df_fixed):,}")

if len(df_orig) != len(df_fixed):
    print(f"\n❌ SATIRLAR FARKLI! Fark: {len(df_orig) - len(df_fixed)}")
else:
    print(f"\n✅ Satır sayısı aynı")

# Kolon kontrolü
fis_col = None
for col in df_fixed.columns:
    if 'transaction' in col.lower() and ('number' in col.lower() or 'numbe' in col.lower()):
        fis_col = col
        break

if fis_col:
    # ORİJİNAL dengeleri kontrol
    df_orig[fis_col] = df_orig[fis_col].astype(str)
    df_orig['debit'] = pd.to_numeric(df_orig['debit'], errors='coerce').fillna(0)
    df_orig['credit'] = pd.to_numeric(df_orig['credit'], errors='coerce').fillna(0)
    
    orig_grouped = df_orig.groupby(fis_col).agg({
        'debit': 'sum',
        'credit': 'sum'
    })
    orig_grouped['fark'] = (orig_grouped['debit'] - orig_grouped['credit']).abs()
    orig_unbalanced = orig_grouped[orig_grouped['fark'] > 0.01]
    
    print(f"\n" + "=" * 80)
    print("ORİJİNAL CSV DENGESİ")
    print("=" * 80)
    print(f"Toplam Fiş: {len(orig_grouped):,}")
    print(f"Dengesi Tutmayan: {len(orig_unbalanced):,}")
    print(f"Toplam Borç: {df_orig['debit'].sum():,.2f}")
    print(f"Toplam Alacak: {df_orig['credit'].sum():,.2f}")
    print(f"Fark: {df_orig['debit'].sum() - df_orig['credit'].sum():,.2f}")
    
    # DÜZELTİLMİŞ dengeleri kontrol
    df_fixed[fis_col] = df_fixed[fis_col].astype(str)
    df_fixed['debit'] = pd.to_numeric(df_fixed['debit'], errors='coerce').fillna(0)
    df_fixed['credit'] = pd.to_numeric(df_fixed['credit'], errors='coerce').fillna(0)
    
    fixed_grouped = df_fixed.groupby(fis_col).agg({
        'debit': 'sum',
        'credit': 'sum'
    })
    fixed_grouped['fark'] = (fixed_grouped['debit'] - fixed_grouped['credit']).abs()
    fixed_unbalanced = fixed_grouped[fixed_grouped['fark'] > 0.01]
    
    print(f"\n" + "=" * 80)
    print("DÜZELTİLMİŞ CSV DENGESİ")
    print("=" * 80)
    print(f"Toplam Fiş: {len(fixed_grouped):,}")
    print(f"Dengesi Tutmayan: {len(fixed_unbalanced):,}")
    print(f"Toplam Borç: {df_fixed['debit'].sum():,.2f}")
    print(f"Toplam Alacak: {df_fixed['credit'].sum():,.2f}")
    print(f"Fark: {df_fixed['debit'].sum() - df_fixed['credit'].sum():,.2f}")
    
    # Karşılaştırma
    if len(orig_unbalanced) == len(fixed_unbalanced):
        print(f"\n✅ Dengesi tutmayan fiş sayısı AYNI - düzeltme dengeleri bozmamış")
    else:
        print(f"\n❌ Dengesi tutmayan fiş sayısı FARKLI!")
        print(f"   Orijinal: {len(orig_unbalanced)}, Düzeltilmiş: {len(fixed_unbalanced)}")

print("\n" + "=" * 80)
print("ÇÖZÜM ÖNERİSİ")
print("=" * 80)
print("1. Sadece 335 hesap kodlarını database'de UPDATE et")
print("2. Tüm fişleri yükleme, sadece hesap kodlarını güncelle")
print("3. Böylece mevcut dengeler bozulmaz")

print("\n" + "=" * 80)
