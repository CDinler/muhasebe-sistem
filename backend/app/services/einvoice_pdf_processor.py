"""
E-FATURA VE E-ARŞİV PDF İŞLEME SERVİSİ
1. Sadece PDF olan e-arşiv faturaları parse et → database kaydet
2. E-faturalarda PDF'i eşleştir ve sakla
3. Dizin yapısı: data/einvoice_pdfs/{year}/{month}/
"""
import os
import re
import shutil
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import pdfplumber
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import EInvoice
from app.core.config import settings


class EInvoicePDFProcessor:
    """E-Fatura ve E-Arşiv PDF işleme servisi"""
    
    # PDF depolama kök dizini (proje root'undan itibaren)
    PDF_ROOT = Path(__file__).parent.parent.parent / "data" / "einvoice_pdfs"
    
    # Compiled regex patterns (cache) - performans optimizasyonu
    _compiled_patterns = {
        'ettn_efatura': [
            re.compile(r'ETTN[:\s]*([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})', re.IGNORECASE | re.MULTILINE | re.DOTALL),
            re.compile(r'ETTN[:\s]*([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4})[\s\-\n]*([0-9A-Fa-f]{12})', re.IGNORECASE | re.MULTILINE | re.DOTALL),
            re.compile(r'UUID[:\s]*([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})', re.IGNORECASE),
            re.compile(r'([0-9a-f]{32})', re.IGNORECASE),
        ],
        'ettn_earsiv': [
            re.compile(r'ETTN[:\s]*([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})', re.IGNORECASE),
            re.compile(r'UUID[:\s]*([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})', re.IGNORECASE),
            re.compile(r'ETTN[:\s]*([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4})[\s\-\n]*([0-9A-Fa-f]{12})', re.IGNORECASE | re.MULTILINE | re.DOTALL),
            re.compile(r'([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})', re.IGNORECASE),
            re.compile(r'([0-9a-f]{32})', re.IGNORECASE),
        ],
        'invoice_no': [
            re.compile(r'Fatura No[:\s]+([^\s\n]+)', re.IGNORECASE),
            re.compile(r'Fatura Numarası[:\s]+([^\s\n]+)', re.IGNORECASE),
            re.compile(r'Fatura Seri/Sıra No[:\s]+([^\s\n]+)', re.IGNORECASE),
        ],
        'date_efatura': [
            re.compile(r'Fatura Tarihi[^\n]*\n[\s]*(\d{2})\s*[\-\u2013\u2014]\s*(\d{2})\s*[\-\u2013\u2014]\s*(\d{4})', re.IGNORECASE),
            re.compile(r'Fatura Tarihi[^\n]*\n[\s]*(\d{2})\s*\.\s*(\d{2})\s*\.\s*(\d{4})', re.IGNORECASE),
            re.compile(r'Fatura Tarihi[:\s]{1,3}(\d{2})\s*[\-\u2013\u2014]\s*(\d{2})\s*[\-\u2013\u2014]\s*(\d{4})', re.IGNORECASE),
            re.compile(r'Fatura Tarihi[:\s]{1,3}(\d{2})[\-\u2013\u2014](\d{2})[\-\u2013\u2014](\d{4})', re.IGNORECASE),
            re.compile(r'Fatura Tarihi[:\s]{1,3}(\d{2})\s*\.\s*(\d{2})\s*\.\s*(\d{4})', re.IGNORECASE),
            re.compile(r'Fatura Tarihi[:\s]{1,3}(\d{2})\.(\d{2})\.(\d{4})\s*[\-\u2013\u2014]', re.IGNORECASE),
            re.compile(r'(?:Fatura|E-Posta:)[^\d]*(\d{2})[\-\u2013\u2014](\d{2})[\-\u2013\u2014](\d{4})[^\d]*(?:Tel|Fax|Tarihi)', re.IGNORECASE),
        ],
        'date_earsiv': [
            re.compile(r'Fatura Tarihi[^\n]*\n[\s]*(\d{2})\s*\.\s*(\d{2})\s*\.\s*(\d{4})', re.IGNORECASE),
            re.compile(r'Fatura Tarihi[^\n]*\n[\s]*(\d{2})\s*[\-\u2013\u2014]\s*(\d{2})\s*[\-\u2013\u2014]\s*(\d{4})', re.IGNORECASE),
            re.compile(r'Fatura Tarihi[:\s]{1,3}(\d{2})\s*\.\s*(\d{2})\s*\.\s*(\d{4})', re.IGNORECASE),
            re.compile(r'Fatura Tarihi[:\s]{1,3}(\d{2})\s*[\-\u2013\u2014]\s*(\d{2})\s*[\-\u2013\u2014]\s*(\d{4})', re.IGNORECASE),
            re.compile(r'Fatura Tarihi[:\s]{1,3}(\d{2})\.(\d{2})\.(\d{4})\s*[\-\u2013\u2014]', re.IGNORECASE),
            re.compile(r'Fatura[\s\n]+(\d{2})\s*[\-\u2013\u2014]\s*(\d{2})\s*[\-\u2013\u2014]\s*(\d{4})[\s\n]+Tarihi', re.IGNORECASE),
            re.compile(r'Fatura Tarihi[:\s]{1,3}(\d{2})[\-\u2013\u2014](\d{2})[\-\u2013\u2014](\d{4})', re.IGNORECASE),
            re.compile(r'(?:Fatura|E-Posta:)[^\d]*(\d{2})[\-\u2013\u2014](\d{2})[\-\u2013\u2014](\d{4})[^\d]*(?:Tel|Fax|Tarihi)', re.IGNORECASE),
        ],
    }
    
    def __init__(self, db: Session):
        self.db = db
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Dizin yapısını oluştur"""
        self.PDF_ROOT.mkdir(parents=True, exist_ok=True)
    
    def get_pdf_path(self, year: int, month: int, filename: str) -> Path:
        """
        PDF için dizin yolu oluştur
        Yapı: data/einvoice_pdfs/{year}/{month}/{filename}
        """
        directory = self.PDF_ROOT / str(year) / f"{month:02d}"
        directory.mkdir(parents=True, exist_ok=True)
        return directory / filename
    
    def save_pdf(self, pdf_content: bytes, year: int, month: int, 
                 invoice_no: str, ettn: str) -> str:
        """
        PDF'i dosya sistemine kaydet
        
        Args:
            pdf_content: PDF binary content
            year: Fatura yılı
            month: Fatura ayı
            invoice_no: Fatura numarası
            ettn: E-fatura UUID
        
        Returns:
            Relative path to saved PDF
        """
        # Dosya adı: {INVOICE_NO}_{ETTN}.pdf
        filename = f"{invoice_no}_{ettn}.pdf"
        pdf_path = self.get_pdf_path(year, month, filename)
        
        # PDF'i kaydet
        with open(pdf_path, 'wb') as f:
            f.write(pdf_content)
        
        # Relative path döndür
        relative_path = os.path.relpath(pdf_path, self.PDF_ROOT.parent)
        return relative_path
    
    def extract_invoice_data_from_pdf(self, pdf_path: str) -> Dict:
        """
        PDF'den fatura verilerini çıkar (E-Arşiv veya E-Fatura)
        
        Otomatik format tespiti yapar ve uygun parser'ı kullanır.
        
        Returns:
            {
                'invoice_no': str,
                'ettn': str,
                'issue_date': date,
                'invoice_type': str,
                'invoice_profile': str,
                'supplier_tax_number': str,
                'supplier_name': str,
                'customer_tax_number': str,
                'customer_name': str,
                'line_extension_amount': Decimal,
                'total_tax_amount': Decimal,
                'payable_amount': Decimal,
                'currency_code': str,
                ...
            }
        """
        with pdfplumber.open(pdf_path) as pdf:
            full_text = pdf.pages[0].extract_text()
        
        # Format tespiti: E-Arşiv vs E-Fatura
        # E-Fatura: "e-Fatura" veya "e-FATURA" yazısı içerir
        # E-Arşiv: GİB standart şablon (e-Fatura yazısı yok)
        has_efatura_marker = bool(re.search(r'e-Fatura|e-FATURA', full_text, re.IGNORECASE))
        
        # E-Fatura marker varsa E-Fatura parser kullan
        if has_efatura_marker:
            return self._extract_efatura_data(pdf_path, full_text)
        else:
            return self._extract_earsiv_data(pdf_path, full_text)
    
    def _extract_earsiv_data(self, pdf_path: str, full_text: str = None) -> Dict:
        """
        E-Arşiv PDF'den veri çıkar (GİB standart e-arşiv formatı)
        """
        if not full_text:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = pdf.pages[0].extract_text()
                tables = pdf.pages[0].extract_tables()
        else:
            with pdfplumber.open(pdf_path) as pdf:
                tables = pdf.pages[0].extract_tables()
        
        data = {}
        
        # === TEMEL ALANLAR ===
        
        # Fatura No - compiled patterns kullan (performans)
        data['invoice_no'] = None
        for pattern in self._compiled_patterns['invoice_no']:
            match = pattern.search(full_text)
            if match:
                data['invoice_no'] = match.group(1)
                break
        
        # ETTN (UUID) - compiled patterns kullan (performans)
        data['ettn'] = None
        for i, pattern in enumerate(self._compiled_patterns['ettn_efatura']):
            match = pattern.search(full_text)
            if match:
                if i == 1:  # Satır sonu ile bölünmüş format
                    data['ettn'] = match.group(1) + match.group(2)
                else:
                    data['ettn'] = match.group(1)
                break
        
        # Fatura Tarihi - compiled patterns kullan (performans)
        data['issue_date'] = None
        for pattern in self._compiled_patterns['date_efatura']:
            match = pattern.search(full_text)
            if match:
                day, month, year = match.groups()
                try:
                    data['issue_date'] = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d").date()
                    break
                except:
                    pass
        
        # Senaryo
        match = re.search(r'Senaryo[:\s]*([^\s\n]+)', full_text)
        data['invoice_profile'] = match.group(1) if match else None
        
        # Fatura Tipi
        match = re.search(r'Fatura Tipi:\s*([^\s\n]+)', full_text)
        data['invoice_type'] = match.group(1) if match else None
        
        # === TEDARİKÇİ BİLGİLERİ ===
        # VKN (Tedarikçi - üstte)
        vkn_matches = re.findall(r'VKN:\s*(\d+)', full_text)
        data['supplier_tax_number'] = vkn_matches[0] if vkn_matches else None
        
        # Tedarikçi Adı (VKN'den önce gelen büyük harfli metin)
        if data['supplier_tax_number']:
            pattern = r'([A-ZİĞÜŞÖÇ\s]+)\s+(?:.*?)VKN:\s*' + data['supplier_tax_number']
            match = re.search(pattern, full_text, re.DOTALL)
            if match:
                supplier_name = match.group(1).strip()
                # Fazla boşlukları temizle
                data['supplier_name'] = ' '.join(supplier_name.split())
            else:
                data['supplier_name'] = None
        
        # === MÜŞTERİ BİLGİLERİ ===
        # TCKN veya VKN (Müşteri - "SAYIN" sonrası)
        tckn_match = re.search(r'SAYIN.*?TCKN:\s*(\d+)', full_text, re.DOTALL)
        if tckn_match:
            data['customer_tax_number'] = tckn_match.group(1)
        else:
            # VKN varsa (2. VKN)
            if len(vkn_matches) > 1:
                data['customer_tax_number'] = vkn_matches[1]
            else:
                data['customer_tax_number'] = None
        
        # Müşteri Adı ("SAYIN" sonrası büyük harfli metin)
        match = re.search(r'SAYIN\s+([A-ZİĞÜŞÖÇ\s]+?)(?:\s+Özelleştirme|\s+KÖRFEZ|\s+\d|\n)', 
                         full_text)
        if match:
            data['customer_name'] = match.group(1).strip()
        else:
            data['customer_name'] = None
        
        # === TUTARLAR ===
        
        # Mal Hizmet Toplam
        match = re.search(r'Mal Hizmet Toplam(?:\s+Tutarı)?[:\s]+([\d.,]+)\s*TL', full_text)
        if match:
            amount_str = match.group(1).replace('.', '').replace(',', '.')
            data['line_extension_amount'] = Decimal(amount_str)
        else:
            data['line_extension_amount'] = None
        
        # KDV Tutarı (birden fazla olabilir, topla)
        kdv_matches = re.findall(r'(?:Hesaplanan|Toplam)\s+(?:.*?)KDV[^:]*[:\s]+([\d.,]+)\s*TL', 
                                 full_text, re.IGNORECASE)
        if kdv_matches:
            total_kdv = Decimal('0')
            for kdv_str in kdv_matches:
                amount_str = kdv_str.replace('.', '').replace(',', '.')
                total_kdv += Decimal(amount_str)
            data['total_tax_amount'] = total_kdv
        else:
            data['total_tax_amount'] = None
        
        # Ödenecek Tutar
        match = re.search(r'Ödenecek Tutar[:\s]+([\d.,]+)\s*TL', full_text)
        if match:
            amount_str = match.group(1).replace('.', '').replace(',', '.')
            data['payable_amount'] = Decimal(amount_str)
        else:
            data['payable_amount'] = None
        
        # Para Birimi (default TL)
        data['currency_code'] = 'TRY'
        
        # === SATIR KALEMLERİ ===
        data['line_items'] = []
        
        for table in tables:
            # Satır tablosunu bul
            if len(table) > 5 and any('Sıra' in str(cell) for row in table[:2] for cell in row if cell):
                headers = table[0]
                
                for row in table[1:]:
                    if not row or not any(cell for cell in row if cell):
                        continue
                    
                    first_cell = str(row[0]).strip() if row[0] else ""
                    if not first_cell or not first_cell.isdigit():
                        continue
                    
                    try:
                        line_item = {
                            'line_id': int(first_cell),
                            'item_name': str(row[1]).strip() if len(row) > 1 and row[1] else None,
                            'quantity_text': str(row[2]).strip() if len(row) > 2 and row[2] else None,
                            'price_text': str(row[3]).strip() if len(row) > 3 and row[3] else None,
                            'tax_percent_text': str(row[4]).strip() if len(row) > 4 and row[4] else None,
                            'tax_amount_text': str(row[5]).strip() if len(row) > 5 and row[5] else None,
                            'line_total_text': str(row[8]).strip() if len(row) > 8 and row[8] else None,
                        }
                        
                        # Parse numeric values
                        # Miktar (örn: "30 m" → 30)
                        if line_item['quantity_text']:
                            qty_match = re.match(r'([\d,\.]+)', line_item['quantity_text'])
                            if qty_match:
                                qty_str = qty_match.group(1).replace('.', '').replace(',', '.')
                                line_item['quantity'] = Decimal(qty_str)
                                
                                # Birim (örn: "m", "Adet")
                                unit_match = re.search(r'\s+([A-Za-zğüşıöçĞÜŞİÖÇ]+)', line_item['quantity_text'])
                                line_item['unit'] = unit_match.group(1) if unit_match else 'Adet'
                        
                        # Birim Fiyat
                        if line_item['price_text']:
                            price_str = line_item['price_text'].replace(' TL', '').replace('.', '').replace(',', '.')
                            line_item['price'] = Decimal(price_str)
                        
                        # KDV Oranı
                        if line_item['tax_percent_text']:
                            tax_match = re.search(r'(\d+)', line_item['tax_percent_text'])
                            line_item['tax_percent'] = int(tax_match.group(1)) if tax_match else 0
                        
                        # KDV Tutarı
                        if line_item['tax_amount_text']:
                            tax_str = line_item['tax_amount_text'].replace(' TL', '').replace('.', '').replace(',', '.')
                            line_item['tax_amount'] = Decimal(tax_str)
                        
                        # Satır Toplamı
                        if line_item['line_total_text']:
                            total_str = line_item['line_total_text'].replace(' TL', '').replace('.', '').replace(',', '.')
                            line_item['line_total'] = Decimal(total_str)
                        
                        data['line_items'].append(line_item)
                        
                    except Exception as e:
                        print(f"⚠️ Satır parse hatası: {e}")
                        continue
                
                break
        
        return data
    
    def _extract_efatura_data(self, pdf_path: str, full_text: str = None) -> Dict:
        """
        E-Fatura PDF'den veri çıkar (GİB standart e-fatura formatı)
        
        E-Fatura formatı E-Arşiv'den farklıdır:
        - ETTN formatı farklı olabilir (tire ile veya tiresiz)
        - Tarih formatı: DD.MM.YYYY veya DD-MM-YYYY
        - "Fatura No:" yerine sadece "No:" olabilir
        """
        if not full_text:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = pdf.pages[0].extract_text()
                tables = pdf.pages[0].extract_tables()
        else:
            with pdfplumber.open(pdf_path) as pdf:
                tables = pdf.pages[0].extract_tables()
        
        data = {}
        
        # === TEMEL ALANLAR ===
        
        # Fatura No - compiled patterns kullan (performans)
        data['invoice_no'] = None
        for pattern in self._compiled_patterns['invoice_no']:
            match = pattern.search(full_text)
            if match:
                data['invoice_no'] = match.group(1)
                break
        
        # Eğer bulunamadıysa, ekstra pattern'ler dene
        if not data['invoice_no']:
            extra_patterns = [
                re.compile(r'(?:^|\n)No[:\s]+([A-Z0-9]+)', re.MULTILINE | re.IGNORECASE),
            ]
            for pattern in extra_patterns:
                match = pattern.search(full_text)
                if match:
                    data['invoice_no'] = match.group(1)
                    break
        
        # ETTN (UUID) - compiled patterns kullan (performans)
        data['ettn'] = None
        for i, pattern in enumerate(self._compiled_patterns['ettn_earsiv']):
            match = pattern.search(full_text)
            if match:
                if i == 2:  # Satır sonu ile bölünmüş format
                    ettn = match.group(1) + match.group(2)
                else:
                    ettn = match.group(1)
                # Tiresiz ise tire ekle
                if len(ettn) == 32 and '-' not in ettn:
                    ettn = f"{ettn[0:8]}-{ettn[8:12]}-{ettn[12:16]}-{ettn[16:20]}-{ettn[20:32]}"
                data['ettn'] = ettn.lower()
                break
        
        # Fatura Tarihi - compiled patterns kullan (performans)
        data['issue_date'] = None
        for pattern in self._compiled_patterns['date_earsiv']:
            match = pattern.search(full_text)
            if match:
                day, month, year = match.groups()
                try:
                    data['issue_date'] = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d").date()
                    break
                except:
                    pass
        
        # Senaryo
        match = re.search(r'Senaryo:\s*([^\s\n]+)', full_text)
        data['invoice_profile'] = match.group(1) if match else 'TEMELFATURA'
        
        # Fatura Tipi
        match = re.search(r'Fatura Tipi:\s*([^\s\n]+)', full_text)
        data['invoice_type'] = match.group(1) if match else 'SATIS'
        
        # === MÜŞTERİ BİLGİLERİ ===
        
        # Satıcı VKN
        match = re.search(r'Vergi Numarası:\s*(\d+)', full_text)
        if match:
            data['supplier_tax_number'] = match.group(1)
        else:
            match = re.search(r'VKN:\s*(\d+)', full_text)
            data['supplier_tax_number'] = match.group(1) if match else None
        
        # Satıcı Adı (ilk satır genelde firma adı)
        lines = full_text.split('\n')
        data['supplier_name'] = lines[0].strip() if lines else None
        
        # Müşteri VKN (ikinci "Vergi Numarası" veya "VKN")
        vkn_matches = list(re.finditer(r'Vergi Numarası:\s*(\d+)', full_text))
        if len(vkn_matches) > 1:
            data['customer_tax_number'] = vkn_matches[1].group(1)
        else:
            vkn_matches = list(re.finditer(r'VKN:\s*(\d+)', full_text))
            data['customer_tax_number'] = vkn_matches[1].group(1) if len(vkn_matches) > 1 else None
        
        # Müşteri Adı ("SAYIN" kelimesinden sonraki satır)
        match = re.search(r'SAYIN\s*\n\s*([^\n]+)', full_text)
        data['customer_name'] = match.group(1).strip() if match else None
        
        # === TUTAR BİLGİLERİ ===
        
        # Mal Hizmet Toplam Tutarı
        match = re.search(r'Mal Hizmet Toplam Tutarı:?\s*([\d.,]+)\s*TL', full_text)
        if match:
            amount_str = match.group(1).replace('.', '').replace(',', '.')
            data['line_extension_amount'] = Decimal(amount_str)
        else:
            data['line_extension_amount'] = Decimal('0.00')
        
        # Toplam KDV
        patterns = [
            r'Toplam KDV Tutarı:?\s*([\d.,]+)\s*TL',
            r'Hesaplanan KDV.*?:?\s*([\d.,]+)\s*TL',
        ]
        data['total_tax_amount'] = Decimal('0.00')
        for pattern in patterns:
            match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)
            if match:
                amount_str = match.group(1).replace('.', '').replace(',', '.')
                data['total_tax_amount'] = Decimal(amount_str)
                break
        
        # Ödenecek Tutar
        match = re.search(r'Ödenecek Tutar:?\s*([\d.,]+)\s*TL', full_text)
        if match:
            amount_str = match.group(1).replace('.', '').replace(',', '.')
            data['payable_amount'] = Decimal(amount_str)
        else:
            data['payable_amount'] = Decimal('0.00')
        
        # Para Birimi
        data['currency_code'] = 'TRY'
        
        # Line items (tablo varsa parse et)
        data['line_items'] = []
        if tables:
            for table in tables:
                if len(table) < 2:
                    continue
                
                # İlk satır başlık mı kontrol et
                header = table[0] if table else []
                if not header or len(header) < 3:
                    continue
                
                # Ürün satırlarını parse et
                for row in table[1:]:
                    if not row or len(row) < 3:
                        continue
                    
                    try:
                        line_item = {
                            'description': ' '.join([str(cell) for cell in row if cell]) if row else '',
                        }
                        data['line_items'].append(line_item)
                    except Exception as e:
                        print(f"⚠️ Satır parse hatası: {e}")
                        continue
                
                break
        
        return data
    
    def save_invoice_from_pdf_only(self, pdf_path: str, original_filename: str = None, direction: str = 'incoming') -> Optional[int]:
        """
        Sadece PDF olan e-fatura/e-arşiv faturayı parse et ve database kaydet
        
        ⚠️ Bu fonksiyon HEM E-FATURA HEM E-ARŞİV için çalışır!
        - Otomatik format tespiti yapar (extract_invoice_data_from_pdf içinde)
        - E-Fatura: "e-Fatura" marker'ı varsa _extract_efatura_data kullanır
        - E-Arşiv: Marker yoksa _extract_earsiv_data kullanır
        
        Args:
            pdf_path: Temp dosya yolu
            original_filename: Orijinal PDF dosya adı (UUID içeren)
            direction: 'incoming' (gelen) veya 'outgoing' (giden) - contact eşleştirmesi için
        
        Returns:
            Created einvoice.id or None
        """
        # Performans optimizasyonu: Dosya adından ETTN çıkar ve önce duplicate check yap
        # Format: {INVOICE_NO}_{ETTN}.pdf
        filename = original_filename if original_filename else os.path.basename(pdf_path)
        ettn_from_filename = None
        existing_record = None
        
        # Dosya adından ETTN'yi çıkarmaya çalış
        print(f"🔍 DEBUG: Filename = {filename}")
        uuid_pattern = re.compile(r'([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})')
        uuid_match = uuid_pattern.search(filename)
        print(f"🔍 DEBUG: UUID Match = {uuid_match}")
        if uuid_match:
            ettn_from_filename = uuid_match.group(1).lower()
            print(f"🔍 ETTN çıkarıldı: {ettn_from_filename} - Dosya: {filename}")
            
            #  Aynı ETTN var mı kontrol et (PDF parse etmeden)
            existing_record = self.db.query(EInvoice).filter(
                EInvoice.invoice_uuid == ettn_from_filename
            ).first()
            
            print(f"🔍 Sorgu sonucu: {existing_record} (ID: {existing_record.id if existing_record else 'YOK'}, PDF: {existing_record.pdf_path if existing_record else 'YOK'})")
            
            if existing_record:
                # Eğer PDF zaten varsa skip et
                if existing_record.pdf_path:
                    print(f"⚠️ Fatura zaten mevcut (PDF var): {filename}")
                    return existing_record.id
                else:
                    # XML kaydı var, PDF yok - PDF'i direkt ekle (PARSE ETME!)
                    print(f"📎 XML kaydına PDF ekleniyor (fast): {filename}")
                    
                    # PDF'i kaydet (parse etmeden)
                    year = existing_record.issue_date.year if existing_record.issue_date else datetime.now().year
                    month = existing_record.issue_date.month if existing_record.issue_date else datetime.now().month
                    
                    with open(pdf_path, 'rb') as f:
                        pdf_content = f.read()
                    
                    pdf_relative_path = self.save_pdf(
                        pdf_content, year, month,
                        existing_record.invoice_number, existing_record.invoice_uuid
                    )
                    
                    # Mevcut kaydı güncelle
                    existing_record.pdf_path = pdf_relative_path
                    self.db.commit()
                    
                    print(f"✅ PDF eklendi (fast): {existing_record.invoice_number}")
                    return existing_record.id
        
        # PDF'den veri çıkar (sadece yeni kayıtlar için)
        data = self.extract_invoice_data_from_pdf(pdf_path)
        
        if not data.get('ettn') or not data.get('invoice_no'):
            print(f"❌ Gerekli alanlar eksik: ETTN={data.get('ettn')}, Invoice No={data.get('invoice_no')}")
            return None
        
        # Son kontrol: PDF'den çıkan ETTN ile de kontrol et (dosya adında ETTN yoksa)
        if not existing_record:
            existing_record = self.db.query(EInvoice).filter(
                EInvoice.invoice_uuid == data['ettn'].lower()
            ).first()
            
            if existing_record:
                print(f"⚠️ Fatura zaten var (beklenmeyen): {data['invoice_no']}")
                return existing_record.id
        
        # Yeni kayıt oluştur (PDF-only)
        # PDF'i kaydet
        year = data['issue_date'].year if data['issue_date'] else datetime.now().year
        month = data['issue_date'].month if data['issue_date'] else datetime.now().month
        
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        pdf_relative_path = self.save_pdf(
            pdf_content, year, month,
            data['invoice_no'], data['ettn']
        )
        
        # Database kaydı oluştur
        einvoice = EInvoice(
            invoice_number=data['invoice_no'],
            invoice_uuid=data['ettn'],
            issue_date=data['issue_date'],
            invoice_type=data.get('invoice_type'),
            invoice_profile=data.get('invoice_profile'),
            supplier_tax_number=data.get('supplier_tax_number'),
            supplier_name=data.get('supplier_name'),
            customer_tax_number=data.get('customer_tax_number'),
            customer_name=data.get('customer_name'),
            line_extension_amount=data.get('line_extension_amount', Decimal('0.00')),
            total_tax_amount=data.get('total_tax_amount', Decimal('0.00')),
            payable_amount=data.get('payable_amount', Decimal('0.00')),
            currency_code=data.get('currency_code', 'TRY'),
            pdf_path=pdf_relative_path,
            has_xml=0,  # Sadece PDF var (Integer: 0 or 1)
            source='pdf_only',
        )
        
        # CONTACT EŞLEŞTİRMESİ (PDF-only için de gerekli!)
        # Direction'a göre contact belirle
        if 'incoming' in direction:
            # GELEN FATURA: Supplier (tedarikçi) contact olacak
            contact_vkn = data.get('supplier_tax_number')
            contact_name = data.get('supplier_name')
            contact_type = 'SUPPLIER'
        else:
            # GİDEN FATURA: Customer (müşteri) contact olacak
            contact_vkn = data.get('customer_tax_number')
            contact_name = data.get('customer_name')
            contact_type = 'CUSTOMER'
        
        if contact_vkn:
            from sqlalchemy import text
            from app.models import Contact
            
            # Mevcut contact var mı?
            contact = self.db.execute(text("""
                SELECT id FROM contacts 
                WHERE CAST(tax_number AS UNSIGNED) = CAST(:vkn AS UNSIGNED)
                LIMIT 1
            """), {"vkn": contact_vkn}).first()
            
            if contact:
                einvoice.contact_id = contact.id
                print(f"📎 Contact eşleştirildi: ID {contact.id} ({contact_type})")
            elif contact_name:
                # Yeni contact oluştur
                from app.domains.partners.contacts.service import ContactService
                contact_service = ContactService(self.db)
                new_code = contact_service.generate_contact_code('supplier' if contact_type == 'SUPPLIER' else 'customer')
                
                new_contact = Contact(
                    code=new_code,
                    name=contact_name,
                    contact_type=contact_type,
                    tax_number=contact_vkn,
                    is_active=True
                )
                
                self.db.add(new_contact)
                self.db.flush()
                
                einvoice.contact_id = new_contact.id
                print(f"🆕 Yeni contact oluşturuldu: ID {new_contact.id}, Code {new_code}, Type {contact_type}")
        
        self.db.add(einvoice)
        self.db.commit()
        self.db.refresh(einvoice)
        
        print(f"✅ Fatura kaydedildi ({direction}): {data['invoice_no']} (ID: {einvoice.id}, Contact: {einvoice.contact_id or 'YOK'})")
        
        # Satır kalemleri varsa kaydet (isteğe bağlı)
        # TODO: InvoiceLine tablosuna kaydet
        
        return einvoice.id
    
    def attach_pdf_to_existing_einvoice(self, einvoice_id: int, pdf_path: str) -> bool:
        """
        Mevcut e-faturaya PDF eşleştir
        (XML zaten var, sadece PDF ekleniyor)
        
        Args:
            einvoice_id: E-fatura ID
            pdf_path: PDF dosya yolu
        
        Returns:
            Success status
        """
        einvoice = self.db.query(EInvoice).filter(EInvoice.id == einvoice_id).first()
        
        if not einvoice:
            print(f"❌ E-fatura bulunamadı: ID={einvoice_id}")
            return False
        
        # PDF'i kaydet
        year = einvoice.issue_date.year
        month = einvoice.issue_date.month
        
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        pdf_relative_path = self.save_pdf(
            pdf_content, year, month,
            einvoice.invoice_number, einvoice.invoice_uuid
        )
        
        # Database güncelle
        einvoice.pdf_path = pdf_relative_path
        self.db.commit()
        
        print(f"✅ PDF eşleştirildi: {einvoice.invoice_number} → {pdf_relative_path}")
        
        return True
    
    def get_pdf_full_path(self, einvoice: EInvoice) -> Optional[Path]:
        """PDF'in tam yolunu al"""
        if not einvoice.pdf_path:
            return None
        
        # pdf_path zaten relative path olarak saklanmış (örn: "2025/12/filename.pdf")
        # PDF_ROOT ile birleştir
        return self.PDF_ROOT / einvoice.pdf_path
    
    def validate_extracted_data(self, data: Dict) -> Tuple[bool, List[str]]:
        """
        Çıkarılan verinin doğruluğunu kontrol et
        
        KRİTİK ZORUNLU ALANLAR:
        - ETTN (UUID) ✓ - Her faturanın benzersiz kimliği (GİB zorunlu)
        - Fatura numarası ✓
        - Fatura tarihi ✓ 
        - Ödenecek tutar ✓
        
        Diğer hatalar (tutar uyumsuzluğu) WARNING olarak dönüyor.
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # === KRİTİK ZORUNLU ALANLAR ===
        
        if not data.get('ettn'):
            errors.append("ETTN (UUID) bulunamadı - GİB sisteminde ETTN zorunludur")
        
        if not data.get('invoice_no'):
            errors.append("Fatura numarası bulunamadı")
        
        if not data.get('issue_date'):
            errors.append("Fatura tarihi bulunamadı")
        
        if data.get('payable_amount') is None:
            errors.append("Ödenecek tutar bulunamadı")
        
        # Kritik hata varsa False dön
        if errors:
            return (False, errors)
        
        # === OPSİYONEL KONTROLLER (WARNING) ===
        warnings = []
        
        # Tutar kontrolleri (WARNING olarak)
        if data.get('line_extension_amount') and data.get('tax_amount') and data.get('payable_amount'):
            expected_total = data['line_extension_amount'] + data['tax_amount']
            actual_total = data['payable_amount']
            
            # 0.50 TL tolerans (daha esnek)
            if abs(expected_total - actual_total) > Decimal('0.50'):
                warnings.append(f"⚠️ Tutar uyumsuzluğu: {data['line_extension_amount']} + {data['tax_amount']} ≠ {data['payable_amount']}")
        
        # Satır kalemleri toplamı (WARNING)
        if data.get('line_items') and data.get('line_extension_amount'):
            line_totals = sum(item.get('line_total', Decimal('0')) for item in data['line_items'])
            if abs(line_totals - data['line_extension_amount']) > Decimal('0.50'):
                warnings.append(f"⚠️ Satır toplamları uyumsuz: {line_totals} ≠ {data['line_extension_amount']}")
        
        # Warnings varsa ama kritik hata yoksa TRUE dön (kaydet)
        return (True, warnings)


# Kullanım örneği
if __name__ == '__main__':
    from app.db.session import SessionLocal
    
    db = SessionLocal()
    processor = EInvoicePDFProcessor(db)
    
    # Örnek 1: Sadece PDF olan e-fatura/e-arşiv (otomatik format tespiti)
    pdf_path = r"C:\Projects\muhasebe-sistem\ilhan_imre.pdf"
    einvoice_id = processor.save_invoice_from_pdf_only(pdf_path, direction='incoming')
    
    if einvoice_id:
        print(f"✅ Başarılı! E-fatura ID: {einvoice_id}")
    
    # Örnek 2: Mevcut e-faturaya PDF ekle
    # processor.attach_pdf_to_existing_einvoice(einvoice_id=123, pdf_path="fatura.pdf")
    
    db.close()
