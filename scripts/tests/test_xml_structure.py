"""
XML TaxTotal yapısını kontrol et
"""
import xml.etree.ElementTree as ET
from pathlib import Path

# Test faturası
xml_file = Path(r'C:\Projects\muhasebe-sistem\data\xml\e-Fatura\2025\01\9d24ecf5-fbaf-49e8-82ab-233761b7e67e.xml')

if xml_file.exists():
    with open(xml_file, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    root = ET.fromstring(xml_content)
    
    # Root tag
    print(f"Root tag: {root.tag}")
    
    ns = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'invoice': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2'
    }
    
    # Tüm TaxTotal'ları bul
    all_tax_totals = root.findall('.//cac:TaxTotal', ns)
    print(f"\nToplam TaxTotal sayısı (.//): {len(all_tax_totals)}")
    
    # Root altındaki TaxTotal
    root_tax_totals = root.findall('cac:TaxTotal', ns)
    print(f"Root altındaki TaxTotal (cac:TaxTotal): {len(root_tax_totals)}")
    
    # Invoice namespace ile dene
    inv_tax_totals = root.findall('invoice:TaxTotal', ns)
    print(f"invoice:TaxTotal: {len(inv_tax_totals)}")
    
    # İlk birkaç child göster
    print(f"\nRoot'un ilk 10 child tag'i:")
    for i, child in enumerate(root[:10]):
        print(f"  {i+1}. {child.tag}")
    
    # TaxTotal'ların parent'larını göster
    print(f"\nİlk 5 TaxTotal'ın parent path'i:")
    for i, tax_total in enumerate(all_tax_totals[:5]):
        parent_path = []
        current = tax_total
        for _ in range(3):  # 3 seviye yukarı
            parent = root.find(f".//*[.//{{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}}TaxTotal='']")
            if parent is None:
                break
        print(f"  {i+1}. Parent yaklaşık path...")
    
    # AllowanceCharge
    all_allowance = root.findall('.//cac:AllowanceCharge', ns)
    print(f"\nToplam AllowanceCharge (.//): {len(all_allowance)}")
    
    root_allowance = root.findall('cac:AllowanceCharge', ns)
    print(f"Root altındaki AllowanceCharge: {len(root_allowance)}")
    
else:
    print("XML dosyası bulunamadı!")
