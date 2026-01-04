"""
PRATIK PDF SATIR BİLGİSİ ÇIKARMA
GİB E-Arşiv Faturalarından Satır Kalemleri (Line Items) Çıkarma
"""
import sys
import re
from decimal import Decimal

try:
    import pdfplumber
except:
    print("❌ pdfplumber gerekli!")
    print("pip install pdfplumber")
    sys.exit(1)

def clean_amount(text):
    """Türkçe sayı formatını decimal'e çevir: 1.234,56 → 1234.56"""
    if not text:
        return None
    
    # "1.234,56 TL" → "1.234,56"
    text = text.replace(' TL', '').replace('TL', '').strip()
    
    # "1.234,56" → "1234.56"
    text = text.replace('.', '').replace(',', '.')
    
    try:
        return Decimal(text)
    except:
        return None

def extract_invoice_lines(pdf_path):
    """PDF'den fatura satır kalemleri çıkar"""
    
    print("=" * 100)
    print(f"📄 PDF Analiz: {pdf_path}")
    print("=" * 100)
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        
        if not tables:
            print("❌ Tablo bulunamadı")
            return []
        
        print(f"\n✅ {len(tables)} tablo bulundu\n")
        
        # Fatura satırları tablosunu bul (en büyük tablo genellikle)
        invoice_table = None
        for table in tables:
            # Tablo en az 10 satır olmalı (header + 9 item + footer)
            if len(table) > 10:
                # "Sıra No" veya "Mal Hizmet" başlığı var mı kontrol et
                header_row = table[0]
                header_text = ' '.join([str(cell) for cell in header_row if cell])
                
                if 'Sıra' in header_text or 'Mal Hizmet' in header_text:
                    invoice_table = table
                    break
        
        if not invoice_table:
            print("❌ Fatura satırları tablosu bulunamadı")
            return []
        
        print(f"📊 Fatura Tablosu Bulundu: {len(invoice_table)} satır\n")
        
        # Başlık satırı
        headers = invoice_table[0]
        print("Başlıklar:")
        for i, h in enumerate(headers):
            if h:
                print(f"  [{i}] {h}")
        
        print("\n" + "-" * 100)
        print("FATURA SATIR KALEMLERİ")
        print("-" * 100)
        
        line_items = []
        
        # Veri satırları (başlık sonrası, footer öncesi)
        for row_num, row in enumerate(invoice_table[1:], 1):
            # Boş satır kontrolü
            if not row or not any(cell for cell in row if cell):
                continue
            
            # Footer satırlarını atla (Toplam, KDV vs.)
            first_cell = str(row[0]).strip() if row[0] else ""
            if not first_cell or not first_cell.isdigit():
                # Bu footer satırı olabilir
                second_cell = str(row[1]).strip() if len(row) > 1 and row[1] else ""
                if any(keyword in second_cell.upper() for keyword in ['TOPLAM', 'KDV', 'VERGİ', 'ÖDENECEK']):
                    print(f"\n📌 Footer satırı tespit edildi: {second_cell}")
                    break
                continue
            
            # Sütun eşleştirmesi (GİB standart format)
            # [0]=Sıra, [1]=Mal/Hiz, [2]=Miktar, [3]=Birim Fiyat, 
            # [4]=İskonto%, [5]=İskonto₺, [6]=İskontoNeden, [7]=KDV%, [8]=KDV₺, [9]=DiğerVergi, [10]=?, [11]=Tutar
            
            try:
                line_item = {
                    'sira_no': int(first_cell),
                    'aciklama': str(row[1]).strip() if len(row) > 1 else None,
                    'miktar_text': str(row[2]).strip() if len(row) > 2 else None,
                    'birim_fiyat_text': str(row[3]).strip() if len(row) > 3 else None,
                    'iskonto_oran': str(row[4]).strip() if len(row) > 4 else None,
                    'iskonto_tutar_text': str(row[5]).strip() if len(row) > 5 else None,
                    'kdv_oran': str(row[7]).strip() if len(row) > 7 else None,
                    'kdv_tutar_text': str(row[8]).strip() if len(row) > 8 else None,
                    'toplam_text': str(row[11]).strip() if len(row) > 11 else None,
                }
                
                # Miktar parse (örn: "1 Adet" → 1)
                miktar_match = re.match(r'([\d,\.]+)', line_item['miktar_text'] or '')
                if miktar_match:
                    line_item['miktar'] = clean_amount(miktar_match.group(1))
                    # Birim (örn: "Adet", "Kg")
                    birim_match = re.search(r'\s+([A-Za-zğüşıöçĞÜŞİÖÇ]+)', line_item['miktar_text'])
                    line_item['birim'] = birim_match.group(1) if birim_match else 'Adet'
                else:
                    line_item['miktar'] = Decimal('1')
                    line_item['birim'] = 'Adet'
                
                # Tutarları decimal'e çevir
                line_item['birim_fiyat'] = clean_amount(line_item['birim_fiyat_text'])
                line_item['iskonto_tutar'] = clean_amount(line_item['iskonto_tutar_text'])
                line_item['kdv_tutar'] = clean_amount(line_item['kdv_tutar_text'])
                line_item['toplam'] = clean_amount(line_item['toplam_text'])
                
                # KDV oranı (örn: "%20,00" → 20)
                kdv_match = re.search(r'(\d+)', line_item['kdv_oran'] or '')
                line_item['kdv_oran_sayi'] = int(kdv_match.group(1)) if kdv_match else 0
                
                line_items.append(line_item)
                
                # Satırı göster
                print(f"\n{line_item['sira_no']}. {line_item['aciklama']}")
                print(f"   Miktar: {line_item['miktar']} {line_item['birim']}")
                print(f"   Birim Fiyat: {line_item['birim_fiyat']} TL")
                print(f"   KDV %{line_item['kdv_oran_sayi']}: {line_item['kdv_tutar']} TL")
                print(f"   TOPLAM: {line_item['toplam']} TL")
                
            except Exception as e:
                print(f"\n⚠️ Satır {row_num} parse edilemedi: {e}")
                print(f"   Raw: {row}")
                continue
        
        print("\n" + "=" * 100)
        print(f"✅ TOPLAM {len(line_items)} KALEM ÇIKARILDI")
        print("=" * 100)
        
        return line_items

