"""
E-Arşiv PDF Analizi - XSLT ve XML Çıkarma
"""
import sys
import os

# Direct path - simplified filename
pdf_path = r"C:\Projects\muhasebe-sistem\ilhan_imre.pdf"

print("=" * 80)
print("E-ARŞİV PDF ANALİZİ - XSLT ve XML Çıkarma")
print("=" * 80)
print(f"\nPDF Yolu: {pdf_path}")
print(f"Dosya mevcut mu: {os.path.exists(pdf_path)}")

if not os.path.exists(pdf_path):
    print("❌ Dosya bulunamadı!")
    sys.exit(1)

file_size = os.path.getsize(pdf_path)
print(f"Dosya boyutu: {file_size:,} bytes ({file_size/1024:.2f} KB)")

print("\n" + "=" * 80)
print("XSLT ve XML AÇIKLAMASI")
print("=" * 80)
print("""
XSLT (Extensible Stylesheet Language Transformations):
- XML'i başka bir formata (HTML, başka XML, metin) dönüştüren şablon dili
- Kendisi de XML formatındadır
- XSLT, XML VERİ içermez, sadece dönüştürme kurallarıdır

E-Arşiv Fatura Süreci:
1. XML (Orijinal Fatura Verisi) → Fatura bilgileri burada
2. XSLT (Dönüştürme Şablonu) → XML'i HTML'e çeviren kurallar
3. HTML (Görsel İçerik) → XSLT + XML = HTML çıktısı
4. PDF (Son Doküman) → HTML'den oluşturulan PDF

ÖNEMLI: XSLT'den XML ÇIKARILAMAZ!
- XSLT sadece dönüştürme kurallarıdır
- Veri, orijinal XML'dedir
- PDF oluşturulurken genellikle:
  a) Sadece HTML render edilip PDF'e çevrilir (XML kaybolur)
  b) Veya XML, PDF içine attachment olarak gömülür
""")

print("\n" + "=" * 80)
print("PDF İÇERİK ANALİZİ")
print("=" * 80)

try:
    import PyPDF2
    
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        num_pages = len(reader.pages)
        
        print(f"\n✅ PDF Bilgileri:")
        print(f"   Sayfa sayısı: {num_pages}")
        
        # Metadata
        if reader.metadata:
            print("\n   Metadata:")
            for key, value in reader.metadata.items():
                if isinstance(value, str) and len(value) < 300:
                    print(f"      {key}: {value}")
        
        # Attachments
        print("\n   Attachments Kontrolü:")
        if hasattr(reader, 'attachments') and reader.attachments:
            print(f"   ✅ {len(reader.attachments)} attachment bulundu:")
            for name, content in reader.attachments.items():
                print(f"      📎 {name} ({len(content):,} bytes)")
                if name.lower().endswith('.xml'):
                    print("         → Bu bir XML attachment! Çıkarılabilir.")
        else:
            print("   ⚠️  PDF'de attachment yok")
        
        # İlk sayfadan metin çıkar
        print("\n   İlk sayfa metin önizlemesi:")
        first_page = reader.pages[0]
        text = first_page.extract_text()
        print("   " + "-" * 76)
        print("   " + text[:800].replace('\n', '\n   '))
        print("   " + "-" * 76)

except Exception as e:
    print(f"❌ PDF okuma hatası: {e}")

print("\n" + "=" * 80)
print("BINARY İÇERİKTE XML ARAMA")
print("=" * 80)

