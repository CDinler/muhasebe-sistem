import pymysql
import xml.etree.ElementTree as ET
import json

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='muhasebe_sistem',
    charset='utf8mb4'
)

cursor = conn.cursor()
cursor.execute("SELECT raw_data FROM einvoices WHERE invoice_uuid='9d24ecf5-fbaf-49e8-82ab-233761b7e67e'")
row = cursor.fetchone()

if row:
    raw_xml = row[0]
    
    # JSON decode
    try:
        raw_xml = json.loads(raw_xml)
    except:
        pass
    
    # Parse XML
    root = ET.fromstring(raw_xml)
    ns = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'
    }
    
    print("Invoice Lines:")
    for i, line in enumerate(root.findall('.//cac:InvoiceLine', ns), 1):
        line_id = line.find('cbc:ID', ns)
        item_name = line.find('.//cbc:Name', ns)
        line_amount = line.find('cbc:LineExtensionAmount', ns)
        
        if i == 1:
            print(f"Satir {i}:")
            print(f"  ID: {line_id.text if line_id is not None else 'N/A'}")
            print(f"  item_name: {item_name.text if item_name is not None else 'N/A'}")
            print(f"  line_amount: {line_amount.text if line_amount is not None else 'N/A'}")
            break

cursor.close()
conn.close()
