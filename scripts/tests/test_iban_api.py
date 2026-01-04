import requests
import json

# Test API
response = requests.get('http://localhost:8000/api/v1/einvoices/?limit=2&supplier_tax_number=35566411922')

print("Status:", response.status_code)
print("\nResponse:")
data = response.json()

for item in data:
    print(f"\nFatura: {item.get('invoice_number')}")
    print(f"Supplier: {item.get('supplier_name')}")
    print(f"Contact ID: {item.get('contact_id')}")
    print(f"Contact IBAN: {item.get('contact_iban')}")
    print(f"Supplier IBAN (XML): {item.get('supplier_iban')}")
