"""
Luca Puantaj Excel dosyasını analiz et
"""
import pandas as pd
import sys

excel_file = r'C:\Users\CAGATAY\Downloads\puantaj (10).xls'

print("=" * 100)
print("LUCA PUANTAJ EXCEL DOSYASI ANALİZİ")
print("=" * 100)

try:
    # Excel'i oku - İlk 8 satırı atla (6 firma bilgisi + 2 başlık satırı)
    df = pd.read_excel(excel_file, header=8)
    
    print(f"\n📊 DOSYA BİLGİLERİ:")
    print(f"   Toplam Kolon: {len(df.columns)}")
    print(f"   Toplam Satır: {len(df)}")
    
    print(f"\n📋 KOLONLAR ({len(df.columns)} adet):")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i:2d}. {col}")
    
    print(f"\n📄 İLK 5 SATIR ÖRNEĞİ:")
    print("=" * 100)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 30)
    print(df.head(5))
    
    print(f"\n\n📈 VERİ TİPLERİ:")
    print("=" * 100)
    for col in df.columns:
        dtype = df[col].dtype
        non_null = df[col].count()
        null_count = df[col].isna().sum()
        print(f"   {col:40} -> {str(dtype):15} (Dolu: {non_null}, Boş: {null_count})")
    
    print(f"\n\n🔍 ÖRNEKLİ VERİLER:")
    print("=" * 100)
    
    # Birkaç satırı detaylı göster
    if len(df) > 0:
        print("\n1. SATIR DETAYI:")
        for col in df.columns:
            val = df.iloc[0][col]
            print(f"   {col:40} = {val}")
    
    # Unique değerler
    print(f"\n\n📊 UNIQUE DEĞERLER (Önemli Kolonlar):")
    print("=" * 100)
    
    # TC varsa
    if 'TC Kimlik No' in df.columns or 'TC' in df.columns or 'TCKN' in df.columns:
        tc_col = next((c for c in df.columns if 'TC' in c.upper()), None)
        if tc_col:
            print(f"\n{tc_col}:")
            print(f"   Benzersiz kişi sayısı: {df[tc_col].nunique()}")
    
    # Tarih kolonları
    date_cols = [c for c in df.columns if 'tarih' in c.lower() or 'date' in c.lower() or 'gün' in c.lower()]
    for col in date_cols:
        print(f"\n{col}:")
        print(f"   İlk 3 değer: {list(df[col].head(3))}")
    
    # Saat kolonları
    hour_cols = [c for c in df.columns if 'saat' in c.lower() or 'hour' in c.lower()]
    for col in hour_cols:
        print(f"\n{col}:")
        stats = df[col].describe() if pd.api.types.is_numeric_dtype(df[col]) else None
        if stats is not None:
            print(f"   Min: {stats['min']}, Max: {stats['max']}, Ortalama: {stats['mean']:.2f}")
    
    print("\n" + "=" * 100)
    print("✅ ANALİZ TAMAMLANDI")
    print("=" * 100)
    
except Exception as e:
    print(f"\n❌ HATA: {e}")
    import traceback
    traceback.print_exc()
