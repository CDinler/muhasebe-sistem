"""
Luca'daki mevcut 335 personel hesapları ve contact ilişkilerini incele
"""
import sys
sys.path.append('.')

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

def analyze_luca_personnel_structure():
    """Luca'da 335 hesapları nasıl yapılandırılmış?"""
    
    with engine.connect() as conn:
        print("\n" + "="*70)
        print("LUCA'DAKİ MEVCUT 335 PERSONEL YAPISINI İNCELE")
        print("="*70)
        
        # 1. 335 hesapları
        print("\n📋 335 HESAPLARI:")
        result = conn.execute(text("""
            SELECT COUNT(*) as count
            FROM accounts
            WHERE code LIKE '335%'
        """))
        print(f"  Toplam 335 hesabı: {result.fetchone().count:,}")
        
        # 2. 335 hesaplarında transaction_lines'da contact_id kullanımı
        print("\n📋 335 HESAPLARINDA CONTACT KULLANIMI:")
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_lines,
                SUM(CASE WHEN tl.contact_id IS NOT NULL THEN 1 ELSE 0 END) as with_contact,
                SUM(CASE WHEN tl.contact_id IS NULL THEN 1 ELSE 0 END) as without_contact
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE a.code LIKE '335%'
        """))
        row = result.fetchone()
        print(f"  Toplam satır: {row.total_lines:,}")
        print(f"  Contact_id dolu: {row.with_contact:,}")
        print(f"  Contact_id boş: {row.without_contact:,}")
        
        # 3. 335 hesaplarında kullanılan contact'ları incele
        if row.with_contact > 0:
            print("\n📋 335'TE KULLANILAN CONTACT'LAR:")
            result = conn.execute(text("""
                SELECT 
                    c.id,
                    c.name,
                    c.tax_number,
                    c.tax_office,
                    c.contact_type,
                    COUNT(*) as usage_count
                FROM transaction_lines tl
                JOIN accounts a ON tl.account_id = a.id
                JOIN contacts c ON tl.contact_id = c.id
                WHERE a.code LIKE '335%'
                GROUP BY c.id, c.name, c.tax_number, c.tax_office, c.contact_type
                ORDER BY usage_count DESC
                LIMIT 10
            """))
            
            for row in result:
                print(f"\n  {row.name}")
                print(f"    TCKN/VKN: {row.tax_number}")
                print(f"    Vergi Dairesi: {row.tax_office}")
                print(f"    Tip: {row.contact_type}")
                print(f"    Kullanım: {row.usage_count:,} satır")
        
        # 4. Aynı kişi hem 320 hem 335'te mi?
        print("\n\n📋 HEM 320 HEM 335'TE KULLANILAN CONTACT'LAR:")
        result = conn.execute(text("""
            SELECT 
                c.id,
                c.name,
                c.tax_number,
                c.contact_type,
                SUM(CASE WHEN a.code LIKE '320%' THEN 1 ELSE 0 END) as used_in_320,
                SUM(CASE WHEN a.code LIKE '335%' THEN 1 ELSE 0 END) as used_in_335,
                SUM(CASE WHEN a.code LIKE '120%' THEN 1 ELSE 0 END) as used_in_120
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            JOIN contacts c ON tl.contact_id = c.id
            WHERE (a.code LIKE '320%' OR a.code LIKE '335%' OR a.code LIKE '120%')
              AND tl.contact_id IS NOT NULL
            GROUP BY c.id, c.name, c.tax_number, c.contact_type
            HAVING used_in_335 > 0 AND (used_in_320 > 0 OR used_in_120 > 0)
            ORDER BY (used_in_320 + used_in_335 + used_in_120) DESC
            LIMIT 15
        """))
        
        dual_count = 0
        for row in result:
            dual_count += 1
            print(f"\n  {row.name}")
            print(f"    TCKN/VKN: {row.tax_number}")
            print(f"    Tip: {row.contact_type}")
            print(f"    120'de: {row.used_in_120}, 320'de: {row.used_in_320}, 335'te: {row.used_in_335}")
        
        if dual_count == 0:
            print("  ❌ Hiç bulunamadı")
        else:
            print(f"\n  ✅ Toplam {dual_count} kişi hem ticari hem personel")
        
        # 5. Personnel tablosunda contact_id dolu olan var mı?
        print("\n\n📋 PERSONNEL TABLOSUNDA CONTACT İLİŞKİSİ:")
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN contact_id IS NOT NULL THEN 1 ELSE 0 END) as with_contact,
                SUM(CASE WHEN contact_id IS NULL THEN 1 ELSE 0 END) as without_contact
            FROM personnel
        """))
        row = result.fetchone()
        print(f"  Toplam personel: {row.total:,}")
        print(f"  Contact_id dolu: {row.with_contact:,}")
        print(f"  Contact_id boş: {row.without_contact:,}")
        
        # 6. Contacts tablosundaki tip dağılımı
        print("\n\n📋 CONTACTS TABLOSU TİP DAĞILIMI:")
        result = conn.execute(text("""
            SELECT 
                contact_type,
                COUNT(*) as count
            FROM contacts
            GROUP BY contact_type
            ORDER BY count DESC
        """))
        
        for row in result:
            print(f"  {row.contact_type or 'NULL'}: {row.count:,}")

if __name__ == "__main__":
    analyze_luca_personnel_structure()
