"""
6 faturadaki boş KDV sorununu araştır
"""
import requests

base_url = 'http://127.0.0.1:8000/api/v1'

problem_ettns = [
    '48ad10c7-de65-47bb-8619-f7b0ca37755f',
    '68cede74-620b-4bb6-9b7d-41836412b4a4',
    '9d24ecf5-fbaf-49e8-82ab-233761b7e67e',
    'da2db336-8cd0-4153-91fb-d0e65deee20e',
    'daad0b8b-11f8-4834-b603-9e4b50971dac',
    '49fa1d8b-3b33-48fb-ad4b-7b697238a274',
]

print("=" * 80)
print("PROBLEM FATURALAR - BOŞ KDV ANALİZİ")
print("=" * 80)

for ettn in problem_ettns:
    # ETTN'den fatura bul
    response = requests.get(f'{base_url}/einvoices', params={'invoice_uuid': ettn})
    
    if response.status_code == 200:
        data = response.json()
        if data['items']:
            invoice = data['items'][0]
            invoice_id = invoice['id']
            
            # Detaylı bilgi al
            detail_response = requests.get(f'{base_url}/einvoices/{invoice_id}')
            if detail_response.status_code == 200:
                detail = detail_response.json()
                
                print(f"\n📄 FATURA: {ettn[:20]}...")
                print(f"   ID: {invoice_id}")
                print(f"   Belge No: {detail.get('invoice_number', 'N/A')}")
                print(f"   Tedarikçi: {detail.get('supplier_name', 'N/A')}")
                print(f"   Tutar: {detail.get('payable_amount', 0):.2f} TRY")
                print(f"   Toplam KDV (total_tax_amount): {detail.get('total_tax_amount', 'N/A')}")
                
                # Satırlar
                lines = detail.get('invoice_lines', [])
                print(f"\n   📊 Satırlar: {len(lines)}")
                total_line_tax = 0
                for i, line in enumerate(lines, 1):
                    tax = line.get('tax_amount', 0) or 0
                    total_line_tax += tax
                    print(f"      {i}. {line.get('item_name', 'N/A')[:40]}")
                    print(f"         Tutar: {line.get('line_total', 0):.2f}, KDV: {tax:.2f} ({line.get('tax_percent', 0)}%)")
                
                print(f"\n   💰 Satırlardan toplam KDV: {total_line_tax:.2f} TRY")
                
                # Vergi detayları
                tax_totals = detail.get('tax_totals', [])
                print(f"\n   📊 Vergi Detayları: {len(tax_totals)}")
                for i, tax in enumerate(tax_totals, 1):
                    print(f"      {i}. {tax.get('tax_name', 'N/A')} %{tax.get('tax_percent', 0)}")
                    print(f"         Matrah: {tax.get('taxable_amount', 0):.2f}, Tutar: {tax.get('tax_amount', 0):.2f}")
                
                # Masraflar
                charges = detail.get('allowance_charges', [])
                if charges:
                    print(f"\n   📊 Masraf/İndirimler: {len(charges)}")
                    for i, charge in enumerate(charges, 1):
                        tip = "Masraf" if charge.get('is_charge') else "İndirim"
                        print(f"      {i}. [{tip}] {charge.get('reason', 'N/A')}: {charge.get('amount', 0):.2f}")
                
                # PROBLEM TEŞHİSİ
                print(f"\n   ⚠️  DURUM:")
                if detail.get('total_tax_amount'):
                    print(f"      ✅ total_tax_amount VAR: {detail['total_tax_amount']:.2f}")
                else:
                    print(f"      ❌ total_tax_amount YOK veya 0")
                
                if total_line_tax > 0:
                    print(f"      ✅ Satır KDV'leri VAR: {total_line_tax:.2f}")
                else:
                    print(f"      ❌ Satır KDV'leri YOK")
                
                if tax_totals:
                    print(f"      ✅ Vergi detayları VAR: {len(tax_totals)} adet")
                else:
                    print(f"      ❌ Vergi detayları YOK")
    else:
        print(f"\n❌ {ettn}: API hatası ({response.status_code})")

print("\n" + "=" * 80)
