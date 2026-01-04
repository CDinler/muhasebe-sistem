"""
6 faturanın total_tax_amount'unu XML'den okuyup güncelle
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_db
from app.models.einvoice import EInvoice
import xml.etree.ElementTree as ET

# 6 fatura UUID
uuids = [
    '48ad10c7-de65-47bb-8619-f7b0ca37755f',
    '68cede74-620b-4bb6-9b7d-41836412b4a4',
    '9d24ecf5-fbaf-49e8-82ab-233761b7e67e',
    'da2db336-8cd0-4153-91fb-d0e65deee20e',
    'daad0b8b-11f8-4834-b603-9e4b50971dac',
    '49fa1d8b-3b33-48fb-ad4b-7b697238a274'
]

ns = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
}

db = next(get_db())
updated = 0

for uuid in uuids:
    inv = db.query(EInvoice).filter(EInvoice.invoice_uuid == uuid).first()
    
    if not inv:
        print(f"❌ {uuid[:8]} bulunamadı")
        continue
    
    if not inv.raw_data:
        print(f"❌ {uuid[:8]} - raw_data yok")
        continue
    
    try:
        root = ET.fromstring(inv.raw_data)
        
        # Invoice seviyesindeki TaxTotal'ı bul (Invoice'ın direkt çocuğu olan)
        invoice_tax_total = None
        for child in root:
            if child.tag.endswith('TaxTotal'):
                tax_amount = child.find('cbc:TaxAmount', ns)
                if tax_amount is not None and tax_amount.text:
                    invoice_tax_total = float(tax_amount.text)
                    break
        
        if invoice_tax_total is not None:
            inv.total_tax_amount = invoice_tax_total
            db.commit()
            updated += 1
            print(f"✅ {inv.invoice_number} - KDV: {invoice_tax_total:.2f}")
        else:
            print(f"⚠️  {inv.invoice_number} - XML'de TaxTotal bulunamadı")
    
    except Exception as e:
        print(f"❌ {inv.invoice_number} - HATA: {e}")

print(f"\n✅ Toplam {updated}/6 fatura güncellendi")
