"""
PDF'DEN FATURA SATIR BİLGİLERİNİ ÇIKARMA - DETAYLI ANALİZ
Mal/Hizmet Kalemleri (Line Items) Extraction
"""
import sys
import re

try:
    import PyPDF2
    import pdfplumber
except:
    print("❌ Gerekli kütüphaneler yok!")
    print("pip install PyPDF2 pdfplumber")
    sys.exit(1)

pdf_path = r"C:\Projects\muhasebe-sistem\ilhan_imre.pdf"

print("=" * 100)
print("PDF SATIR BİLGİLERİ ÇIKARMA - DETAYLI ANALİZ")
print("=" * 100)

# ============================================================================
# YÖNTEM 1: PyPDF2 ile Basit Metin Çıkarma
# ============================================================================
print("\n📖 YÖNTEM 1: PyPDF2 ile Basit Metin Çıkarma")
print("-" * 100)
print("Açıklama: PDF'den tüm metni çıkarır, ancak tablo yapısını korumaz.")
print("Avantaj: Basit, hızlı")
print("Dezavantaj: Tablo sütunları karışabilir, pozisyon bilgisi yok\n")

with open(pdf_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

print("Çıkarılan Metin (ilk 3000 karakter):")
print("-" * 100)
print(text[:3000])
print("-" * 100)

# Tablo bölümünü bul
if "Sıra" in text and "Mal Hizmet" in text:
    # Tablo başlangıcını bul
    table_start = text.find("Sıra")
    table_section = text[table_start:table_start+1500]
    print("\n📋 Tablo Bölümü:")
    print("-" * 100)
    print(table_section)
    print("-" * 100)

# ============================================================================
# YÖNTEM 2: pdfplumber ile Tablo Extraction
# ============================================================================
print("\n\n📊 YÖNTEM 2: pdfplumber ile Tablo Extraction")
print("-" * 100)
print("Açıklama: PDF'deki tabloları otomatik algılayıp extract eder.")
print("Avantaj: Tablo yapısını korur, sütunları doğru ayırır")
print("Dezavantaj: Karmaşık tablolarda hata yapabilir\n")

with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages, 1):
        print(f"\n📄 Sayfa {page_num}:")
        print("-" * 100)
        
        # Tablolari çıkar
        tables = page.extract_tables()
        
        if tables:
            print(f"✅ {len(tables)} tablo bulundu\n")
            
            for table_num, table in enumerate(tables, 1):
                print(f"Tablo {table_num}:")
                print(f"Satır sayısı: {len(table)}")
                print(f"Sütun sayısı: {len(table[0]) if table else 0}")
                print()
                
                # Tabloyu göster
                for row_num, row in enumerate(table):
                    print(f"  Satır {row_num}: {row}")
                
                print()
        else:
            print("❌ Tablo bulunamadı")
        
        # Alternatif: Metin pozisyonları ile
        print("\n📍 Metin Pozisyon Analizi:")
        print("-" * 100)
        words = page.extract_words()
        print(f"Toplam {len(words)} kelime bulundu")
        print("\nİlk 20 kelime (x, y pozisyonları ile):")
        for i, word in enumerate(words[:20]):
            print(f"  {i+1}. '{word['text']}' @ ({word['x0']:.1f}, {word['top']:.1f})")

# ============================================================================
# YÖNTEM 3: Regex ile Manuel Parse
# ============================================================================
print("\n\n🔍 YÖNTEM 3: Regex ile Manuel Parse")
print("-" * 100)
print("Açıklama: Metin içinden regex pattern'leri ile satır bilgilerini çeker.")
print("Avantaj: Özelleştirilebilir, spesifik formatlara uyarlanabilir")
print("Dezavantaj: Her PDF formatı için farklı regex gerekir\n")

# E-arşiv fatura satır formatı genellikle:
# Sıra No | Mal/Hizmet | Miktar | Birim Fiyat | KDV Oranı | KDV Tutarı | Mal/Hizmet Tutarı

# Satır pattern'i (basitleştirilmiş)
# Örnek: "1 SOĞUK HADDE 1.00 17,971,050.14 %20 3,594,210.03 17,971,050.14"

line_patterns = [
    # Pattern 1: Sıra No ile başlayan
    r'(\d+)\s+([A-ZİÜÖŞÇĞa-zığüşöç\s\-\(\)\.]+?)\s+([\d,\.]+)\s+([\d,\.]+)\s+%?\s*(\d+)\s+([\d,\.]+)\s+([\d,\.]+)',
    
    # Pattern 2: Sadece açıklama ve tutarlar
    r'([A-ZİÜÖŞÇĞa-zığüşöç\s\-\(\)\.]+?)\s+([\d,\.]+)\s+TL',
]

print("Satır Pattern'leri ile Arama:")
print("-" * 100)

