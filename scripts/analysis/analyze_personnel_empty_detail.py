"""
Personel kartında cari bilgisi olmayan 88,536 satırı detaylandır
"""
import sys
sys.path.append('.')

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

def analyze_personnel_empty():
    """335 ile ilişkili ama dolduramadığımız 88,536 satırı analiz et"""
    
    with engine.connect() as conn:
        print("\n" + "="*70)
        print("335 PERSONELİNDE CARİ OLMAYAN 88,536 SATIRIN DETAYI")
        print("="*70)
        
        # Hangi hesap kodları bu kategoride?
        print("\n📋 HESAP KODU DAĞILIMI:")
        result = conn.execute(text("""
            SELECT 
                a.code,
                a.name,
                COUNT(*) as count
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE tl.contact_id IS NULL
              AND EXISTS (
                  SELECT 1
                  FROM transaction_lines tl3
                  JOIN accounts a3 ON tl3.account_id = a3.id
                  JOIN personnel p ON a3.id = p.account_id
                  WHERE tl3.transaction_id = tl.transaction_id
                    AND a3.code LIKE '335%'
                    AND p.contact_id IS NULL
              )
              AND NOT EXISTS (
                  SELECT 1
                  FROM transaction_lines tl2
                  JOIN accounts a2 ON tl2.account_id = a2.id
                  WHERE tl2.transaction_id = tl.transaction_id
                    AND (a2.code LIKE '120%' OR a2.code LIKE '320%')
                    AND tl2.contact_id IS NOT NULL
              )
            GROUP BY a.code, a.name
            ORDER BY count DESC
            LIMIT 20
        """))
        
        total_shown = 0
        for idx, row in enumerate(result, 1):
            print(f"{idx:2}. {row.code} - {row.name}: {row.count:,}")
            total_shown += row.count
        
        print(f"\n   Yukarıdaki 20 hesap toplamı: {total_shown:,}")
        
        # 335 hesabının kendisi kaç satır?
        print("\n\n📋 335 HESABI (PERSONEL BORÇLARI) DETAYI:")
        result = conn.execute(text("""
            SELECT 
                a.code,
                a.name,
                COUNT(*) as count
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE tl.contact_id IS NULL
              AND a.code LIKE '335%'
            GROUP BY a.code, a.name
            ORDER BY count DESC
            LIMIT 10
        """))
        
        total_335 = 0
        for row in result:
            print(f"  {row.code} - {row.name}: {row.count:,}")
            total_335 += row.count
        
        print(f"\n  335 hesapları toplamı: {total_335:,}")
        
        # Hesap grubu dağılımı
        print("\n\n📋 HESAP GRUBU DAĞILIMI:")
        result = conn.execute(text("""
            SELECT 
                SUBSTRING(a.code, 1, 1) as account_group,
                COUNT(*) as count
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE tl.contact_id IS NULL
              AND EXISTS (
                  SELECT 1
                  FROM transaction_lines tl3
                  JOIN accounts a3 ON tl3.account_id = a3.id
                  JOIN personnel p ON a3.id = p.account_id
                  WHERE tl3.transaction_id = tl.transaction_id
                    AND a3.code LIKE '335%'
                    AND p.contact_id IS NULL
              )
              AND NOT EXISTS (
                  SELECT 1
                  FROM transaction_lines tl2
                  JOIN accounts a2 ON tl2.account_id = a2.id
                  WHERE tl2.transaction_id = tl.transaction_id
                    AND (a2.code LIKE '120%' OR a2.code LIKE '320%')
                    AND tl2.contact_id IS NOT NULL
              )
            GROUP BY SUBSTRING(a.code, 1, 1)
            ORDER BY count DESC
        """))
        
        for row in result:
            print(f"  {row.account_group}xx: {row.count:,}")
        
        # Kaç tane personel contact_id'si boş?
        print("\n\n📋 PERSONEL KARTI ANALİZİ:")
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_personnel,
                SUM(CASE WHEN contact_id IS NULL THEN 1 ELSE 0 END) as no_contact,
                SUM(CASE WHEN contact_id IS NOT NULL THEN 1 ELSE 0 END) as has_contact
            FROM personnel
            WHERE account_id IS NOT NULL
              AND account_id IN (
                  SELECT id FROM accounts WHERE code LIKE '335%'
              )
        """))
        
        row = result.fetchone()
        print(f"  Toplam personel (335 hesabı olan): {row.total_personnel:,}")
        print(f"  Contact_id boş olanlar: {row.no_contact:,}")
        print(f"  Contact_id dolu olanlar: {row.has_contact:,}")
        
        # Örnek personeller
        print("\n  Örnek personeller (contact_id boş):")
        result = conn.execute(text("""
            SELECT 
                p.id,
                CONCAT(p.first_name, ' ', p.last_name) as name,
                p.tckn,
                a.code as account_code,
                a.name as account_name
            FROM personnel p
            JOIN accounts a ON p.account_id = a.id
            WHERE p.contact_id IS NULL
              AND a.code LIKE '335%'
            LIMIT 5
        """))
        
        for row in result:
            print(f"    • {row.name} (TCKN: {row.tckn}) - {row.account_code}")

if __name__ == "__main__":
    analyze_personnel_empty()
