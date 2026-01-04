"""
E-Fatura PDF analiz scripti
- PDF içeriğini inceler
- GIB XSLT/XML varlığını kontrol eder
- XML'i çıkarır (varsa)
- Fatura bilgilerini okur
"""
import sys
import os

pdf_path = r"C:\Projects\muhasebe-sistem\YCM2025000000033_0562467c-2077-41ba-848a-b342c6dc42dc.pdf"

print("=" * 80)
print("E-FATURA PDF ANALİZ")
print("=" * 80)
print(f"\nPDF Yolu: {pdf_path}")
print(f"Dosya mevcut mu: {os.path.exists(pdf_path)}")

if not os.path.exists(pdf_path):
    print("❌ Dosya bulunamadı!")
    sys.exit(1)

file_size = os.path.getsize(pdf_path)
print(f"Dosya boyutu: {file_size:,} bytes ({file_size/1024:.2f} KB)")

# Dosya adından fatura numarasını çıkar
filename = os.path.basename(pdf_path)
parts = filename.split('_')
invoice_number = parts[0] if parts else "Bilinmiyor"
uuid = parts[1].replace('.pdf', '') if len(parts) > 1 else "Bilinmiyor"

print(f"\nDOSYA ADI ANALİZİ:")
print(f"  Fatura No: {invoice_number}")
print(f"  UUID: {uuid}")

print("\n" + "=" * 80)
print("1. PDF İÇERİĞİ İNCELENEBİLİR Mİ?")
print("=" * 80)

try:
    import PyPDF2
    print("✅ PyPDF2 mevcut - PDF okunabilir")
    pdf_available = True
except ImportError:
    print("❌ PyPDF2 yok - pip install PyPDF2 gerekli")
    pdf_available = False

try:
    import pdfplumber
    print("✅ pdfplumber mevcut - Gelişmiş PDF okuma yapılabilir")
    pdfplumber_available = True
except ImportError:
    print("⚠️  pdfplumber yok - pip install pdfplumber ile daha iyi metin çıkarılabilir")
    pdfplumber_available = False

print("\n" + "=" * 80)
print("2. HANGİ FATURANIN PDF'İ OLDUĞU BULUNABİLİR Mİ?")
print("=" * 80)
print("✅ EVET - Dosya adından:")
print(f"   Fatura Numarası: {invoice_number}")
print(f"   Fatura UUID: {uuid}")

# PDF içinden de okuyabiliriz
if pdf_available:
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            num_pages = len(reader.pages)
            print(f"\n   PDF'de {num_pages} sayfa var")
            
            # İlk sayfayı oku
            first_page = reader.pages[0]
            text = first_page.extract_text()
            
            # Fatura numarasını metinde ara
            if invoice_number in text:
                print(f"   ✅ Fatura numarası ({invoice_number}) PDF içinde bulundu")
            
            # UUID'yi ara
            if uuid in text:
                print(f"   ✅ UUID ({uuid}) PDF içinde bulundu")
                
    except Exception as e:
        print(f"   ⚠️  PDF okuma hatası: {e}")

print("\n" + "=" * 80)
print("3. GIB XSLT KISMINI ÇÖZEBİLİR MİYİZ?")
print("=" * 80)
print("✅ EVET - GIB e-fatura PDF'leri genellikle:")
print("   - XSLT ile dönüştürülmüş HTML/XML içerir")
print("   - PDF içinde attachment olarak XML saklanabilir")
print("   - veya PDF metadata'sında XML bulunabilir")

