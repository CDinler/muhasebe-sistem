"""
KENDİ HAZIRLANAN E-ARŞİV FATURA ANALİZİ
PDF'den XML çıkarma ve XML içindeki XSLT decode etme
"""
import sys
import base64
import xml.etree.ElementTree as ET

try:
    import PyPDF2
    import pdfplumber
except:
    print("❌ Gerekli kütüphaneler yok!")
    sys.exit(1)

pdf_path = r"C:\Projects\muhasebe-sistem\ff2188f5-a623-4cff-a3e9-3c39c3369ab4.pdf"
xml_path = r"C:\Projects\muhasebe-sistem\END2025000000001_c017486c-b380-4397-b062-06c30ca1d95b.xml"

print("=" * 100)
print("KENDİ E-ARŞİV FATURAMIZI ANALİZ EDELİM")
print("=" * 100)

# ============================================================================
# BÖLÜM 1: PDF İÇİNDE XML VAR MI?
# ============================================================================
print("\n📄 BÖLÜM 1: PDF İÇİNDE GÖMÜLÜ XML KONTROLÜ")
print("=" * 100)

with open(pdf_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    
    print(f"Sayfa sayısı: {len(reader.pages)}")
    print(f"PDF metadata: {reader.metadata}")
    print()
    
    # 1. Attachments kontrolü
    print("🔍 PDF Attachments Kontrolü:")
    if '/Names' in reader.trailer['/Root']:
        names = reader.trailer['/Root']['/Names']
        if '/EmbeddedFiles' in names:
            print("✅ PDF içinde embedded files var!")
            embedded = names['/EmbeddedFiles']
            print(f"Embedded files: {embedded}")
        else:
            print("❌ EmbeddedFiles yok")
    else:
        print("❌ Names dictionary yok")
    
    # 2. Binary içerikte XML arama
    print("\n🔍 Binary İçerik Taraması:")
    
    # PDF'in tüm binary içeriğini al
    f.seek(0)
    pdf_binary = f.read()
    
    # XML işaretleri ara
    xml_markers = [
        b'<?xml',
        b'<Invoice',
        b'<cac:',
        b'<cbc:',
        b'urn:oasis:names:specification:ubl:schema',
    ]
    
    found_markers = []
    for marker in xml_markers:
        if marker in pdf_binary:
            count = pdf_binary.count(marker)
            found_markers.append((marker.decode('latin1'), count))
            print(f"✅ '{marker.decode('latin1')}' bulundu: {count} kez")
    
    if not found_markers:
        print("❌ XML işareti bulunamadı")
    
    # 3. XML extraction denemesi
    if found_markers:
        print("\n🔧 XML Çıkarma Denemesi:")
        
        # <?xml ile başlayan kısımları bul
        xml_start = pdf_binary.find(b'<?xml')
        if xml_start != -1:
            print(f"✅ XML başlangıcı bulundu: pozisyon {xml_start}")
            
            # XML'in bitişini bul (</Invoice> gibi)
            xml_end_markers = [b'</Invoice>', b'</inv:Invoice>']
            xml_end = -1
            
            for end_marker in xml_end_markers:
                pos = pdf_binary.find(end_marker, xml_start)
                if pos != -1:
                    xml_end = pos + len(end_marker)
                    print(f"✅ XML bitişi bulundu: {end_marker.decode('latin1')}")
                    break
            
            if xml_end != -1:
                # XML'i çıkar
                xml_content = pdf_binary[xml_start:xml_end]
                
                print(f"\n📋 Çıkarılan XML Boyutu: {len(xml_content)} bytes")
                print(f"İlk 500 karakter:")
                print("-" * 100)
                print(xml_content[:500].decode('utf-8', errors='ignore'))
                print("-" * 100)
                
                # Dosyaya kaydet
                output_path = r"C:\Projects\muhasebe-sistem\backend\data\earsiv_from_pdf\extracted_from_pdf.xml"
                with open(output_path, 'wb') as xml_file:
                    xml_file.write(xml_content)
                print(f"\n💾 XML kaydedildi: {output_path}")
            else:
                print("❌ XML bitişi bulunamadı")
        else:
            print("❌ XML başlangıcı bulunamadı")

# ============================================================================
# BÖLÜM 2: XML İÇİNDEKİ XSLT DECODE
# ============================================================================
print("\n\n📋 BÖLÜM 2: XML İÇİNDEKİ XSLT ANALİZİ")
print("=" * 100)

# XML'i parse et
tree = ET.parse(xml_path)
root = tree.getroot()

# Namespace tanımları
namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
}

