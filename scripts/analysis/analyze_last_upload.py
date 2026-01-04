"""
Son Excel upload'ı analiz et - kolon adları ve örnek satırlar
"""
import pandas as pd
import os
from datetime import datetime

# Downloads klasöründeki en son .xlsx dosyasını bul
downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
excel_files = []

for file in os.listdir(downloads_folder):
    if file.endswith('.xlsx') or file.endswith('.xls'):
        if 'personel' in file.lower() or 'sicil' in file.lower():
            file_path = os.path.join(downloads_folder, file)
            mtime = os.path.getmtime(file_path)
            excel_files.append((file_path, mtime, file))

if not excel_files:
    print("❌ Downloads klasöründe personel/sicil Excel dosyası bulunamadı")
    print(f"📂 Arama yolu: {downloads_folder}")
    exit(1)

# En son değiştirilen dosyayı al
excel_files.sort(key=lambda x: x[1], reverse=True)
latest_file, mtime, filename = excel_files[0]

print("=" * 80)
print("EN SON EXCEL DOSYASI")
print("=" * 80)
print(f"📄 Dosya: {filename}")
print(f"📁 Yol: {latest_file}")
print(f"🕐 Değiştirilme: {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}")
print()

try:
    df = pd.read_excel(latest_file)
    
    print("=" * 80)
    print("EXCEL KOLON İSİMLERİ")
    print("=" * 80)
    print(f"Satır sayısı: {len(df)}")
    print(f"Kolon sayısı: {len(df.columns)}\n")
    
    print("Kolonlar:")
    for i, col in enumerate(df.columns, 1):
        print(f"{i:2d}. [{col}]")
    
    print("\n" + "=" * 80)
    print("BEKLENİLEN KOLONLAR")
    print("=" * 80)
    expected = [
        'TC Kimlik No',
        'Ad Soyad',
        'Bölüm',
        'İşe Giriş Tarihi',
        'İşten Çıkış Tarihi',
        'Ücret',
        'Ücret Tipi',
        'İşyeri',
        'Ünvan',
        'Meslek Adı'
    ]
    
    for i, col in enumerate(expected, 1):
        exists = col in df.columns
        symbol = "✅" if exists else "❌"
        print(f"{symbol} {i:2d}. {col}")
    
    print("\n" + "=" * 80)
    print("İLK 3 SATIR ÖRNEĞİ")
    print("=" * 80)
    
    # İlk 3 satırı göster
    for idx in range(min(3, len(df))):
        print(f"\nSatır {idx + 1}:")
        for col in df.columns[:10]:  # İlk 10 kolon
            val = df[col].iloc[idx]
            if pd.notna(val):
                print(f"  {col}: {val}")
    
    print("\n" + "=" * 80)
    print("TC KİMLİK NO ÖRNEKLERİ")
    print("=" * 80)
    
    tc_col = None
    for col in df.columns:
        if 'tc' in col.lower() or 'kimlik' in col.lower():
            tc_col = col
            break
    
    if tc_col:
        print(f"TC kolon adı: [{tc_col}]")
        print("\nİlk 5 TC örneği:")
        for i, tc in enumerate(df[tc_col].head(), 1):
            if pd.notna(tc):
                print(f"  {i}. {tc} (tip: {type(tc).__name__})")
    else:
        print("❌ TC Kimlik No kolonu bulunamadı!")
        print("\nKolonlarda 'tc' veya 'kimlik' içeren:")
        for col in df.columns:
            if any(word in col.lower() for word in ['tc', 'kimlik', 'no', 'numara']):
                print(f"  - {col}")

except Exception as e:
    print(f"❌ Hata: {e}")
    import traceback
    traceback.print_exc()