def generate_xml_line_items(line_items):
    """Satır kalemlerini GİB XML formatına çevir"""
    
    print("\n\n📝 GİB XML FORMAT:")
    print("=" * 100)
    
    xml_lines = []
    
    for item in line_items:
        xml = f"""
  <malHizmetTablosu>
    <siraNo>{item['sira_no']}</siraNo>
    <malHizmet>{item['aciklama']}</malHizmet>
    <miktar>{item['miktar']}</miktar>
    <birim>{item['birim']}</birim>
    <birimFiyat>{item['birim_fiyat']}</birimFiyat>
    <iskontoArttirmTutar>{item['iskonto_tutar'] or 0}</iskontoArttirmTutar>
    <malHizmetTutari>{item['toplam']}</malHizmetTutari>
    <kdvOrani>{item['kdv_oran_sayi']}</kdvOrani>
    <kdvTutari>{item['kdv_tutar']}</kdvTutari>
    <vergilerDahilToplam>{item['toplam'] + item['kdv_tutar']}</vergilerDahilToplam>
  </malHizmetTablosu>"""
        
        xml_lines.append(xml)
    
    full_xml = '\n'.join(xml_lines)
    print(full_xml)
    print("\n" + "=" * 100)
    
    return full_xml

def generate_summary(line_items):
    """Toplam değerleri hesapla"""
    
    print("\n\n💰 FATURA ÖZETİ:")
    print("=" * 100)
    
    toplam_mal_hizmet = sum(item['toplam'] for item in line_items if item['toplam'])
    toplam_kdv = sum(item['kdv_tutar'] for item in line_items if item['kdv_tutar'])
    genel_toplam = toplam_mal_hizmet + toplam_kdv
    
    print(f"Mal/Hizmet Toplam: {toplam_mal_hizmet:,.2f} TL")
    print(f"Toplam KDV: {toplam_kdv:,.2f} TL")
    print(f"Genel Toplam: {genel_toplam:,.2f} TL")
    
    print("\nKDV Dağılımı:")
    kdv_groups = {}
    for item in line_items:
        oran = item['kdv_oran_sayi']
        if oran not in kdv_groups:
            kdv_groups[oran] = {'matrah': Decimal(0), 'kdv': Decimal(0)}
        kdv_groups[oran]['matrah'] += item['toplam'] or Decimal(0)
        kdv_groups[oran]['kdv'] += item['kdv_tutar'] or Decimal(0)
    
    for oran, values in sorted(kdv_groups.items()):
        print(f"  %{oran}: Matrah {values['matrah']:,.2f} TL → KDV {values['kdv']:,.2f} TL")
    
    print("=" * 100)
    
    return {
        'mal_hizmet_toplam': toplam_mal_hizmet,
        'kdv_toplam': toplam_kdv,
        'genel_toplam': genel_toplam,
        'kdv_dagilim': kdv_groups
    }

if __name__ == '__main__':
    pdf_path = r"C:\Projects\muhasebe-sistem\ilhan_imre.pdf"
    
    # 1. Satır kalemleri çıkar
    line_items = extract_invoice_lines(pdf_path)
    
    if line_items:
        # 2. XML oluştur
        xml = generate_xml_line_items(line_items)
        
        # 3. Özet bilgileri
        summary = generate_summary(line_items)
        
        # 4. Doğrulama
        print("\n\n✅ DOĞRULAMA:")
        print("=" * 100)
        print("Bu değerleri PDF'deki 'Toplam' satırları ile karşılaştırın:")
        print(f"  Mal Hizmet Toplam: {summary['mal_hizmet_toplam']} TL")
        print(f"  Hesaplanan KDV: {summary['kdv_toplam']} TL")
        print(f"  Vergiler Dahil Toplam: {summary['genel_toplam']} TL")
        print("=" * 100)
