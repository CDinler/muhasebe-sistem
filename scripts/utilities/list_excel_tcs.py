"""
Downloads'taki en son Excel'deki TC'leri listele
"""
import pandas as pd
import os
from datetime import datetime

downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
excel_files = []

for file in os.listdir(downloads_folder):
    if file.endswith('.xlsx') or file.endswith('.xls'):
        if 'personel' in file.lower() or 'sicil' in file.lower():
            if file.startswith('~$'):  # Geçici dosyaları atla
                continue
            file_path = os.path.join(downloads_folder, file)
            mtime = os.path.getmtime(file_path)
            excel_files.append((file_path, mtime, file))

if not excel_files:
    print("❌ Excel dosyası bulunamadı")
    exit(1)

excel_files.sort(key=lambda x: x[1], reverse=True)
latest_file, mtime, filename = excel_files[0]

print("=" * 80)
print("EXCEL TC KIMLIK KONTROLU")
print("=" * 80)
print(f"Dosya: {filename}")
print(f"Tarih: {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}")
print()

df = pd.read_excel(latest_file)

print(f"Toplam satır: {len(df)}")
print(f"Kolonlar: {', '.join(df.columns[:10])}...")
print()

# TC Kimlik No kolonunu bul
tc_col = None
for col in df.columns:
    if 'tc' in col.lower() and 'kimlik' in col.lower():
        tc_col = col
        break

if not tc_col:
    print("❌ TC Kimlik No kolonu bulunamadı!")
    exit(1)

print(f"TC kolonu: [{tc_col}]")
print()

# Tüm TC'leri listele
print("=" * 80)
print(f"DOSYADAKI TÜM TC'LER ({len(df)} adet)")
print("=" * 80)

for idx, row in df.iterrows():
    tc = str(int(row[tc_col])) if pd.notna(row[tc_col]) else 'BOŞ'
    ad = row.get('Adı', '')
    soyad = row.get('Soyadı', '')
    print(f"{idx+2:3d}. {tc:11s} - {ad} {soyad}")

print()
print("=" * 80)
print("ÖZET")
print("=" * 80)
print(f"Toplam satır: {len(df)}")
print(f"TC olan: {df[tc_col].notna().sum()}")
print(f"TC boş: {df[tc_col].isna().sum()}")