for pattern_num, pattern in enumerate(line_patterns, 1):
    print(f"\nPattern {pattern_num}: {pattern[:50]}...")
    matches = re.finditer(pattern, text)
    match_count = 0
    for match in matches:
        match_count += 1
        print(f"  Eşleşme {match_count}: {match.groups()}")
        if match_count >= 3:  # İlk 3 eşleşme
            break
    
    if match_count == 0:
        print("  ❌ Eşleşme bulunamadı")

# ============================================================================
# YÖNTEM 4: Pozisyon Bazlı Extraction (pdfplumber)
# ============================================================================
print("\n\n📐 YÖNTEM 4: Pozisyon Bazlı Extraction")
print("-" * 100)
print("Açıklama: Satır tablo başlıklarının pozisyonlarını bulup, altındaki değerleri çeker.")
print("Avantaj: Düzgün formatlanmış PDF'lerde çok başarılı")
print("Dezavantaj: Pozisyon hesaplamaları gerekir\n")

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    
    # Tablo başlıklarını bul
    text_content = page.extract_text()
    
    # Başlık kelimelerini ara
    header_keywords = ["Sıra", "Mal", "Hizmet", "Miktar", "Birim", "Fiyat", "KDV", "Oran", "Tutar"]
    
    print("Tablo Başlıkları Arama:")
    words = page.extract_words()
    
    header_positions = {}
    for word in words:
        word_text = word['text']
        for keyword in header_keywords:
            if keyword.lower() in word_text.lower():
                if keyword not in header_positions:
                    header_positions[keyword] = []
                header_positions[keyword].append({
                    'text': word_text,
                    'x': word['x0'],
                    'y': word['top'],
                    'width': word['x1'] - word['x0']
                })
    
    print("\nBulunan Başlıklar:")
    for keyword, positions in header_positions.items():
        print(f"  {keyword}: {len(positions)} pozisyon")
        for pos in positions[:2]:  # İlk 2 pozisyon
            print(f"    - '{pos['text']}' @ x={pos['x']:.1f}, y={pos['y']:.1f}")

# ============================================================================
# YÖNTEM 5: GİB E-Arşiv Standart Tablo Formatı
# ============================================================================
print("\n\n📋 YÖNTEM 5: GİB E-Arşiv Standart Format Analizi")
print("-" * 100)
print("Açıklama: GİB e-arşiv faturalarının standart tablo yapısını kullanarak parse eder.\n")

# E-arşiv fatura standart sütunları:
columns = [
    "Sıra No",
    "Mal Hizmet",
    "Miktar",
    "Birim Fiyat",
    "İskonto/Arttırım Oranı",
    "İskonto/Arttırım Tutarı",
    "İskonto/Arttırım Nedeni",
    "KDV Oranı",
    "KDV Tutarı",
    "Diğer Vergiler",
    "Mal Hizmet Tutarı"
]

print("GİB E-Arşiv Standart Sütunlar:")
for i, col in enumerate(columns, 1):
    print(f"  {i}. {col}")

print("\nBu sütunları PDF'den çıkarmak için:")
print("1. Tablo başlangıç ve bitiş noktasını bul")
print("2. Her satır için sütun değerlerini ayır")
print("3. Sayısal değerleri parse et (1.234,56 → 1234.56)")
print("4. XML'e ekle")

# ============================================================================
# PRATIK ÖRNEK: Satır Bilgilerini Çıkarma
# ============================================================================
print("\n\n🔧 PRATIK ÖRNEK: Satır Bilgilerini Çıkarma")
print("-" * 100)

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    tables = page.extract_tables()
    
    if tables:
        invoice_table = None
        
        # En büyük tabloyu bul (genellikle fatura satırları)
        for table in tables:
            if len(table) > 2:  # En az başlık + 2 satır
                invoice_table = table
                break
        
        if invoice_table:
            print(f"✅ Fatura tablosu bulundu ({len(invoice_table)} satır)\n")
            
            # Başlık satırı
            headers = invoice_table[0]
            print("Başlıklar:")
            print(f"  {headers}\n")
            
            # Veri satırları
            print("Fatura Satırları:")
            print("-" * 100)
            
            line_items = []
            for row_num, row in enumerate(invoice_table[1:], 1):
                if row and any(cell for cell in row if cell):  # Boş satırları atla
                    print(f"Satır {row_num}:")
                    
                    # Her hücreyi göster
                    for col_num, cell in enumerate(row):
                        header = headers[col_num] if col_num < len(headers) else f"Col_{col_num}"
                        print(f"  {header}: {cell}")
                    
                    # Satır bilgisini kaydet
                    line_item = {
                        'sira_no': row[0] if len(row) > 0 else None,
                        'mal_hizmet': row[1] if len(row) > 1 else None,
                        'miktar': row[2] if len(row) > 2 else None,
                        'birim_fiyat': row[3] if len(row) > 3 else None,
                        'kdv_oran': row[7] if len(row) > 7 else None,
                        'kdv_tutar': row[8] if len(row) > 8 else None,
                        'tutar': row[10] if len(row) > 10 else None,
                    }
                    line_items.append(line_item)
                    print()
            
            print(f"\n✅ Toplam {len(line_items)} satır kalem çıkarıldı")
            print("\nÖzet:")
            for item in line_items:
                print(f"  - {item['mal_hizmet']}: {item['tutar']}")
        else:
            print("❌ Uygun fatura tablosu bulunamadı")

