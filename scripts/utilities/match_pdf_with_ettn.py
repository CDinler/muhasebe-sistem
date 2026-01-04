"""
E-ARŞİV PDF → ETTN ÇIKARMA ve VERİTABANI EŞLEŞTİRME
Pratik Uygulama
"""
import sys
import re
sys.path.append('.')

from app.core.database import get_db
from app.models.einvoice import EInvoice

try:
    import PyPDF2
except:
    print("❌ PyPDF2 gerekli: pip install PyPDF2")
    sys.exit(1)

pdf_path = r"C:\Projects\muhasebe-sistem\ilhan_imre.pdf"

print("=" * 80)
print("E-ARŞİV PDF ANALİZİ ve VERİTABANI EŞLEŞTİRME")
print("=" * 80)
print(f"\nPDF: {pdf_path}\n")

# PDF'den metin çıkar
with open(pdf_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

print("1️⃣ PDF'DEN ETTN ÇIKARMA")
print("-" * 80)

# Debug: PDF metninin ETTN içeren kısmını göster
ettn_context = text[text.find('ETTN'):text.find('ETTN')+200] if 'ETTN' in text else "ETTN kelimesi bulunamadı"
print(f"ETTN bölgesi: {ettn_context}")

# ETTN pattern: 8-4-4-4-12 hex karakterler (boşluk ve farklı formatlar için esnek)
ettn_patterns = [
    r'ETTN[:\s]+([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})',
    r'ETTN[:\s]*([a-fA-F0-9]{8}\s*-\s*[a-fA-F0-9]{4}\s*-\s*[a-fA-F0-9]{4}\s*-\s*[a-fA-F0-9]{4}\s*-\s*[a-fA-F0-9]{12})',
    r'([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})',  # Sadece UUID pattern
]

ettn = None
for pattern in ettn_patterns:
    ettn_match = re.search(pattern, text)
    if ettn_match:
        ettn = ettn_match.group(1).replace(' ', '')  # Boşlukları temizle
        print(f"✅ ETTN bulundu: {ettn}")
        break

if not ettn:
    print("❌ ETTN bulunamadı!")
    print("\nPDF Metin İçeriği (ilk 2000 karakter):")
    print("-" * 80)
    print(text[:2000])
    print("-" * 80)
    sys.exit(1)

print("\n2️⃣ DİĞER BİLGİLERİ ÇIKARMA")
print("-" * 80)

# Fatura numarası
invoice_no_pattern = r'Fatura No[:\s]+(\S+)'
invoice_no_match = re.search(invoice_no_pattern, text)
invoice_no = invoice_no_match.group(1) if invoice_no_match else None
print(f"Fatura No: {invoice_no or 'Bulunamadı'}")

# Fatura tarihi
date_pattern = r'Fatura Tarihi[:\s]+([\d\-\.]+)\s+([\d:]+)'
date_match = re.search(date_pattern, text)
if date_match:
    invoice_date = date_match.group(1)
    invoice_time = date_match.group(2)
    print(f"Fatura Tarihi: {invoice_date} {invoice_time}")

# VKN/TCKN
tckn_pattern = r'TCKN[:\s]+(\d{11})'
tckn_match = re.search(tckn_pattern, text)
tckn = tckn_match.group(1) if tckn_match else None
print(f"TCKN: {tckn or 'Bulunamadı'}")

# Tedarikçi adı
# PDF'de genellikle en üstte büyük harfle yazılı
lines = text.split('\n')
supplier_name = None
for line in lines[:20]:  # İlk 20 satıra bak
    line = line.strip()
    if len(line) > 3 and line.isupper() and 'SAYIN' not in line and 'FATURA' not in line:
        # İlk büyük harf satır muhtemelen tedarikçi
        if not supplier_name:
            supplier_name = line
            break

print(f"Tedarikçi: {supplier_name or 'Bulunamadı'}")

# Tutar
amount_pattern = r'YALNIZ[:\s]*([A-ZİÜÖŞÇĞ\s]+)TL'
amount_match = re.search(amount_pattern, text)
if amount_match:
    amount_text = amount_match.group(1).strip()
    print(f"Tutar (yazıyla): {amount_text} TL")

print("\n3️⃣ VERİTABANINDA ETTN İLE ARAMA")
print("-" * 80)

db = next(get_db())

# ETTN ile ara
invoice = db.query(EInvoice).filter(EInvoice.invoice_uuid == ettn).first()

if invoice:
    print("✅ VERİTABANINDA BU FATURA MEVCUT!")
    print(f"\n   Veritabanı Kaydı:")
    print(f"   ID: {invoice.id}")
    print(f"   Fatura No: {invoice.invoice_number}")
    print(f"   UUID: {invoice.invoice_uuid}")
    print(f"   Gönderen: {invoice.supplier_name}")
    print(f"   VKN/TCKN: {invoice.supplier_tax_number}")
    print(f"   Tutar: {invoice.payable_amount:,.2f} {invoice.currency_code}")
    print(f"   Kategori: {invoice.invoice_category}")
    print(f"   Tarih: {invoice.issue_date}")
    
    # PDF bilgilerini karşılaştır
    print(f"\n   Karşılaştırma:")
    
    if invoice_no and invoice.invoice_number != invoice_no:
        print(f"   ⚠️  Fatura No uyumsuz: DB={invoice.invoice_number}, PDF={invoice_no}")
    else:
        print(f"   ✅ Fatura No eşleşiyor: {invoice.invoice_number}")
    
    if tckn and invoice.supplier_tax_number != tckn:
        print(f"   ⚠️  TCKN uyumsuz: DB={invoice.supplier_tax_number}, PDF={tckn}")
    else:
        print(f"   ✅ TCKN eşleşiyor: {invoice.supplier_tax_number}")
    
    print(f"\n   Bu PDF'i bu faturaya bağlayabilirsiniz!")
    
else:
    print("❌ VERİTABANINDA BU ETTN İLE FATURA BULUNAMADI")
    print("\n   Bu yeni bir fatura olabilir, PDF'den çıkarılan bilgiler:")
    print(f"   - Fatura No: {invoice_no}")
    print(f"   - ETTN: {ettn}")
    print(f"   - TCKN: {tckn}")
    print(f"   - Tedarikçi: {supplier_name}")
    print(f"\n   Bu bilgilerle yeni bir kayıt oluşturulabilir.")

# Fatura no ile de ara (eğer ETTN ile bulunamadıysa)
if not invoice and invoice_no:
    print(f"\n4️⃣ FATURA NO İLE ARAMA ({invoice_no})")
    print("-" * 80)
    
    invoice = db.query(EInvoice).filter(EInvoice.invoice_number == invoice_no).first()
    
    if invoice:
        print("✅ Fatura No ile bulundu!")
        print(f"   Ancak ETTN farklı:")
        print(f"   DB ETTN: {invoice.invoice_uuid}")
        print(f"   PDF ETTN: {ettn}")
        print(f"   ⚠️  Bu farklı faturalar olabilir!")
    else:
        print("❌ Fatura No ile de bulunamadı")

print("\n" + "=" * 80)
print("ÖZET")
print("=" * 80)
print(f"""
PDF Analizi: ✅ Başarılı
ETTN Çıkarma: {'✅ Başarılı' if ettn else '❌ Başarısız'}
Veritabanı Eşleştirme: {'✅ Bulundu' if invoice else '❌ Bulunamadı'}

SONRAKİ ADIMLAR:
1. PDF'i sisteme yükle
2. ETTN ile eşleştir
3. {'Mevcut kaydı güncelle' if invoice else 'Yeni kayıt oluştur'}
4. PDF dosya yolunu kaydet
""")
print("=" * 80)
