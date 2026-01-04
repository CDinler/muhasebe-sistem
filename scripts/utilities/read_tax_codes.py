import pdfplumber
import sys
from pathlib import Path

pdf_path = r"C:\Projects\muhasebe-sistem\docs\UBLTR_1.2.1_Kilavuzlar\UBLTR_1.2.1_Kilavuzlar\UBLTR_1.2.1_K_ılavuzlar\KOD LİSTELERİ\UBL-TR Kod Listeleri - V 1.40.pdf"

# Dosyayı bul
for file in Path(r"C:\Projects\muhasebe-sistem\docs\UBLTR_1.2.1_Kilavuzlar").rglob("*.pdf"):
    if "Kod" in file.name:
        pdf_path = str(file)
        break

print(f"PDF: {pdf_path}\n")

with pdfplumber.open(pdf_path) as pdf:
    print(f"Toplam sayfa: {len(pdf.pages)}\n")
    
    # Vergi kodlarını bul
    for i in range(len(pdf.pages)):
        text = pdf.pages[i].extract_text()
        if text:
            lines = text.split('\n')
            # Vergi ile ilgili sayfaları bul
            if any('vergi' in l.lower() or 'tax' in l.lower() for l in lines):
                print(f"\n{'='*80}")
                print(f"SAYFA {i+1}")
                print(f"{'='*80}")
                print('\n'.join(lines[:50]))
                print("\n...")
