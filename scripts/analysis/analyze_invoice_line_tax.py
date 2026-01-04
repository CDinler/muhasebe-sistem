"""
InvoiceLine içindeki KDV % yapısını incele
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_db
from app.models.einvoice import EInvoice
import xml.etree.ElementTree as ET

db = next(get_db())
inv = db.query(EInvoice).filter(EInvoice.invoice_uuid == '48ad10c7-de65-47bb-8619-f7b0ca37755f').first()

if inv and inv.raw_data:
    root = ET.fromstring(inv.raw_data)
    ns = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    # InvoiceLine'ı bul
    lines = root.findall('.//cac:InvoiceLine', ns)
    print(f'InvoiceLine sayısı: {len(lines)}')
    
    for i, line in enumerate(lines[:1]):
        print(f'\n=== Satır {i+1} ===')
        
        # Item name
        item_name = line.find('.//cbc:Name', ns)
        print(f'Item: {item_name.text if item_name is not None else "YOK"}')
        
        # TaxTotal içindeki Percent
        tax_percent = line.find('.//cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent', ns)
        print(f'TaxPercent (full path): {tax_percent.text if tax_percent is not None else "YOK"}')
        
        # TaxSubtotal'ı listele
        tax_subtotals = line.findall('.//cac:TaxSubtotal', ns)
        print(f'TaxSubtotal sayısı: {len(tax_subtotals)}')
        
        for j, ts in enumerate(tax_subtotals):
            pct = ts.find('.//cbc:Percent', ns)
            amt = ts.find('.//cbc:TaxAmount', ns)
            print(f'  {j+1}. Percent: {pct.text if pct else "YOK"}, Amount: {amt.text if amt else "YOK"}')
