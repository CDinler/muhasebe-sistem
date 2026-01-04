"""
API'den vergi detaylarını test et
"""
import requests
import json

# Test faturası ID'sini bul
BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_tax_details_in_api():
    """API'den vergi detaylarını kontrol et"""
    
    # Önce TURKCELL faturasını bul
    response = requests.get(f"{BASE_URL}/einvoices/", params={
        "invoice_number": "0012025270801375"
    })
    
    if response.status_code != 200:
        print(f"✗ API Hatası: {response.status_code}")
        return
    
    invoices = response.json()
    
    if not invoices:
        print("✗ Fatura bulunamadı!")
        return
    
    invoice_id = invoices[0]['id']
    print(f"=== FATURA BULUNDU ===")
    print(f"ID: {invoice_id}")
    print(f"No: {invoices[0]['invoice_number']}")
    print(f"Toplam: {invoices[0]['payable_amount']} TRY")
    
    # Detay API'sini çağır
    detail_response = requests.get(f"{BASE_URL}/einvoices/{invoice_id}")
    
    if detail_response.status_code != 200:
        print(f"✗ Detay API Hatası: {detail_response.status_code}")
        print(detail_response.text)
        return
    
    invoice_detail = detail_response.json()
    
    # Vergi detaylarını kontrol et
    tax_details = invoice_detail.get('tax_details', [])
    
    print(f"\n=== VERGİ DETAYLARI ({len(tax_details)} adet) ===")
    
    if not tax_details:
        print("✗ Vergi detayı yok!")
        return
    
    total_tax = 0
    for idx, tax in enumerate(tax_details, 1):
        print(f"\n{idx}. {tax['tax_name']} ({tax['tax_type_code']})")
        print(f"   Oran      : %{tax['tax_percent']}")
        print(f"   Matrah    : {tax['taxable_amount']} {tax['currency_code']}")
        print(f"   Vergi     : {tax['tax_amount']} {tax['currency_code']}")
        total_tax += tax['tax_amount']
    
    print(f"\n=== TOPLAM VERGİ: {total_tax:.2f} TRY ===")
    
    # Satırları da kontrol et
    invoice_lines = invoice_detail.get('invoice_lines', [])
    print(f"\n=== FATURA SATIRLARI ({len(invoice_lines)} adet) ===")
    
    for idx, line in enumerate(invoice_lines, 1):
        print(f"\n{idx}. {line.get('item_name')}")
        print(f"   Miktar    : {line.get('quantity', 0)} {line.get('unit', '')}")
        print(f"   Birim Fiyat: {line.get('unit_price', 0)} TRY")
        print(f"   Toplam    : {line.get('line_total', 0)} TRY")
    
    print("\n✓ API testi başarılı!")

if __name__ == "__main__":
    print("=" * 80)
    print("API VERGİ DETAYLARI TESTİ")
    print("=" * 80 + "\n")
    
    test_tax_details_in_api()