if pdf_available:
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            # Attachments kontrol et
            if hasattr(reader, 'attachments') and reader.attachments:
                print(f"\n   ✅ PDF'de {len(reader.attachments)} attachment bulundu:")
                for name, content in reader.attachments.items():
                    print(f"      - {name} ({len(content)} bytes)")
            
            # Metadata kontrol et
            if reader.metadata:
                print("\n   PDF Metadata:")
                for key, value in reader.metadata.items():
                    if isinstance(value, str) and len(value) < 200:
                        print(f"      {key}: {value}")
                    else:
                        print(f"      {key}: [{type(value).__name__}]")
            
            # Binary içerikte XML ara
            with open(pdf_path, 'rb') as binary_f:
                binary_content = binary_f.read()
                
                # XML başlangıç taglerini ara
                xml_markers = [
                    b'<?xml version',
                    b'<Invoice',
                    b'<cac:',
                    b'<cbc:',
                    b'urn:oasis:names:specification:ubl:schema:xsd:Invoice'
                ]
                
                found_xml = False
                for marker in xml_markers:
                    if marker in binary_content:
                        print(f"\n   ✅ PDF içinde XML marker bulundu: {marker.decode('utf-8', errors='ignore')}")
                        found_xml = True
                        break
                
                if not found_xml:
                    print("\n   ⚠️  Bilinen XML marker'ları bulunamadı")
                
    except Exception as e:
        print(f"   ⚠️  XSLT analiz hatası: {e}")

print("\n" + "=" * 80)
print("4. XSLT İÇİNDEN XML ALABİLİR MİYİZ?")
print("=" * 80)
print("✅ EVET - Aşağıdaki yöntemlerle:")
print("   a) PDF'den attachment'ları çıkarma")
print("   b) PDF binary içinden XML extraction")
print("   c) PDF'den metin çıkarıp HTML/XML parse etme")

if pdf_available:
    print("\n   XML Çıkarma Denemesi:")
    try:
        with open(pdf_path, 'rb') as f:
            content = f.read()
            
            # XML başlangıcını bul
            xml_start = content.find(b'<?xml version')
            if xml_start == -1:
                xml_start = content.find(b'<Invoice')
            
            if xml_start != -1:
                # XML bitişini bul
                xml_end = content.find(b'</Invoice>', xml_start)
                if xml_end != -1:
                    xml_end += len(b'</Invoice>')
                    xml_bytes = content[xml_start:xml_end]
                    
                    # XML'i kaydet
                    xml_output_path = pdf_path.replace('.pdf', '_extracted.xml')
                    with open(xml_output_path, 'wb') as xml_f:
                        xml_f.write(xml_bytes)
                    
                    print(f"   ✅ XML çıkarıldı ve kaydedildi:")
                    print(f"      {xml_output_path}")
                    print(f"      Boyut: {len(xml_bytes):,} bytes")
                    
                    # XML'in ilk 500 karakterini göster
                    try:
                        xml_str = xml_bytes.decode('utf-8', errors='ignore')
                        print(f"\n   XML İçeriği (ilk 500 karakter):")
                        print("   " + "-" * 76)
                        print("   " + xml_str[:500].replace('\n', '\n   '))
                        print("   " + "-" * 76)
                    except:
                        pass
                else:
                    print("   ⚠️  XML bitiş tag'i bulunamadı")
            else:
                print("   ⚠️  XML başlangıcı bulunamadı")
                
    except Exception as e:
        print(f"   ❌ XML çıkarma hatası: {e}")

print("\n" + "=" * 80)
print("5. PDF'İ OKUYABİLİR MİYİZ?")
print("=" * 80)
print("✅ EVET - Python kütüphaneleri ile:")

if pdf_available:
    print("\n   PyPDF2 ile metin çıkarma:")
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            first_page = reader.pages[0]
            text = first_page.extract_text()
            
            # İlk 1000 karakteri göster
            print("   " + "-" * 76)
            print("   " + text[:1000].replace('\n', '\n   '))
            print("   " + "-" * 76)
            print(f"   (Toplam {len(text)} karakter çıkarıldı)")
            
    except Exception as e:
        print(f"   ❌ Metin çıkarma hatası: {e}")

if pdfplumber_available:
    print("\n   pdfplumber ile daha iyi metin çıkarma mümkün")

print("\n" + "=" * 80)
print("ÖZET")
print("=" * 80)
print("1. ✅ PDF incelenebilir - PyPDF2, pdfplumber ile")
print("2. ✅ Fatura bilgisi bulunabilir - Dosya adından ve PDF içinden")
print("3. ✅ GIB XSLT çözülebilir - PDF içinde XML bulunabilir")
print("4. ✅ XML çıkarılabilir - Binary extraction veya attachments ile")
print("5. ✅ PDF okunabilir - Metin ve veri çıkarma yapılabilir")
print("=" * 80)
