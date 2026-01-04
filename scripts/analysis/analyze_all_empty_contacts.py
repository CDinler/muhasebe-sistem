"""
TÜM hesaplardaki boş contact_id satırlarını analiz et
(740 ve 770 dışındakiler)
"""
import sys
sys.path.append('.')

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

def analyze_all_empty_contacts():
    """Tüm hesaplardaki boş contact_id'leri analiz et"""
    
    with engine.connect() as conn:
        # 1. Toplam boş contact_id sayısı (740/770 hariç)
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_empty,
                COUNT(DISTINCT tl.transaction_id) as distinct_transactions,
                COUNT(DISTINCT a.code) as distinct_accounts
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE tl.contact_id IS NULL
              AND a.code NOT LIKE '740%'
              AND a.code NOT LIKE '770%'
        """))
        stats = result.fetchone()
        print(f"\n📊 GENEL İSTATİSTİKLER (740/770 hariç)")
        print(f"Toplam boş contact_id satırı: {stats.total_empty}")
        print(f"Etkilenen fiş sayısı: {stats.distinct_transactions}")
        print(f"Etkilenen farklı hesap kodu: {stats.distinct_accounts}")
        
        # 2. Hesap kodu gruplarına göre dağılım
        print("\n📋 HESAP KODU GRUPLARINA GÖRE DAĞILIM:")
        result = conn.execute(text("""
            SELECT 
                SUBSTRING(a.code, 1, 1) as account_group,
                COUNT(*) as count,
                COUNT(DISTINCT tl.transaction_id) as transaction_count
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE tl.contact_id IS NULL
              AND a.code NOT LIKE '740%'
              AND a.code NOT LIKE '770%'
            GROUP BY SUBSTRING(a.code, 1, 1)
            ORDER BY count DESC
        """))
        
        for row in result:
            print(f"  {row.account_group}xx: {row.count:,} satır, {row.transaction_count:,} fiş")
        
        # 3. En çok boş olan hesap kodları (top 10)
        print("\n📋 EN ÇOK BOŞ CONTACT_ID OLAN HESAPLAR:")
        result = conn.execute(text("""
            SELECT 
                a.code,
                a.name,
                COUNT(*) as count
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE tl.contact_id IS NULL
              AND a.code NOT LIKE '740%'
              AND a.code NOT LIKE '770%'
            GROUP BY a.code, a.name
            ORDER BY count DESC
            LIMIT 10
        """))
        
        for row in result:
            print(f"  {row.code} - {row.name}: {row.count:,} satır")
        
        # 4. Aynı fişteki 120/320 carilerinden doldurabileceğimiz satırlar
        result = conn.execute(text("""
            SELECT COUNT(*) as fillable_from_120_320
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE tl.contact_id IS NULL
              AND a.code NOT LIKE '740%'
              AND a.code NOT LIKE '770%'
              AND a.code NOT LIKE '120%'
              AND a.code NOT LIKE '320%'
              AND a.code NOT LIKE '335%'
              AND EXISTS (
                  SELECT 1 
                  FROM transaction_lines tl2
                  JOIN accounts a2 ON tl2.account_id = a2.id
                  WHERE tl2.transaction_id = tl.transaction_id
                    AND (a2.code LIKE '120%' OR a2.code LIKE '320%')
                    AND tl2.contact_id IS NOT NULL
              )
        """))
        fillable = result.fetchone()
        print(f"\n✅ 120/320 carilerinden doldurabileceğimiz: {fillable.fillable_from_120_320:,}")
        
        # 5. Aynı fişteki 335 personelinden doldurabileceğimiz satırlar
        result = conn.execute(text("""
            SELECT COUNT(*) as fillable_from_335
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE tl.contact_id IS NULL
              AND a.code NOT LIKE '740%'
              AND a.code NOT LIKE '770%'
              AND a.code NOT LIKE '120%'
              AND a.code NOT LIKE '320%'
              AND a.code NOT LIKE '335%'
              AND EXISTS (
                  SELECT 1 
                  FROM transaction_lines tl3
                  JOIN accounts a3 ON tl3.account_id = a3.id
                  JOIN personnel p ON a3.id = p.account_id
                  WHERE tl3.transaction_id = tl.transaction_id
                    AND a3.code LIKE '335%'
                    AND p.contact_id IS NOT NULL
              )
        """))
        personnel_fillable = result.fetchone()
        print(f"✅ 335 personelinden doldurabileceğimiz: {personnel_fillable.fillable_from_335:,}")
        
        # 6. TEK eşleşmesi olanlar (GÜVENLİ)
        result = conn.execute(text("""
            SELECT COUNT(*) as safe_updates
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE tl.contact_id IS NULL
              AND a.code NOT LIKE '740%'
              AND a.code NOT LIKE '770%'
              AND a.code NOT LIKE '120%'
              AND a.code NOT LIKE '320%'
              AND a.code NOT LIKE '335%'
              AND (
                  -- Tek 120/320 carisi var
                  (SELECT COUNT(DISTINCT tl2.contact_id)
                   FROM transaction_lines tl2
                   JOIN accounts a2 ON tl2.account_id = a2.id
                   WHERE tl2.transaction_id = tl.transaction_id
                     AND (a2.code LIKE '120%' OR a2.code LIKE '320%')
                     AND tl2.contact_id IS NOT NULL) = 1
                  OR
                  -- Tek 335 personeli var
                  (SELECT COUNT(DISTINCT p.contact_id)
                   FROM transaction_lines tl3
                   JOIN accounts a3 ON tl3.account_id = a3.id
                   JOIN personnel p ON a3.id = p.account_id
                   WHERE tl3.transaction_id = tl.transaction_id
                     AND a3.code LIKE '335%'
                     AND p.contact_id IS NOT NULL) = 1
              )
        """))
        safe = result.fetchone()
        print(f"\n🔒 GÜVENLİ GÜNCELLEME (tek eşleşme): {safe.safe_updates:,}")
        
        # 7. RİSKLİ durumlar
        result = conn.execute(text("""
            SELECT COUNT(*) as risky_updates
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE tl.contact_id IS NULL
              AND a.code NOT LIKE '740%'
              AND a.code NOT LIKE '770%'
              AND a.code NOT LIKE '120%'
              AND a.code NOT LIKE '320%'
              AND a.code NOT LIKE '335%'
              AND (
                  -- Birden fazla 120/320 carisi var
                  (SELECT COUNT(DISTINCT tl2.contact_id)
                   FROM transaction_lines tl2
                   JOIN accounts a2 ON tl2.account_id = a2.id
                   WHERE tl2.transaction_id = tl.transaction_id
                     AND (a2.code LIKE '120%' OR a2.code LIKE '320%')
                     AND tl2.contact_id IS NOT NULL) > 1
                  OR
                  -- Birden fazla 335 personeli var
                  (SELECT COUNT(DISTINCT p.contact_id)
                   FROM transaction_lines tl3
                   JOIN accounts a3 ON tl3.account_id = a3.id
                   JOIN personnel p ON a3.id = p.account_id
                   WHERE tl3.transaction_id = tl.transaction_id
                     AND a3.code LIKE '335%'
                     AND p.contact_id IS NOT NULL) > 1
              )
        """))
        risky = result.fetchone()
        print(f"⚠️  RİSKLİ (birden fazla eşleşme): {risky.risky_updates:,}")
        
        # 8. Hiç eşleşmesi olmayanlar
        total_with_match = fillable.fillable_from_120_320 + personnel_fillable.fillable_from_335
        no_match = stats.total_empty - total_with_match
        print(f"❌ Hiç eşleşmesi olmayanlar: {no_match:,}")

if __name__ == "__main__":
    analyze_all_empty_contacts()
