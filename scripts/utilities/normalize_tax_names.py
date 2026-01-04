"""
Mevcut vergi kayıtlarını resmi kod listesine göre normalize et
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from app.core.database import SessionLocal
from app.models.invoice_tax import InvoiceTax
from app.models.tax_code import TaxCode

def normalize_tax_records():
    """Vergi kayıtlarını normalize et"""
    db = SessionLocal()
    
    try:
        # Referans kodlarını al
        tax_codes = {tc.code: tc for tc in db.query(TaxCode).all()}
        
        print("=" * 80)
        print("VERGİ KAYITLARINI NORMALİZE ETME")
        print("=" * 80)
        
        # Tüm vergi kayıtlarını al
        all_taxes = db.query(InvoiceTax).all()
        print(f"\nToplam {len(all_taxes)} vergi kaydı bulundu")
        
        updated_count = 0
        error_count = 0
        
        for tax in all_taxes:
            code = tax.tax_type_code
            
            if code in tax_codes:
                official_name = tax_codes[code].name
                
                # İsim farklıysa güncelle
                if tax.tax_name != official_name:
                    old_name = tax.tax_name
                    tax.tax_name = official_name
                    updated_count += 1
                    
                    if updated_count <= 10:  # İlk 10'unu göster
                        print(f"  ✓ {code}: '{old_name}' -> '{official_name}'")
            else:
                error_count += 1
                if error_count <= 5:
                    print(f"  ✗ {code}: '{tax.tax_name}' - RESMİ LİSTEDE YOK!")
        
        if updated_count > 10:
            print(f"  ... ve {updated_count - 10} kayıt daha")
        
        # Değişiklikleri kaydet
        if updated_count > 0:
            print(f"\n=== {updated_count} KAYIT GÜNCELLENİYOR ===")
            db.commit()
            print("✓ Başarıyla kaydedildi!")
        else:
            print("\n✓ Tüm kayıtlar zaten normalize")
        
        if error_count > 0:
            print(f"\n⚠ {error_count} kayıt resmi listede bulunamadı")
        
        # Sonuç özeti
        print(f"\n=== ÖZET ===")
        print(f"  Güncellenen: {updated_count}")
        print(f"  Hatalı: {error_count}")
        print(f"  Toplam: {len(all_taxes)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    normalize_tax_records()
