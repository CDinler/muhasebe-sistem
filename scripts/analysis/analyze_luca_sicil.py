"""
Luca Personel Sicil Excel dosyasını analiz et
"""
import pandas as pd
from pathlib import Path

# Excel dosyasını oku
excel_path = r"C:\Users\CAGATAY\Downloads\personel_sicil_listesi_kadiogulla (18).xlsx"
df = pd.read_excel(excel_path)

print("="*80)
print("LUCA PERSONEL SİCİL LİSTESİ ANALİZİ")
print("="*80)

print(f"\n📊 GENEL İSTATİSTİKLER:")
print(f"Toplam satır: {len(df)}")
print(f"Unique TC: {df['TC Kimlik No'].nunique()}")
print(f"Unique İşyeri: {df['İşyeri'].nunique()}")
print(f"Unique Bölüm: {df['Bölüm'].nunique()}")

print(f"\n👥 AKTİF/PASİF DURUM:")
aktif = df['İşten Çıkış Tarihi'].isna().sum()
pasif = df['İşten Çıkış Tarihi'].notna().sum()
print(f"Aktif (çalışıyor): {aktif}")
print(f"Pasif (işten çıkmış): {pasif}")

print(f"\n💰 ÜCRET BİLGİLERİ:")
print(f"Min ücret: {df['Ücret'].min():,.2f} TL")
print(f"Max ücret: {df['Ücret'].max():,.2f} TL")
print(f"Ortalama: {df['Ücret'].mean():,.2f} TL")
print(f"\nNet/Brüt dağılımı:")
print(df['Net / Brüt'].value_counts())

print(f"\n🏢 İŞYERLERİ:")
print(df['İşyeri'].value_counts())

print(f"\n📍 BÖLÜMLER (ŞANTİYELER):")
print(df['Bölüm'].value_counts())

print(f"\n🔄 DUPLICATE TC (BİRDEN FAZLA BÖLÜMDE ÇALIŞANLAR):")
tc_counts = df['TC Kimlik No'].value_counts()
duplicates = tc_counts[tc_counts > 1]
print(f"Birden fazla bölümde çalışan personel sayısı: {len(duplicates)}")

if len(duplicates) > 0:
    print(f"\n📋 ÖRNEK DUPLICATE PERSONELLER (İLK 5):")
    for i, (tc, count) in enumerate(duplicates.head().items()):
        if i >= 5:
            break
        print(f"\n{i+1}. TC: {tc} ({count} farklı bölüm)")
        dup_rows = df[df['TC Kimlik No'] == tc]
        for idx, row in dup_rows.iterrows():
            print(f"   - Bölüm: {row['Bölüm']}")
            print(f"     Giriş: {row['İşe Giriş Tarihi']}, Çıkış: {row['İşten Çıkış Tarihi']}")
            print(f"     Ücret: {row['Ücret']:,.2f} ({row['Net / Brüt']})")

print(f"\n📋 KOLON LİSTESİ:")
for i, col in enumerate(df.columns, 1):
    non_null = df[col].notna().sum()
    print(f"{i:2d}. {col:40s} (Dolu: {non_null}/{len(df)})")

print(f"\n✅ ANALİZ TAMAMLANDI")
