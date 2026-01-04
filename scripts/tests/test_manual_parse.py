# -*- coding: utf-8 -*-
from app.core.database import engine
from sqlalchemy import text
import xml.etree.ElementTree as ET
import html

with engine.connect() as conn:
    result = conn.execute(text("SELECT raw_data FROM einvoices WHERE id = 1"))
    row = result.fetchone()
    
    if row:
        xml_data = row[0]
        
        # Unescape
        if '&quot;' in xml_data:
            xml_data = html.unescape(xml_data)
            print("XML unescaped")
        
        # Parse
        try:
            root = ET.fromstring(xml_data)
            print(f"XML parsed. Root: {root.tag}")
            
            # Namespace
            ns = {
                'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
            }
            
            # Find lines
            lines = root.findall('.//cac:InvoiceLine', ns)
            print(f"InvoiceLine count: {len(lines)}")
            
            if lines:
                for i, line in enumerate(lines, 1):
                    print(f"\nLine {i}:")
                    
                    # Item name
                    item = line.find('.//cac:Item/cbc:Name', ns)
                    print(f"  Name: {item.text if item is not None else 'N/A'}")
                    
                    # Quantity
                    qty = line.find('cbc:InvoicedQuantity', ns)
                    if qty is not None:
                        print(f"  Qty: {qty.text} {qty.get('unitCode')}")
            else:
                print("No InvoiceLine found!")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