print("🔍 XML Root Element:")
print(f"  Tag: {root.tag}")
print(f"  Attributes: {root.attrib}")

# Attachment bul
print("\n🔍 Attachment Arama:")
attachments = root.findall('.//cac:Attachment', namespaces)

if not attachments:
    print("❌ cac:Attachment bulunamadı, namespace'siz deniyorum...")
    # Namespace olmadan dene
    for elem in root.iter():
        if 'Attachment' in elem.tag:
            attachments.append(elem)
            print(f"✅ Bulundu: {elem.tag}")

print(f"\nToplam {len(attachments)} attachment bulundu\n")

for idx, attachment in enumerate(attachments, 1):
    print(f"{'=' * 100}")
    print(f"ATTACHMENT #{idx}")
    print(f"{'=' * 100}")
    
    # EmbeddedDocumentBinaryObject bul
    for child in attachment:
        if 'EmbeddedDocumentBinaryObject' in child.tag:
            print(f"\n📦 EmbeddedDocumentBinaryObject bulundu!")
            print(f"Tag: {child.tag}")
            print(f"\nAttributes:")
            for attr, value in child.attrib.items():
                print(f"  {attr}: {value}")
            
            # Base64 içeriği
            base64_content = child.text
            if base64_content:
                base64_content = base64_content.strip()
                print(f"\nBase64 İçerik Boyutu: {len(base64_content)} karakter")
                print(f"İlk 100 karakter: {base64_content[:100]}")
                
                # Base64 decode
                try:
                    decoded = base64.b64decode(base64_content)
                    print(f"\n✅ Base64 Decode Başarılı!")
                    print(f"Decode Boyutu: {len(decoded)} bytes")
                    
                    # Dosya tipini anla
                    filename = child.attrib.get('filename', 'unknown')
                    mime = child.attrib.get('mimeCode', 'unknown')
                    
                    print(f"\nDosya Bilgileri:")
                    print(f"  Filename: {filename}")
                    print(f"  MIME Type: {mime}")
                    
                    # İçeriği göster
                    print(f"\nDecode Edilmiş İçerik (ilk 1000 karakter):")
                    print("-" * 100)
                    decoded_text = decoded.decode('utf-8', errors='ignore')
                    print(decoded_text[:1000])
                    print("-" * 100)
                    
                    # XSLT ise kaydet
                    if 'xslt' in filename.lower() or 'xsl' in filename.lower():
                        output_xslt = r"C:\Projects\muhasebe-sistem\backend\data\earsiv_from_pdf\decoded_xslt.xslt"
                        with open(output_xslt, 'wb') as xslt_file:
                            xslt_file.write(decoded)
                        print(f"\n💾 XSLT kaydedildi: {output_xslt}")
                        print(f"   Boyut: {len(decoded)} bytes ({len(decoded)/1024:.1f} KB)")
                    
                    # PDF ise kaydet
                    if mime == 'application/pdf' or filename.endswith('.pdf'):
                        output_pdf = f"C:\\Projects\\muhasebe-sistem\\backend\\data\\earsiv_from_pdf\\decoded_{filename}"
                        with open(output_pdf, 'wb') as pdf_file:
                            pdf_file.write(decoded)
                        print(f"\n💾 PDF kaydedildi: {output_pdf}")
                    
                except Exception as e:
                    print(f"\n❌ Base64 decode hatası: {e}")
            else:
                print("\n⚠️ Base64 içerik boş!")

# ============================================================================
# BÖLÜM 3: XSLT NEDİR? NE İŞE YARAR?
# ============================================================================
print("\n\n📚 BÖLÜM 3: XSLT (eXtensible Stylesheet Language Transformations)")
print("=" * 100)

