"""
Sync sonrası test - artık tüm faturalar satır görmeli
"""
import requests

base_url = 'http://127.0.0.1:8000/api/v1'

print("=" * 60)
print("SYNC SONRASI TEST - İLK 10 FATURA")
print("=" * 60)

for invoice_id in range(1, 11):
    response = requests.get(f'{base_url}/einvoices/{invoice_id}')
    
    if response.status_code == 200:
        data = response.json()
        lines = data.get('invoice_lines', [])
        
        if lines:
            print(f"\n✅ FATURA ID={invoice_id}: {len(lines)} SATIR")
            for i, line in enumerate(lines, 1):
                item_name = line.get('item_name', 'N/A')[:40]
                qty = line.get('quantity', 0)
                price = line.get('unit_price', 0)
                total = line.get('line_total', 0)
                print(f"   {i}. {item_name} | {qty} x {price:.2f} = {total:.2f} TL")
        else:
            print(f"\n❌ FATURA ID={invoice_id}: SATIR YOK!")
    else:
        print(f"\n⚠️  FATURA ID={invoice_id}: API HATASI ({response.status_code})")

print("\n" + "=" * 60)
