"""
Luca sicil Excel kolonlarını analiz et
"""
import pandas as pd
import sys

if len(sys.argv) < 2:
    print("Kullanım: python analyze_excel_columns.py <excel_dosyasi.xlsx>")
    print("Örnek: python analyze_excel_columns.py 'C:\\Users\\CAGATAY\\Downloads\\personel_sicil_listesi.xlsx'")
    sys.exit(1)

file_path = sys.argv[1]

try:
    df = pd.read_excel(file_path)
    
    print("=" * 80)
    print("EXCEL KOLON İSİMLERİ")
    print("=" * 80)
    print(f"Dosya: {file_path}")
    print(f"Satır sayısı: {len(df)}")
    print(f"Kolon sayısı: {len(df.columns)}\n")
    
    print("Kolonlar:")
    for i, col in enumerate(df.columns, 1):
        print(f"{i:2d}. {col}")
    
    print("\n" + "=" * 80)
    print("İLK 3 SATIR ÖRNEĞİ")
    print("=" * 80)
    print(df.head(3).to_string())
    
except Exception as e:
    print(f"Hata: {e}")
