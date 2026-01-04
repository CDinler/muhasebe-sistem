"""
740 ve 770 hesap kodlarındaki contact_id boş satırları analiz et
ve güvenli update için script üret
"""
import sys
sys.path.append('.')

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

def analyze_empty_contacts():
    """740 ve 770 hesaplardaki boş contact_id'leri analiz et"""
    
    with engine.connect() as conn:
        # 1. Toplam boş contact_id sayısı
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_empty,
                COUNT(DISTINCT tl.transaction_id) as distinct_transactions
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE (a.code LIKE '740%' OR a.code LIKE '770%')
              AND tl.contact_id IS NULL
        """))
        stats = result.fetchone()
        print(f"\n📊 GENEL İSTATİSTİKLER")
        print(f"Toplam boş contact_id satırı: {stats.total_empty}")
        print(f"Etkilenen fiş sayısı: {stats.distinct_transactions}")
        
        # 2. Aynı fişteki 120/320 carilerinden doldurabileceğimiz satırlar
        result = conn.execute(text("""
            SELECT COUNT(*) as fillable_from_120_320
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE (a.code LIKE '740%' OR a.code LIKE '770%')
              AND tl.contact_id IS NULL
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
        print(f"\n✅ 120/320 carilerinden doldurabileceğimiz: {fillable.fillable_from_120_320}")
        
        # 3. Aynı fişteki 335 personelinden doldurabileceğimiz satırlar
        result = conn.execute(text("""
            SELECT COUNT(*) as fillable_from_335
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE (a.code LIKE '740%' OR a.code LIKE '770%')
              AND tl.contact_id IS NULL
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
        print(f"✅ 335 personelinden doldurabileceğimiz: {personnel_fillable.fillable_from_335}")
        
        # 4. TEK eşleşmesi olanlar (GÜVENLİ)
        result = conn.execute(text("""
            SELECT COUNT(*) as safe_updates
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE (a.code LIKE '740%' OR a.code LIKE '770%')
              AND tl.contact_id IS NULL
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
        print(f"\n🔒 GÜVENLİ GÜNCELLEME (tek eşleşme): {safe.safe_updates}")
        
        # 5. RİSKLİ durumlar (birden fazla cari/personel)
        result = conn.execute(text("""
            SELECT COUNT(*) as risky_updates
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE (a.code LIKE '740%' OR a.code LIKE '770%')
              AND tl.contact_id IS NULL
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
        print(f"⚠️  RİSKLİ (birden fazla eşleşme): {risky.risky_updates}")
        
        # 6. Hiç eşleşmesi olmayanlar
        total_with_match = fillable.fillable_from_120_320 + personnel_fillable.fillable_from_335
        no_match = stats.total_empty - total_with_match
        print(f"❌ Hiç eşleşmesi olmayanlar: {no_match}")
        
        # 7. Örnek riskli fişler göster
        print("\n\n📋 ÖRNEK RİSKLİ FİŞLER (birden fazla cari/personel):")
        result = conn.execute(text("""
            SELECT DISTINCT
                t.id,
                t.transaction_number,
                t.transaction_date,
                t.description,
                (SELECT COUNT(DISTINCT tl2.contact_id)
                 FROM transaction_lines tl2
                 JOIN accounts a2 ON tl2.account_id = a2.id
                 WHERE tl2.transaction_id = t.id
                   AND (a2.code LIKE '120%' OR a2.code LIKE '320%')
                   AND tl2.contact_id IS NOT NULL) as cari_count,
                (SELECT GROUP_CONCAT(DISTINCT c.name SEPARATOR ', ')
                 FROM transaction_lines tl2
                 JOIN contacts c ON tl2.contact_id = c.id
                 WHERE tl2.transaction_id = t.id) as cariler
            FROM transactions t
            WHERE EXISTS (
                SELECT 1 FROM transaction_lines tl
                JOIN accounts a ON tl.account_id = a.id
                WHERE tl.transaction_id = t.id
                  AND (a.code LIKE '740%' OR a.code LIKE '770%')
                  AND tl.contact_id IS NULL
            )
            AND (
                SELECT COUNT(DISTINCT tl2.contact_id)
                FROM transaction_lines tl2
                JOIN accounts a2 ON tl2.account_id = a2.id
                WHERE tl2.transaction_id = t.id
                  AND (a2.code LIKE '120%' OR a2.code LIKE '320%')
                  AND tl2.contact_id IS NOT NULL
            ) > 1
            LIMIT 5
        """))
        
        for row in result:
            print(f"\nFiş #{row.id} - {row.transaction_number}")
            print(f"  Tarih: {row.transaction_date}")
            print(f"  Cari sayısı: {row.cari_count}")
            print(f"  Cariler: {row.cariler}")

if __name__ == "__main__":
    analyze_empty_contacts()
