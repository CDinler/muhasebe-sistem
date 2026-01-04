"""
ibanlar.csv dosyasından contacts ve einvoices tablolarındaki IBAN bilgilerini güncelle
VKN'lerde başındaki sıfırları düzeltir
"""
import pandas as pd
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.contact import Contact
from app.models.einvoice import EInvoice

def main():
    # CSV dosyasını oku
    csv_path = r"C:\Projects\muhasebe-sistem\ibanlar.csv"
    df = pd.read_csv(csv_path, sep=';', dtype=str)
    
    print(f"📋 CSV'den {len(df)} kayıt okundu")
    
    # VKN/TCKN'leri temizle ve standardize et
    df['vkn/tckn'] = df['vkn/tckn'].fillna('').str.strip()
    df['iban'] = df['iban'].fillna('').str.strip()
    
    # Boş satırları temizle
    df = df[df['vkn/tckn'] != '']
    df = df[df['iban'] != '']
    
    print(f"📋 Geçerli kayıt sayısı: {len(df)}")
    
    # VKN'leri 10 haneli yap (başına sıfır ekle)
    def standardize_vkn_tckn(value):
        value = value.strip()
        # 11 haneli ise TCKN, olduğu gibi bırak
        if len(value) == 11:
            return value
        # 10 haneden küçük ise VKN, başına sıfır ekle
        elif len(value) < 10:
            return value.zfill(10)
        else:
            return value
    
    df['vkn_standardized'] = df['vkn/tckn'].apply(standardize_vkn_tckn)
    
    # IBAN dictionary oluştur (VKN/TCKN -> IBAN)
    iban_dict = dict(zip(df['vkn_standardized'], df['iban']))
    
    print(f"📊 {len(iban_dict)} benzersiz VKN/TCKN-IBAN eşleşmesi bulundu")
    
    db = SessionLocal()
    
    try:
        # 1. Contacts tablosunu güncelle
        print("\n" + "="*60)
        print("CONTACTS TABLOSU GÜNCELLENİYOR")
        print("="*60)
        
        # IBAN'ı NULL veya boş olan contacts
        contacts = db.query(Contact).filter(
            (Contact.iban == None) | (Contact.iban == '')
        ).all()
        
        print(f"📋 IBAN bilgisi olmayan {len(contacts)} contact bulundu")
        
        updated_contacts = 0
        for contact in contacts:
            # VKN veya TCKN ile eşleştir (tax_number alanında her ikisi de olabilir)
            tax_id = None
            if contact.tax_number:
                tax_id = contact.tax_number.strip()
            
            if tax_id and tax_id in iban_dict:
                contact.iban = iban_dict[tax_id]
                updated_contacts += 1
                
                if updated_contacts % 50 == 0:
                    print(f"  💾 {updated_contacts} contact güncellendi...")
                    db.commit()
        
        db.commit()
        print(f"✅ Toplam {updated_contacts} contact'ın IBAN bilgisi güncellendi")
        
        # 2. EInvoices tablosunu güncelle
        print("\n" + "="*60)
        print("EINVOICES TABLOSU GÜNCELLENİYOR")
        print("="*60)
        
        # supplier_iban'ı NULL veya boş olan e-faturalar
        einvoices = db.query(EInvoice).filter(
            (EInvoice.supplier_iban == None) | (EInvoice.supplier_iban == '')
        ).all()
        
        print(f"📋 IBAN bilgisi olmayan {len(einvoices)} e-fatura bulundu")
        
        updated_einvoices = 0
        for einvoice in einvoices:
            # supplier_tax_number ile eşleştir (VKN veya TCKN olabilir)
            tax_id = None
            if einvoice.supplier_tax_number:
                tax_id = einvoice.supplier_tax_number.strip()
            
            if tax_id and tax_id in iban_dict:
                einvoice.supplier_iban = iban_dict[tax_id]
                updated_einvoices += 1
                
                if updated_einvoices % 100 == 0:
                    print(f"  💾 {updated_einvoices} e-fatura güncellendi...")
                    db.commit()
        
        db.commit()
        print(f"✅ Toplam {updated_einvoices} e-fatura'nın IBAN bilgisi güncellendi")
        
        # Özet
        print("\n" + "="*60)
        print("ÖZET")
        print("="*60)
        print(f"📊 CSV'den okunan kayıt: {len(df)}")
        print(f"📊 Güncellenen contact: {updated_contacts}")
        print(f"📊 Güncellenen e-fatura: {updated_einvoices}")
        print(f"📊 Toplam güncelleme: {updated_contacts + updated_einvoices}")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
