"""
740 ve 770 hesap kodlarındaki contact_id boş satırları
güvenli bir şekilde doldur (sadece tek eşleşmesi olanlar)
"""
import sys
sys.path.append('.')

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

def update_contacts_safe():
    """Sadece TEK eşleşmesi olan kayıtları güncelle"""
    
    with engine.begin() as conn:
        print("🔄 120/320 carilerinden contact_id dolduruluyor...\n")
        
        # 1. 120/320 carilerinden doldur (tek cari olanlar)
        result = conn.execute(text("""
            UPDATE transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            SET tl.contact_id = (
                SELECT tl2.contact_id
                FROM transaction_lines tl2
                JOIN accounts a2 ON tl2.account_id = a2.id
                WHERE tl2.transaction_id = tl.transaction_id
                  AND (a2.code LIKE '120%' OR a2.code LIKE '320%')
                  AND tl2.contact_id IS NOT NULL
                LIMIT 1
            )
            WHERE (a.code LIKE '740%' OR a.code LIKE '770%')
              AND tl.contact_id IS NULL
              AND (
                  SELECT COUNT(DISTINCT tl2.contact_id)
                  FROM transaction_lines tl2
                  JOIN accounts a2 ON tl2.account_id = a2.id
                  WHERE tl2.transaction_id = tl.transaction_id
                    AND (a2.code LIKE '120%' OR a2.code LIKE '320%')
                    AND tl2.contact_id IS NOT NULL
              ) = 1
        """))
        
        updated_120_320 = result.rowcount
        print(f"✅ 120/320 carilerinden güncellenen: {updated_120_320}")
        
        # 2. 335 personelinden doldur (tek personel olanlar)
        result = conn.execute(text("""
            UPDATE transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            SET tl.contact_id = (
                SELECT p.contact_id
                FROM transaction_lines tl3
                JOIN accounts a3 ON tl3.account_id = a3.id
                JOIN personnel p ON a3.id = p.account_id
                WHERE tl3.transaction_id = tl.transaction_id
                  AND a3.code LIKE '335%'
                  AND p.contact_id IS NOT NULL
                LIMIT 1
            )
            WHERE (a.code LIKE '740%' OR a.code LIKE '770%')
              AND tl.contact_id IS NULL
              AND (
                  SELECT COUNT(DISTINCT p.contact_id)
                  FROM transaction_lines tl3
                  JOIN accounts a3 ON tl3.account_id = a3.id
                  JOIN personnel p ON a3.id = p.account_id
                  WHERE tl3.transaction_id = tl.transaction_id
                    AND a3.code LIKE '335%'
                    AND p.contact_id IS NOT NULL
              ) = 1
        """))
        
        updated_335 = result.rowcount
        print(f"✅ 335 personelinden güncellenen: {updated_335}")
        
        print(f"\n📊 TOPLAM GÜNCELLEME: {updated_120_320 + updated_335}")
        print("✅ İşlem tamamlandı!")
        
        # Kontrol - hala boş olanlar
        result = conn.execute(text("""
            SELECT COUNT(*) as still_empty
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE (a.code LIKE '740%' OR a.code LIKE '770%')
              AND tl.contact_id IS NULL
        """))
        
        still_empty = result.fetchone().still_empty
        print(f"\n📌 Hala boş kalan: {still_empty}")
        print("   (Bunlar riskli veya hiç eşleşmesi olmayan kayıtlar)")

if __name__ == "__main__":
    confirm = input("\n⚠️  740 ve 770 hesap kodlarındaki ~11,000 satır güncellenecek. Devam? (evet/hayır): ")
    if confirm.lower() in ['evet', 'e', 'yes', 'y']:
        update_contacts_safe()
    else:
        print("❌ İşlem iptal edildi.")
