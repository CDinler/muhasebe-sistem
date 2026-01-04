"""
Test: Import preview endpoint'ini doğrudan çağır
"""
import requests

# E-fatura ID 3497 için preview çağır (log'da görünen)
response = requests.get('http://localhost:8000/api/v1/einvoices/3497/import-preview')

print('=' * 80)
print('IMPORT PREVIEW TESTİ (E-Fatura #3497)')
print('=' * 80)

if response.status_code == 200:
    data = response.json()
    
    print('\n📄 FATURA BİLGİLERİ:')
    print(f"   Fatura No: {data['invoice']['invoice_number']}")
    print(f"   Tarih: {data['invoice']['invoice_date']}")
    print(f"   Tedarikçi: {data['invoice']['supplier_name']}")
    print(f"   Tutar: {data['invoice']['payable_amount']:.2f} {data['invoice']['currency_code']}")
    
    print('\n👤 CARİ BİLGİLERİ:')
    print(f"   Kod: {data['contact']['code']}")
    print(f"   Ad: {data['contact']['name']}")
    print(f"   VKN: {data['contact']['tax_number']}")
    durum = "Yeni oluşturulacak" if data["contact"]["will_create"] else "Mevcut"
    print(f"   Durum: {durum}")
    
    print('\n📋 YEVMİYE KAYDI:')
    print(f"   Fiş No: {data['transaction']['number']}")
    print(f"   Tarih: {data['transaction']['date']}")
    print(f"   Dönem: {data['transaction']['period']}")
    print(f"   Belge: {data['transaction']['document_type']} - {data['transaction']['document_number']}")
    
    print(f'\n   {"HESAP":12} {"HESAP ADI":40} {"BORÇ":>12} {"ALACAK":>12}')
    print(f'   {"-"*12} {"-"*40} {"-"*12} {"-"*12}')
    
    for line in data['transaction']['lines']:
        borc = f"{line['debit']:>12.2f}" if line['debit'] > 0 else " " * 12
        alacak = f"{line['credit']:>12.2f}" if line['credit'] > 0 else " " * 12
        hesap_adi = line['account_name'][:40]
        print(f"   {line['account_code']:12} {hesap_adi:40} {borc} {alacak}")
        
        # KDV oranı göster
        if line.get('vat_rate'):
            print(f"      └─ KDV %{int(line['vat_rate']*100)}")
        
        # Tevkifat oranı göster
        if line.get('withholding_rate'):
            print(f"      └─ Tevkifat %{int(line['withholding_rate']*100)}")
    
    print(f'   {"-"*12} {"-"*40} {"-"*12} {"-"*12}')
    print(f'   {"TOPLAM":52} {data["transaction"]["total_debit"]:>12.2f} {data["transaction"]["total_credit"]:>12.2f}')
    
    is_balanced = data['transaction']['is_balanced']
    print(f'\n   Denge: {"✓ Dengede" if is_balanced else "✗ Dengesiz"}')
    
    if data.get('warnings'):
        print('\n⚠️  UYARILAR:')
        for warning in data['warnings']:
            print(f'   {warning}')
    
    print(f'\n   Import Durumu: {"✓ Import edilebilir" if data["can_import"] else "✗ Import edilemez"}')
    
else:
    print(f'\n❌ HATA: {response.status_code}')
    print(response.text)

print('\n' + '=' * 80)
