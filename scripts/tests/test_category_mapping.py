"""
Test kategori mapping ile preview güncelleme
"""
import requests
import json

# Test data: 740.00204 hesabı seçilmiş
category_data = {
    "invoice_lines_mapping": [
        {
            "line_id": "1",
            "account_code": "740.00204",  # Kullanıcının seçtiği hesap
            "category": "hizmet_maliyet",
            "item_name": "KDV",
            "line_total": 24750.00
        }
    ]
}

# Preview endpoint'ini POST ile çağır
response = requests.post(
    'http://localhost:8000/api/v1/einvoices/3497/import-preview',
    json=category_data
)

print('=' * 80)
print('KATEGORİZASYON İLE PREVIEW TESTİ')
print('=' * 80)

if response.status_code == 200:
    data = response.json()
    
    print(f'\n📋 FATURA: {data["invoice"]["invoice_number"]}')
    print(f'📋 TEDARİKÇİ: {data["invoice"]["supplier_name"]}')
    
    print('\n💰 YEVMİYE KAYDI:')
    print(f'   {"HESAP":12} {"HESAP ADI":40} {"BORÇ":>12} {"ALACAK":>12}')
    print(f'   {"-"*12} {"-"*40} {"-"*12} {"-"*12}')
    
    for line in data['transaction']['lines']:
        borc = f"{line['debit']:>12.2f}" if line['debit'] > 0 else " " * 12
        alacak = f"{line['credit']:>12.2f}" if line['credit'] > 0 else " " * 12
        hesap_adi = line['account_name'][:40]
        print(f"   {line['account_code']:12} {hesap_adi:40} {borc} {alacak}")
        print(f"      └─ {line['description']}")
    
    print(f'\n   TOPLAM: BORÇ {data["transaction"]["total_debit"]:.2f} = ALACAK {data["transaction"]["total_credit"]:.2f}')
    print(f'   Denge: {"✓ OK" if data["transaction"]["is_balanced"] else "✗ HATA"}')
    
    # 740.00204 kullanıldı mı kontrol et
    has_740_00204 = any(line['account_code'] == '740.00204' for line in data['transaction']['lines'])
    print(f'\n   ✓ 740.00204 hesabı kullanıldı mı? {has_740_00204}')
    
    if data.get('warnings'):
        print('\n⚠️  UYARILAR:')
        for warning in data['warnings']:
            print(f'   {warning}')
else:
    print(f'\n❌ HATA: {response.status_code}')
    print(response.text)

print('\n' + '=' * 80)
