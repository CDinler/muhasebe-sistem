"""
Boş kalan contact_id satırlarının neden boş kaldığını analiz et
"""
import sys
sys.path.append('.')

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

def analyze_why_empty():
    """Boş kalan satırların nedenlerini kategorize et"""
    
    with engine.connect() as conn:
        print("\n" + "="*70)
        print("BOŞ KALAN CONTACT_ID SATIRLARININ SEBEP ANALİZİ")
        print("="*70)
        
        # Toplam boş sayısı
        result = conn.execute(text("""
            SELECT COUNT(*) as total_empty
            FROM transaction_lines tl
            WHERE tl.contact_id IS NULL
        """))
        total_empty = result.fetchone().total_empty
        print(f"\n📊 TOPLAM BOŞ SATIR: {total_empty:,}\n")
        
        # KATEGORI 1: Hiç 120/320/335 hesabı olmayan fişler
        print("1️⃣  HİÇ 120/320/335 HESABI OLMAYAN FİŞLER")
        print("   (İç transfer, nakit işlemler, kesinti kayıtları)")
        result = conn.execute(text("""
            SELECT COUNT(*) as count
            FROM transaction_lines tl
            WHERE tl.contact_id IS NULL
              AND NOT EXISTS (
                  SELECT 1
                  FROM transaction_lines tl2
                  JOIN accounts a2 ON tl2.account_id = a2.id
                  WHERE tl2.transaction_id = tl.transaction_id
                    AND (a2.code LIKE '120%' OR a2.code LIKE '320%' OR a2.code LIKE '335%')
              )
        """))
        no_related_accounts = result.fetchone().count
        pct = (no_related_accounts / total_empty * 100) if total_empty > 0 else 0
        print(f"   📌 {no_related_accounts:,} satır ({pct:.1f}%)")
        
        # En çok kullanılan hesaplar
        print("\n   En çok kullanılan hesaplar:")
        result = conn.execute(text("""
            SELECT 
                a.code,
                a.name,
                COUNT(*) as count
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE tl.contact_id IS NULL
              AND NOT EXISTS (
                  SELECT 1
                  FROM transaction_lines tl2
                  JOIN accounts a2 ON tl2.account_id = a2.id
                  WHERE tl2.transaction_id = tl.transaction_id
                    AND (a2.code LIKE '120%' OR a2.code LIKE '320%' OR a2.code LIKE '335%')
              )
            GROUP BY a.code, a.name
            ORDER BY count DESC
            LIMIT 10
        """))
        for row in result:
            print(f"     • {row.code} - {row.name}: {row.count:,}")
        
        # KATEGORI 2: 120/320 var ama contact_id NULL olan satırlar
        print("\n\n2️⃣  120/320 HESABI VAR AMA CONTACT_ID BOŞ")
        print("   (120/320 satırlarında da cari bilgisi yok)")
        result = conn.execute(text("""
            SELECT COUNT(*) as count
            FROM transaction_lines tl
            WHERE tl.contact_id IS NULL
              AND EXISTS (
                  SELECT 1
                  FROM transaction_lines tl2
                  JOIN accounts a2 ON tl2.account_id = a2.id
                  WHERE tl2.transaction_id = tl.transaction_id
                    AND (a2.code LIKE '120%' OR a2.code LIKE '320%')
                    AND tl2.contact_id IS NULL
              )
              AND NOT EXISTS (
                  SELECT 1
                  FROM transaction_lines tl2
                  JOIN accounts a2 ON tl2.account_id = a2.id
                  WHERE tl2.transaction_id = tl.transaction_id
                    AND (a2.code LIKE '120%' OR a2.code LIKE '320%')
                    AND tl2.contact_id IS NOT NULL
              )
        """))
        related_accounts_also_null = result.fetchone().count
        pct = (related_accounts_also_null / total_empty * 100) if total_empty > 0 else 0
        print(f"   📌 {related_accounts_also_null:,} satır ({pct:.1f}%)")
        
        # Örnek fişler
        print("\n   Örnek fişler (120/320 de cari yok):")
        result = conn.execute(text("""
            SELECT DISTINCT
                t.id,
                t.transaction_number,
                t.transaction_date,
                t.description,
                (SELECT GROUP_CONCAT(DISTINCT a2.code ORDER BY a2.code SEPARATOR ', ')
                 FROM transaction_lines tl2
                 JOIN accounts a2 ON tl2.account_id = a2.id
                 WHERE tl2.transaction_id = t.id) as hesaplar
            FROM transactions t
            JOIN transaction_lines tl ON t.id = tl.transaction_id
            WHERE tl.contact_id IS NULL
              AND EXISTS (
                  SELECT 1
                  FROM transaction_lines tl2
                  JOIN accounts a2 ON tl2.account_id = a2.id
                  WHERE tl2.transaction_id = tl.transaction_id
                    AND (a2.code LIKE '120%' OR a2.code LIKE '320%')
                    AND tl2.contact_id IS NULL
              )
              AND NOT EXISTS (
                  SELECT 1
                  FROM transaction_lines tl2
                  JOIN accounts a2 ON tl2.account_id = a2.id
                  WHERE tl2.transaction_id = tl.transaction_id
                    AND (a2.code LIKE '120%' OR a2.code LIKE '320%')
                    AND tl2.contact_id IS NOT NULL
              )
            LIMIT 5
        """))
        for row in result:
            print(f"     • Fiş #{row.id} - {row.transaction_number} ({row.transaction_date})")
            print(f"       Hesaplar: {row.hesaplar}")
        
        # KATEGORI 3: 335 var ama personnel.contact_id NULL
        print("\n\n3️⃣  335 HESABI VAR AMA PERSONNEL.CONTACT_ID BOŞ")
        print("   (Personel kartında cari bilgisi eksik)")
        result = conn.execute(text("""
            SELECT COUNT(*) as count
            FROM transaction_lines tl
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
        """))
        personnel_no_contact = result.fetchone().count
        pct = (personnel_no_contact / total_empty * 100) if total_empty > 0 else 0
        print(f"   📌 {personnel_no_contact:,} satır ({pct:.1f}%)")
        
        # KATEGORI 4: Birden fazla cari var (RİSKLİ)
        print("\n\n4️⃣  BİRDEN FAZLA CARİ/PERSONEL VAR (RİSKLİ)")
        print("   (Hangi carinin seçileceği belirsiz)")
        result = conn.execute(text("""
            SELECT COUNT(*) as count
            FROM transaction_lines tl
            WHERE tl.contact_id IS NULL
              AND (
                  (SELECT COUNT(DISTINCT tl2.contact_id)
                   FROM transaction_lines tl2
                   JOIN accounts a2 ON tl2.account_id = a2.id
                   WHERE tl2.transaction_id = tl.transaction_id
                     AND (a2.code LIKE '120%' OR a2.code LIKE '320%')
                     AND tl2.contact_id IS NOT NULL) > 1
                  OR
                  (SELECT COUNT(DISTINCT p.contact_id)
                   FROM transaction_lines tl3
                   JOIN accounts a3 ON tl3.account_id = a3.id
                   JOIN personnel p ON a3.id = p.account_id
                   WHERE tl3.transaction_id = tl.transaction_id
                     AND a3.code LIKE '335%'
                     AND p.contact_id IS NOT NULL) > 1
              )
        """))
        multiple_contacts = result.fetchone().count
        pct = (multiple_contacts / total_empty * 100) if total_empty > 0 else 0
        print(f"   📌 {multiple_contacts:,} satır ({pct:.1f}%)")
        
        # Örnek riskli fişler
        if multiple_contacts > 0:
            print("\n   Örnek riskli fişler:")
            result = conn.execute(text("""
                SELECT DISTINCT
                    t.id,
                    t.transaction_number,
                    t.transaction_date,
                    (SELECT COUNT(DISTINCT tl2.contact_id)
                     FROM transaction_lines tl2
                     JOIN accounts a2 ON tl2.account_id = a2.id
                     WHERE tl2.transaction_id = t.id
                       AND (a2.code LIKE '120%' OR a2.code LIKE '320%')
                       AND tl2.contact_id IS NOT NULL) as cari_count,
                    (SELECT GROUP_CONCAT(DISTINCT c.name SEPARATOR ' | ')
                     FROM transaction_lines tl2
                     JOIN contacts c ON tl2.contact_id = c.id
                     WHERE tl2.transaction_id = t.id) as cariler
                FROM transactions t
                WHERE EXISTS (
                    SELECT 1 FROM transaction_lines tl
                    WHERE tl.transaction_id = t.id AND tl.contact_id IS NULL
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
                print(f"     • Fiş #{row.id} - {row.transaction_number}")
                print(f"       {row.cari_count} farklı cari: {row.cariler[:80]}...")
        
        # ÖZET
        print("\n\n" + "="*70)
        print("📊 ÖZET")
        print("="*70)
        kategorize_edilen = no_related_accounts + related_accounts_also_null + personnel_no_contact + multiple_contacts
        diger = total_empty - kategorize_edilen
        
        print(f"1️⃣  Hiç ilişkili hesap yok: {no_related_accounts:,} ({no_related_accounts/total_empty*100:.1f}%)")
        print(f"2️⃣  120/320 de cari yok: {related_accounts_also_null:,} ({related_accounts_also_null/total_empty*100:.1f}%)")
        print(f"3️⃣  Personel cari yok: {personnel_no_contact:,} ({personnel_no_contact/total_empty*100:.1f}%)")
        print(f"4️⃣  Riskli (çoklu cari): {multiple_contacts:,} ({multiple_contacts/total_empty*100:.1f}%)")
        if diger > 0:
            print(f"5️⃣  Diğer: {diger:,} ({diger/total_empty*100:.1f}%)")
        print(f"\n✅ TOPLAM: {total_empty:,}")

if __name__ == "__main__":
    analyze_why_empty()