# ============================================================================
# ÖZET ve ÖNERİLER
# ============================================================================
print("\n\n" + "=" * 100)
print("ÖZET: PDF'DEN SATIR BİLGİSİ ÇIKARMA YÖNTEMLERİ")
print("=" * 100)

print("""
📊 YÖNTEM KARŞILAŞTIRMASI:
========================

1. PyPDF2 (Basit Metin)
   ✅ Avantajlar: Basit, hızlı, her PDF'de çalışır
   ❌ Dezavantajlar: Tablo yapısı bozulur, sütun ayırma zorlu
   🎯 Kullanım: Basit faturalar, az satırlı
   ⭐ Başarı Oranı: %40-60

2. pdfplumber (Tablo Extraction)
   ✅ Avantajlar: Tablo yapısını korur, otomatik sütun algılama
   ❌ Dezavantajlar: Karmaşık tablolarda hata, birleşik hücrelerde sorun
   🎯 Kullanım: Standart formatlanmış e-arşiv faturalar
   ⭐ Başarı Oranı: %70-90

3. Regex (Manuel Parse)
   ✅ Avantajlar: Özelleştirilebilir, spesifik formatlara uygun
   ❌ Dezavantajlar: Her format için farklı regex, bakım zorlu
   🎯 Kullanım: Belirli tedarikçilerin sabit formatları
   ⭐ Başarı Oranı: %50-80

4. Pozisyon Bazlı
   ✅ Avantajlar: Çok hassas, sütun konumlarını kullanır
   ❌ Dezavantajlar: Pozisyon hesaplamaları, format değişikliklerine hassas
   🎯 Kullanım: GİB standart XSLT çıktıları
   ⭐ Başarı Oranı: %80-95

5. OCR + ML (Gelişmiş)
   ✅ Avantajlar: Taranmış PDF'lerde çalışır, format bağımsız
   ❌ Dezavantajlar: Yavaş, pahalı, eğitim gerekir
   🎯 Kullanım: Taranmış eski faturalar, farklı formatlar
   ⭐ Başarı Oranı: %60-95

ÖNERİLEN YAKLAŞIM: HİBRİT SİSTEM
================================

1. Önce pdfplumber ile tablo extraction dene
2. Başarısız olursa regex ile manuel parse
3. Kritik alanları doğrulama yap
4. Kullanıcıya manuel düzeltme seçeneği sun

ÖRNEK KOD:
```python
def extract_invoice_lines(pdf_path):
    # Yöntem 1: pdfplumber
    lines = extract_with_pdfplumber(pdf_path)
    if lines and len(lines) > 0:
        return lines
    
    # Yöntem 2: Regex
    lines = extract_with_regex(pdf_path)
    if lines and len(lines) > 0:
        return lines
    
    # Yöntem 3: Manuel inceleme gerekir
    return None
```

SATIR BİLGİLERİNİ XML'E EKLEME:
================================

GİB e-arşiv XML'inde her satır için:
```xml
<malHizmetTablosu>
  <siraNo>1</siraNo>
  <malHizmet>SOĞUK HADDE FAZ-2</malHizmet>
  <miktar>1.00</miktar>
  <birimFiyat>17971050.14</birimFiyat>
  <malHizmetTutari>17971050.14</malHizmetTutari>
  <kdvOrani>20</kdvOrani>
  <kdvTutari>3594210.03</kdvTutari>
  <vergilerDahilToplam>21565260.17</vergilerDahilToplam>
</malHizmetTablosu>
```

ZORLUKLAR ve ÇÖZÜMLER:
=====================

Zorluk 1: Satırlar birden fazla satıra bölünmüş
Çözüm: Pozisyon bilgisi ile gruplayın

Zorluk 2: Birleşik hücreler
Çözüm: Tablo yapısını manuel analiz edin

Zorluk 3: Sayı formatları (1.234,56 vs 1,234.56)
Çözüm: TR locale ile parse: replace('.', '').replace(',', '.')

Zorluk 4: Boş/eksik hücreler
Çözüm: Default değerler ve validation

Zorluk 5: Özel karakterler (™, ®, vb.)
Çözüm: Unicode normalization
""")

print("\n" + "=" * 100)