try:
    with open(pdf_path, 'rb') as f:
        binary_content = f.read()
    
    # XML markerları ara
    xml_markers = {
        'XML Declaration': b'<?xml version',
        'Invoice Tag': b'<Invoice',
        'cac Namespace': b'<cac:',
        'cbc Namespace': b'<cbc:',
        'UBL Schema': b'urn:oasis:names:specification:ubl',
        'HTML Tag': b'<html',
        'XSLT Tag': b'<xsl:',
        'XSLT Namespace': b'xmlns:xsl',
    }
    
    print("\nXML/XSLT Marker Taraması:")
    found_markers = []
    for marker_name, marker_bytes in xml_markers.items():
        if marker_bytes in binary_content:
            # Marker'ın pozisyonunu bul
            pos = binary_content.find(marker_bytes)
            print(f"   ✅ {marker_name} bulundu (pozisyon: {pos:,})")
            found_markers.append(marker_name)
            
            # Marker etrafındaki 200 byte'ı göster
            start = max(0, pos - 50)
            end = min(len(binary_content), pos + 200)
            context = binary_content[start:end]
            try:
                context_str = context.decode('utf-8', errors='ignore')
                print(f"      Önizleme: {context_str[:150]}...")
            except:
                pass
        else:
            print(f"   ❌ {marker_name} bulunamadı")
    
    if 'XML Declaration' in found_markers:
        print("\n" + "=" * 80)
        print("XML ÇIKARMA DENEMESİ")
        print("=" * 80)
        
        # XML başlangıcını bul
        xml_start = binary_content.find(b'<?xml version')
        if xml_start == -1:
            xml_start = binary_content.find(b'<Invoice')
        
        if xml_start != -1:
            # XML bitişini bul - muhtemel kapanış tagları
            end_tags = [
                b'</Invoice>',
                b'</html>',
                b'</xsl:stylesheet>',
            ]
            
            xml_end = -1
            found_end_tag = None
            for end_tag in end_tags:
                pos = binary_content.find(end_tag, xml_start)
                if pos != -1:
                    if xml_end == -1 or pos < xml_end:
                        xml_end = pos
                        found_end_tag = end_tag
            
            if xml_end != -1:
                xml_end += len(found_end_tag)
                xml_bytes = binary_content[xml_start:xml_end]
                
                # XML'i kaydet
                base_name = os.path.splitext(pdf_path)[0]
                xml_output_path = base_name + '_extracted.xml'
                
                with open(xml_output_path, 'wb') as xml_f:
                    xml_f.write(xml_bytes)
                
                print(f"\n✅ XML/XSLT/HTML Çıkarıldı:")
                print(f"   Dosya: {xml_output_path}")
                print(f"   Boyut: {len(xml_bytes):,} bytes ({len(xml_bytes)/1024:.2f} KB)")
                print(f"   Başlangıç: {xml_start:,}")
                print(f"   Bitiş: {xml_end:,}")
                print(f"   Bitiş Tag: {found_end_tag.decode('utf-8', errors='ignore')}")
                
                # İçeriği analiz et
                try:
                    xml_str = xml_bytes.decode('utf-8', errors='ignore')
                    
                    # Ne tür bir XML?
                    if '<xsl:stylesheet' in xml_str or 'xmlns:xsl' in xml_str:
                        print("\n   📋 İçerik Tipi: XSLT (Dönüştürme Şablonu)")
                        print("      ⚠️  Bu XSLT'dir, fatura verisi içermez!")
                    elif '<Invoice' in xml_str and 'urn:oasis:names:specification:ubl' in xml_str:
                        print("\n   📋 İçerik Tipi: UBL-TR XML (Fatura Verisi)")
                        print("      ✅ Bu orijinal fatura XML'idir!")
                    elif '<html' in xml_str:
                        print("\n   📋 İçerik Tipi: HTML (Render Edilmiş)")
                        print("      ⚠️  Bu HTML'dir, muhtemelen XSLT ile üretilmiş")
                    else:
                        print("\n   📋 İçerik Tipi: Bilinmeyen XML")
                    
                    # İlk 1000 karakteri göster
                    print(f"\n   İlk 1000 karakter:")
                    print("   " + "-" * 76)
                    print("   " + xml_str[:1000].replace('\n', '\n   '))
                    print("   " + "-" * 76)
                    
                    # Eğer Invoice tag'i varsa, fatura bilgilerini çıkar
                    if '<Invoice' in xml_str:
                        print("\n   🔍 Fatura Bilgilerini Arama:")
                        
                        import re
                        
                        # Fatura numarası
                        invoice_no_match = re.search(r'<cbc:ID>([^<]+)</cbc:ID>', xml_str)
                        if invoice_no_match:
                            print(f"      Fatura No: {invoice_no_match.group(1)}")
                        
                        # UUID
                        uuid_match = re.search(r'<cbc:UUID>([^<]+)</cbc:UUID>', xml_str)
                        if uuid_match:
                            print(f"      UUID: {uuid_match.group(1)}")
                        
                        # Tarih
                        date_match = re.search(r'<cbc:IssueDate>([^<]+)</cbc:IssueDate>', xml_str)
                        if date_match:
                            print(f"      Fatura Tarihi: {date_match.group(1)}")
                        
                        # Tutar
                        amount_match = re.search(r'<cbc:PayableAmount[^>]*>([^<]+)</cbc:PayableAmount>', xml_str)
                        if amount_match:
                            print(f"      Ödenecek Tutar: {amount_match.group(1)}")
                        
                except Exception as e:
                    print(f"   ⚠️  XML parse hatası: {e}")
            else:
                print("\n   ⚠️  XML bitiş tag'i bulunamadı")
    
except Exception as e:
    print(f"❌ Binary analiz hatası: {e}")

print("\n" + "=" * 80)
print("ÖZET ve ÖNERİLER")
print("=" * 80)
print("""
E-ARŞİV PDF'LERİNDEN VERİ ÇIKARMA:

1. ✅ YAPILABİLİR İŞLER:
   • PDF içinde gömülü XML attachment çıkarma
   • PDF binary içinden XML extraction (eğer varsa)
   • PDF'den metin çıkarıp parse etme (OCR benzeri)
   • PDF metadata okuma

2. ❌ YAPILAMAYAN İŞLER:
   • XSLT'den XML üretme (XSLT sadece dönüştürme kuralıdır)
   • HTML'den orijinal XML'e geri dönme (veri kaybı olur)
   • PDF'den %100 kesin XML restoration

3. 📋 XSLT NEDİR:
   • XML → HTML/PDF dönüştürme şablonu
   • Kendisi XML formatında ama VERİ içermez
   • <xsl:template>, <xsl:value-of> gibi komutlar içerir
   • Orijinal fatura verileri XSLT'de DEĞİL, kaynak XML'dedir

4. 💡 ÖNERİLER:
   • E-arşiv XML'leri varsa onları kullan (en doğru veri)
   • PDF'de gömülü XML varsa çıkar ve kullan
   • XML yoksa PDF'den metin parse et (hata payı olabilir)
   • Kritik işlemler için XML'leri tedarikçiden/GIB'den talep et

5. 🔧 UYGULAMA STRATEJİSİ:
   a) Önce PDF'de attachment XML ara
   b) Yoksa binary içinden XML extraction dene
   c) Yoksa PDF'den metin çıkarıp regex/parse kullan
   d) Önemli: Her zaman veri doğrulaması yap!
""")
print("=" * 80)
