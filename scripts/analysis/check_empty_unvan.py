"""
Ünvan bilgisi olmayan e-faturaları kontrol et
"""
import pandas as pd
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

def main():
    db = SessionLocal()
    
    try:
        # AAA2025000000338 faturasını kontrol et
        query = """
        SELECT 
            id,
            invoice_number,
            supplier_name,
            customer_name,
            invoice_category,
            supplier_tax_number,
            customer_tax_number
        FROM einvoices 
        WHERE invoice_number = 'AAA2025000000338'
        """
        
        result = pd.read_sql(query, db.bind)
        print("=" * 80)
        print("AAA2025000000338 FATURA BİLGİLERİ:")
        print("=" * 80)
        print(result.to_string())
        
        # Genel olarak supplier_name veya customer_name boş olanları bul
        query2 = """
        SELECT 
            COUNT(*) as toplam,
            SUM(CASE WHEN supplier_name IS NULL OR supplier_name = '' THEN 1 ELSE 0 END) as bos_supplier_name,
            SUM(CASE WHEN customer_name IS NULL OR customer_name = '' THEN 1 ELSE 0 END) as bos_customer_name
        FROM einvoices
        """
        
        result2 = pd.read_sql(query2, db.bind)
        print("\n" + "=" * 80)
        print("GENEL İSTATİSTİKLER:")
        print("=" * 80)
        print(result2.to_string())
        
        # Boş supplier_name olanlardan birkaç örnek
        query3 = """
        SELECT 
            id,
            invoice_number,
            supplier_name,
            customer_name,
            invoice_category,
            supplier_tax_number
        FROM einvoices 
        WHERE (supplier_name IS NULL OR supplier_name = '')
        LIMIT 10
        """
        
        result3 = pd.read_sql(query3, db.bind)
        print("\n" + "=" * 80)
        print("BOŞ SUPPLIER_NAME ÖRNEKLER (İLK 10):")
        print("=" * 80)
        print(result3.to_string())
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