print("""
XSLT NEDİR?
===========
XSLT, XML verilerini başka bir formata dönüştürmek için kullanılan bir dildir.
E-Fatura/E-Arşiv sisteminde, XML verisini görsel PDF'e dönüştürmek için kullanılır.

NASIL ÇALIŞIR?
==============
1. GİB, standart bir XSLT şablonu sağlar
2. E-Fatura XML'i + XSLT → PDF dönüşümü yapılır
3. XSLT, XML'deki verileri okuyup HTML/PDF formatına yerleştirir

NEDEN XML'E GÖMÜLÜ?
===================
- GİB'e gönderilen XML paketi, hem veriyi hem de görsel şablonu içerir
- Alıcı taraf, aynı XSLT ile PDF'i yeniden oluşturabilir
- Standardizasyon: Herkes aynı XSLT'yi kullanır

XML İÇİNDE XSLT OLMASININ FAYDALARI:
====================================
✅ Self-contained: XML dosyası kendi başına yeterli
✅ Taşınabilir: XSLT harici dosya olarak aranmaz
✅ Versiyonlama: Her XML kendi XSLT versiyonunu taşır
✅ Güvenlik: XSLT değiştirilmemiş olduğu doğrulanabilir

XSLT'DEN NE ÇIKARTABİLİRİZ?
===========================
❌ VERİ çıkartamayız - XSLT sadece şablon
✅ TASARIM bilgilerini görebiliriz
✅ HANGİ ALANLARIN gösterileceğini görebiliriz
✅ PDF OLUŞTURMA mantığını anlayabiliriz

ÖNEMLİ NOT:
===========
PDF'de gördüğünüz veriler = XML'deki <cbc:> ve <cac:> elementlerinden gelir
XSLT sadece "bu veriyi şurada göster" kurallarını içerir.

ÖRNEK XSLT KODU:
================
<xsl:value-of select="cbc:InvoiceNumber"/>
→ Bu kod, XML'deki InvoiceNumber elementini PDF'e yazdırır

<xsl:for-each select="cac:InvoiceLine">
→ Bu kod, her fatura satırı için tekrarlar

SONRASİNDA NE YAPALIM?
=====================
1. XSLT'yi decode ettik ✅
2. XSLT'yi inceleyebiliriz (tasarım kuralları)
3. Kendi PDF'mizi oluşturmak için kullanabiliriz
4. Ancak VERİLER için yine XML'i parse etmemiz gerek
""")

# ============================================================================
# BÖLÜM 4: PDF vs XML KARŞILAŞTIRMASI
# ============================================================================
print("\n\n⚖️ BÖLÜM 4: PDF vs XML - HANGİSİNİ KULLANMALIYIZ?")
print("=" * 100)

print("""
SENARYO 1: İKİSİ DE VAR (Bizim durum)
======================================
XML Dosyası: ✅ Var
PDF Dosyası: ✅ Var

ÖNERİ: XML'İ KULLAN!
--------------------
✅ Structured data - kolay parse
✅ Tüm alanlar mevcut
✅ KDV hesaplamaları, satır kalemleri, vs. hepsi var
✅ Standart format (UBL-TR 2.1)
❌ PDF parse etmeye gerek YOK


SENARYO 2: SADECE PDF VAR
=========================
XML Dosyası: ❌ Yok
PDF Dosyası: ✅ Var

DURUM 1: PDF içinde XML gömülü
-------------------------------
Yaptığımız gibi PDF'den XML'i extract et
Sonra XML'i parse et

DURUM 2: PDF içinde XML yok
----------------------------
pdfplumber ile text extraction
Regex ile data parsing
Bizim pdf_to_gib_xml.py gibi


SENARYO 3: SADECE XML VAR
=========================
XML Dosyası: ✅ Var
PDF Dosyası: ❌ Yok

PDF'e ihtiyaç varsa:
1. XML + XSLT → PDF oluştur
2. XSLT decode et (yaptığımız gibi)
3. XSLT transformation engine kullan (Java Saxon, Python lxml)
4. Ya da basit HTML render + PDF export


SİSTEMİNİZ İÇİN ÖNERİ:
======================
1. XML varsa → XML'i import et (UBL parser kullan)
2. XML yoksa → PDF parse et (pdfplumber + regex)
3. İkisi de varsa → XML öncelikli, PDF backup
4. XSLT'yi sakla → İleride PDF oluşturmak için
""")

print("\n" + "=" * 100)
print("ANALİZ TAMAMLANDI")
print("=" * 100)
