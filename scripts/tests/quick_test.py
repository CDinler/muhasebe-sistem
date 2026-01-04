import requests
import json

r = requests.get('http://127.0.0.1:8000/api/v1/einvoices/3496')
data = r.json()

print(f"Fatura: {data.get('invoice_number')}")
print(f"Toplam: {data.get('payable_amount')} TRY")
print(f"\nVergi Detayları: {len(data.get('tax_details', []))}")

for t in data.get('tax_details', []):
    print(f"  - {t['tax_name']} ({t['tax_type_code']}): {t['tax_amount']} TRY")
