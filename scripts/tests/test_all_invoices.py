"""
KESİN ÇÖZÜM: Backend'i yeniden başlat ve tüm faturaları test et
"""
import sys
sys.path.append('.')
import requests

print("=" * 80)
print("FATURA SATIR TESTİ - İLK 5 FATURA")
print("=" * 80)

for invoice_id in [1, 2, 3, 4, 5]:
    print(f"\n{'='*80}")
    print(f"FATURA ID={invoice_id}")
    print('='*80)
    
    try:
        response = requests.get(f'http://localhost:8000/api/v1/einvoices/{invoice_id}')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Fatura No: {data.get('invoice_number')}")
            print(f"   Toplam: {data.get('payable_amount')} {data.get('currency_code')}")
            
            if 'invoice_lines' in data:
                lines = data['invoice_lines']
                print(f"   invoice_lines: {len(lines)} satır")
                
                if lines:
                    for i, line in enumerate(lines[:3], 1):  # İlk 3 satır
                        print(f"\n   Satır {i}:")
                        print(f"     Ürün: {line.get('item_name')}")
                        print(f"     Miktar: {line.get('quantity')} {line.get('unit')}")
                        print(f"     Fiyat: {line.get('unit_price')} TL")
                else:
                    print("   ❌ invoice_lines BOŞ!")
            else:
                print("   ❌ invoice_lines YOK!")
        else:
            print(f"❌ API Hatası: {response.status_code}")
    except Exception as e:
        print(f"❌ Bağlantı Hatası: {e}")

print("\n" + "=" * 80)
print("TEST TAMAMLANDI")
print("=" * 80)
