"""
GIB E-ARŞİV PAKET ANALİZİ ve PDF İLİŞKİSİ
Kaynak: earsiv_paket_v1.1_6 XSD dosyaları
"""

print("=" * 100)
print("GIB E-ARŞİV PAKET YAPISI ANALİZİ")
print("=" * 100)

print("""
📦 E-ARŞİV PAKET İÇERİĞİ (GIB Resmi Standartları)
================================================

E-arşiv faturalar GIB'e rapor edilirken aşağıdaki yapıda gönderilir:

1. eArsivRaporu.xml (Ana Rapor Dosyası)
   ├── baslik (Rapor başlık bilgileri)
   └── fatura[] (Fatura listesi)
       ├── faturaNo: Fatura numarası (örn: GIB2025000000016)
       ├── faturaUUID: ETTN (örn: 856fdb6f-bb17-411c-930c-fedd0b5465db)
       ├── faturaTip: SATIS/IADE/TEVKIFAT/ISTISNA/OZELMATRAH
       ├── gonderimSekli: KAGIT / ELEKTRONIK
       ├── dosyaAdi: PDF dosya adı (örn: "GIB2025000000016.pdf")
       ├── ozetDeger: PDF'in hash değeri (özet)
       ├── duzenlenmeTarihi: Fatura tarihi
       ├── duzenlenmeZamani: Fatura saati
       ├── toplamTutar: Toplam tutar
       ├── toplamIskonto: İskonto
       ├── odenecekTutar: Ödenecek tutar
       ├── paraBirimi: TRY/USD/EUR vb.
       ├── dovizKuru: Döviz kuru
       ├── faturaUrl: PDF'in URL'i (GIB sunucusunda)
       ├── vergiBilgisi: KDV detayları
       └── aliciBilgileri: Müşteri bilgileri

2. PDF Dosyaları (Her fatura için ayrı)
   - GIB2025000000016.pdf
   - GIB2025000000017.pdf
   - ...

3. XML Fatura Dosyaları (Opsiyonel - ELEKTRONIK gönderimde)
   - GIB2025000000016.xml (UBL-TR formatında)
   - GIB2025000000017.xml
   - ...
""")

print("\n" + "=" * 100)
print("ÖNEMLI BULGULAR - PDF ve XML İLİŞKİSİ")
print("=" * 100)

print("""
✅ ÇOK ÖNEMLİ KEŞİF:
==================

E-arşiv paketinde her fatura için 3 dosya olabilir:

1. RAPOR XML (eArsivRaporu.xml)
   - Tüm faturaların özet bilgileri
   - PDF dosya adları (dosyaAdi)
   - ETTN'ler (faturaUUID)
   - Tutar bilgileri
   - PDF hash değerleri (ozetDeger)
   - **PDF URL'leri (faturaUrl)**

2. PDF DOSYALARI
   - Görsel fatura (render edilmiş HTML)
   - İçinde UBL-TR XML YOK (genellikle)
   - Sadece görselleştirilmiş veri

3. XML FATURA DOSYALARI (Eğer ELEKTRONIK gönderim ise)
   - UBL-TR formatında tam XML
   - Tüm fatura detayları
   - Dijital imza
   - **Bu XML'den her şey çıkarılabilir**

BAĞLANTI KURMA STRATEJİSİ:
=========================

Senaryo 1: E-arşiv Rapor XML'i Varsa
------------------------------------
eArsivRaporu.xml içinden:
- faturaNo → Fatura numarası
- faturaUUID → ETTN (PDF'deki ETTN ile eşleştir)
- dosyaAdi → PDF dosya adı
- faturaUrl → GIB'deki PDF URL'i
- Tüm diğer fatura bilgileri doğrudan rapor XML'inde

Senaryo 2: Sadece PDF Varsa
---------------------------
PDF'den metin çıkar:
- ETTN (856fdb6f-bb17-411c-930c-fedd0b5465db)
- Fatura No (GIB2025000000016)
- Bu bilgilerle GIB web servisi üzerinden:
  * E-arşiv rapor XML indir
  * veya UBL-TR XML indir (eğer ELEKTRONIK gönderim ise)

Senaryo 3: PDF + XML Paketi Varsa (İDEAL)
-----------------------------------------
1. PDF dosya adından fatura no al: "GIB2025000000016.pdf" → "GIB2025000000016"
2. Aynı isme sahip XML dosyasını bul: "GIB2025000000016.xml"
3. XML'i UBL-TR parser ile işle (zaten sisteminizde var)
4. PDF'i sadece görselleştirme/arşiv için sakla
""")

print("\n" + "=" * 100)
print("UYGULAMA ÖNERİLERİ - SİSTEMİNİZ İÇİN")
print("=" * 100)

