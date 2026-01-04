"""
Tüm personeller için contacts tablosunda cari kartı oluştur
ve personnel.contact_id'yi güncelle
"""
import sys
sys.path.append('.')

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

def create_personnel_contacts():
    """Her personel için contact kartı oluştur"""
    
    with engine.begin() as conn:
        print("🔄 Personeller için cari kartları oluşturuluyor...\n")
        
        # 1. Önce kaç personel etkilenecek?
        result = conn.execute(text("""
            SELECT COUNT(*) as count
            FROM personnel
            WHERE contact_id IS NULL
              AND account_id IS NOT NULL
        """))
        count = result.fetchone().count
        print(f"📌 İşlenecek personel sayısı: {count:,}\n")
        
        # 2. Önce mevcut contact sayısını kontrol et (aynı TCKN'li)
        result = conn.execute(text("""
            SELECT COUNT(*) as count
            FROM personnel p
            JOIN contacts c ON c.tax_number = p.tckn
            WHERE p.contact_id IS NULL
              AND p.account_id IS NOT NULL
              AND p.tckn IS NOT NULL
        """))
        
        existing_count = result.fetchone().count
        print(f"📌 Zaten contact kartı olan (TCKN eşleşen): {existing_count:,}")
        
        # 3. Yeni contact kartı oluştur (sadece TCKN eşleşmeyenler için)
        result = conn.execute(text("""
            INSERT INTO contacts (name, tax_number, contact_type, is_active)
            SELECT 
                CONCAT(p.first_name, ' ', p.last_name) as name,
                p.tckn as tax_number,
                'both' as contact_type,
                p.is_active
            FROM personnel p
            WHERE p.contact_id IS NULL
              AND p.account_id IS NOT NULL
              AND p.tckn IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1 FROM contacts c WHERE c.tax_number = p.tckn
              )
        """))
        
        created = result.rowcount
        print(f"✅ Yeni contact kartı oluşturuldu: {created:,}")
        
        # 4. Personnel.contact_id'yi güncelle (mevcut + yeni oluşturulan)
        result = conn.execute(text("""
            UPDATE personnel p
            JOIN contacts c ON c.tax_number = p.tckn
            SET p.contact_id = c.id
            WHERE p.contact_id IS NULL
              AND p.account_id IS NOT NULL
              AND p.tckn IS NOT NULL
        """))
        
        updated = result.rowcount
        print(f"✅ Personnel.contact_id güncellendi: {updated:,}")
        
        # 4. TCKN olmayan personeller (güncellenmedi)
        result = conn.execute(text("""
            SELECT COUNT(*) as count
            FROM personnel
            WHERE contact_id IS NULL
              AND account_id IS NOT NULL
        """))
        
        still_empty = result.fetchone().count
        print(f"\n📌 TCKN olmadığı için güncellenemeyen: {still_empty}")
        
        if still_empty > 0:
            print("\n   Örnek TCKN'siz personeller:")
            result = conn.execute(text("""
                SELECT 
                    CONCAT(first_name, ' ', last_name) as name,
                    tckn,
                    sicil_no
                FROM personnel
                WHERE contact_id IS NULL
                  AND account_id IS NOT NULL
                LIMIT 5
            """))
            
            for row in result:
                print(f"     • {row.name} - TCKN: {row.tckn}, Sicil: {row.sicil_no}")

if __name__ == "__main__":
    confirm = input("\n⚠️  Her personel için cari kartı oluşturulacak. Devam? (evet/hayır): ")
    if confirm.lower() in ['evet', 'e', 'yes', 'y']:
        create_personnel_contacts()
    else:
        print("❌ İşlem iptal edildi.")
