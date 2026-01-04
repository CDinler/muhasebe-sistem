import requests
import json

# Backend API'den preview al
url = "http://localhost:8000/api/v1/einvoices/3495/import-preview"

try:
    response = requests.post(url)
    
    if response.status_code == 200:
        data = response.json()
        
        print("✅ Preview Başarılı")
        print("=" * 100)
        
        print(f"\n📄 Transaction Bilgileri:")
        trans = data.get('transaction', {})
        print(f"  Fatura No: {data.get('invoice', {}).get('invoice_number')}")
        print(f"  Tedarikçi: {data.get('invoice', {}).get('supplier_name')}")
        print(f"  Toplam Tutar: {data.get('invoice', {}).get('payable_amount')}")
        print(f"  Para Birimi: {data.get('invoice', {}).get('currency_code')}")
        print(f"  Maliyet Merkezi: {trans.get('cost_center_name')} (ID: {trans.get('cost_center_id')})")
        print(f"  Belge Tipi: {trans.get('document_type')} (ID: {trans.get('document_type_id')})")
        print(f"  Belge Alt Tipi: {trans.get('document_subtype')} (ID: {trans.get('document_subtype_id')})")
        
        print(f"\n📋 Muhasebe Satırları ({len(trans.get('lines', []))} satır):")
        print(f"{'No':<4} {'Hesap Kodu':<15} {'Hesap Adı':<40} {'Borç':>12} {'Alacak':>12} {'Açıklama':<30}")
        print("-" * 130)
        
        total_debit = 0
        total_credit = 0
        
        for i, line in enumerate(trans.get('lines', []), 1):
            account_code = line.get('account_code', '')
            account_name = line.get('account_name', '')
            debit = line.get('debit', 0) or 0
            credit = line.get('credit', 0) or 0
            description = line.get('description', '')
            
            total_debit += debit
            total_credit += credit
            
            print(f"{i:<4} {account_code:<15} {account_name:<40} {debit:>12.2f} {credit:>12.2f} {description:<30}")
        
        print("-" * 130)
        print(f"{'TOPLAM':<60} {total_debit:>12.2f} {total_credit:>12.2f}")
        print(f"{'FARK':<60} {abs(total_debit - total_credit):>12.2f}")
        
        # Beklenen kayıt
        print("\n" + "=" * 100)
        print("🎯 BEKLENEN KAYIT (YEVMIYE_KAYDI_SABLONU.md'ye göre):")
        print("=" * 100)
        print("SATIR1: 770.00015  538,46      Tarife Ve Paket Ücretleri")
        print("SATIR2: 191.00001  107,69      Gerçek Usulde Katma Değer Vergisi %20")
        print("SATIR3: 689.00001   53,85      5035 Sayılı Kanuna Göre Özel İletişim Vergisi")
        print("SATIR4: 689.00005   14,94      Telsiz Kullanım Ücreti")
        print("SATIR5: 689.00005   81,00      Tahsilatına Aracılık Edilen Ödemeleriniz")
        print("SATIR6: 679.00001    0,00      Düzeltmeler (veya 659.00003)")
        print("SATIR7: 320.12345            795,90  Ödenecek tutar")
        
    else:
        print(f"❌ Hata: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Bağlantı hatası: {str(e)}")