print("""
💡 Öneri 1: E-arşiv Rapor XML Parser
===================================
Tedarikçilerden PDF yerine "e-arşiv paket ZIP" talep edin:
- eArsivRaporu.xml (tüm fatura özet bilgileri)
- *.pdf dosyaları
- *.xml dosyaları (varsa)

Parser:
```python
def parse_earsiv_rapor(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    for fatura in root.findall('.//fatura'):
        invoice_data = {
            'invoice_number': fatura.find('faturaNo').text,
            'uuid': fatura.find('faturaUUID').text,
            'pdf_filename': fatura.find('dosyaAdi').text,
            'pdf_hash': fatura.find('ozetDeger').text,
            'pdf_url': fatura.find('faturaUrl').text,
            'issue_date': fatura.find('duzenlenmeTarihi').text,
            'issue_time': fatura.find('duzenlenmeZamani').text,
            'total_amount': fatura.find('toplamTutar').text,
            'payable_amount': fatura.find('odenecekTutar').text,
            'currency': fatura.find('paraBirimi').text,
            # ... diğer alanlar
        }
        
        # PDF dosyasını bul ve eşleştir
        pdf_path = find_pdf_by_name(invoice_data['pdf_filename'])
        
        # XML varsa onu da bul
        xml_filename = invoice_data['pdf_filename'].replace('.pdf', '.xml')
        xml_path = find_xml_by_name(xml_filename)
        
        if xml_path:
            # UBL-TR XML'i parse et (en doğru veri)
            invoice_data.update(parse_ubl_xml(xml_path))
        
        save_to_database(invoice_data)
```

💡 Öneri 2: PDF + ETTN Eşleştirme
=================================
Eğer sadece PDF geliyor ise:

```python
def match_pdf_with_database(pdf_path):
    # PDF'den ETTN çıkar
    text = extract_text_from_pdf(pdf_path)
    ettn = extract_ettn_from_text(text)  # Regex ile
    
    # Veritabanında ETTN ile ara
    invoice = db.query(EInvoice).filter(
        EInvoice.invoice_uuid == ettn
    ).first()
    
    if invoice:
        # PDF'i faturaya bağla
        invoice.pdf_file_path = pdf_path
        db.commit()
    else:
        # Yeni fatura olarak PDF'den parse et
        invoice_data = parse_pdf_text(text)
        create_invoice(invoice_data)
```

💡 Öneri 3: GIB Web Servisi Entegrasyonu
========================================
ETTN ile XML indirme:

```python
from zeep import Client

def download_earsiv_xml(ettn):
    wsdl = 'https://earsivwstest.efatura.gov.tr/...'
    client = Client(wsdl)
    
    # GIB'den e-arşiv XML indir
    response = client.service.getEArsivInvoice(
        uuid=ettn,
        username='kullanici',
        password='sifre'
    )
    
    return response.invoice_xml
```

💡 Öneri 4: Dosya Adı Standardı
===============================
E-arşiv PDF ve XML'leri şu formatta kaydedin:

Format: {FATURA_NO}_{ETTN}.{pdf|xml}
Örnek: GIB2025000000016_856fdb6f-bb17-411c-930c-fedd0b5465db.pdf
       GIB2025000000016_856fdb6f-bb17-411c-930c-fedd0b5465db.xml

Bu sayede:
- PDF ve XML kolayca eşleşir
- ETTN dosya adından okunabilir
- Veritabanı sorgulaması kolay

💡 Öneri 5: Hibrit Veri Kaynağı
===============================
```python
def import_earsiv_invoice(files):
    # Öncelik sırası:
    
    # 1. UBL-TR XML varsa (en doğru)
    if xml_file:
        data = parse_ubl_xml(xml_file)
        data['pdf_path'] = pdf_file
        return data
    
    # 2. E-arşiv Rapor XML varsa (özet veri)
    elif earsiv_rapor_xml:
        data = parse_earsiv_rapor_xml(earsiv_rapor_xml)
        data['pdf_path'] = pdf_file
        return data
    
    # 3. Sadece PDF varsa (metin parse)
    elif pdf_file:
        data = parse_pdf_text(pdf_file)
        data['source'] = 'PDF_PARSE'
        data['needs_verification'] = True
        return data
    
    # 4. GIB web servisi (son çare)
    else:
        ettn = extract_ettn_from_pdf(pdf_file)
        data = download_from_gib(ettn)
        return data
```
""")

print("\n" + "=" * 100)
print("SONUÇ ve AKSİYON PLANI")
print("=" * 100)

print("""
✅ EVET, PDF İLE BAĞLANTI KURABİLİRİZ!
=====================================

E-arşiv paket yapısında:
1. ✅ dosyaAdi → PDF dosya adı (eArsivRaporu.xml'de)
2. ✅ faturaUUID → ETTN (hem rapor XML'de hem PDF'de)
3. ✅ faturaUrl → PDF'in GIB URL'i
4. ✅ ozetDeger → PDF hash (doğrulama için)

BAĞLANTI YÖNTEM LERİ:
====================
1. E-arşiv Rapor XML → PDF (dosyaAdi ile)
2. ETTN → PDF (PDF metin içinden ETTN çıkarıp eşleştirme)
3. Fatura No → PDF (dosya adı standardı ile)
4. GIB Web Servisi → ETTN ile XML/PDF indirme

ÖNERİLEN UYGULAMA:
==================
1. Tedarikçilerden e-arşiv paket ZIP talep et (rapor XML + PDF + XML)
2. eArsivRaporu.xml parser ekle
3. PDF ve XML eşleştirme sistemi kur
4. PDF'den ETTN çıkarma fonksiyonu ekle
5. GIB web servisi entegrasyonu (gelecek için)

HEMEN ŞİMDİ YAPILABİLECEKLER:
============================
1. PDF'den ETTN çıkarma (regex ile) ✅ Basit
2. ETTN ile veritabanı eşleştirme ✅ Basit
3. E-arşiv rapor XML parser ⚠️ Orta zorluk
4. GIB web servisi entegrasyonu ❌ Karmaşık (yetkilendirme)

Başlangıç için Seçenek 1-2 ile başlamanızı öneririm!
""")

print("\n" + "=" * 100)
