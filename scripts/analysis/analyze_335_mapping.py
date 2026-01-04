"""ESKİ 335 hesaplardan YENİ 335.{TCKN} hesaplara eşleştirme analizi"""
from app.core.database import SessionLocal
from sqlalchemy import text
import re

db = SessionLocal()

# ESKİ hesapların adlarından TC kimlik çıkar
eski_accounts = db.execute(text("""
    SELECT id, code, name
    FROM accounts
    WHERE code LIKE '335.%' 
    AND (name LIKE '%ESKİ%' OR code REGEXP '^335\.[0-9]{5}$')
    ORDER BY code
    LIMIT 50
""")).fetchall()

print("=" * 80)
print("ESKİ 335 HESAPLAR - TC KİMLİK NUMARASI EŞLEŞTİRME ANALİZİ")
print("=" * 80)

# TC kimlik regex (11 haneli sayı)
tc_pattern = re.compile(r'\b\d{11}\b')

matched_count = 0
unmatched_count = 0

for acc in eski_accounts[:20]:  # İlk 20'yi analiz et
    acc_id, code, name = acc
    
    # TC kimlik numarasını bul
    tc_match = tc_pattern.search(name)
    
    if tc_match:
        tckn = tc_match.group()
        
        # YENİ hesabı bul (335.{TCKN})
        new_account = db.execute(text("""
            SELECT id, code, name 
            FROM accounts 
            WHERE code = :new_code
        """), {"new_code": f"335.{tckn}"}).fetchone()
        
        if new_account:
            matched_count += 1
            print(f"✅ ESKİ: {code:15} -> YENİ: {new_account[1]:20} | {name[:50]}")
        else:
            unmatched_count += 1
            print(f"❌ ESKİ: {code:15} -> YENİ HESAP YOK         | TC: {tckn} | {name[:50]}")
    else:
        unmatched_count += 1
        print(f"⚠️  ESKİ: {code:15} -> TC BULUNAMADI          | {name[:50]}")

print("\n" + "=" * 80)
print(f"Eşleşen: {matched_count}")
print(f"Eşleşmeyen: {unmatched_count}")
print("=" * 80)

# Transaction_lines'da ESKİ hesaplara ait kayıtları say
tx_count = db.execute(text("""
    SELECT COUNT(*) as kayit_sayisi
    FROM transaction_lines tl
    JOIN accounts a ON a.id = tl.account_id
    WHERE a.code LIKE '335.%' 
    AND (a.name LIKE '%ESKİ%' OR a.code REGEXP '^335\.[0-9]{5}$')
""")).fetchone()

print(f"\n📊 ESKİ hesaplarda {tx_count[0]} adet transaction_lines kaydı var")
print("=" * 80)

# Örnek bir eşleştirme için detay
if matched_count > 0:
    sample = db.execute(text("""
        SELECT 
            old_acc.id as eski_id,
            old_acc.code as eski_code,
            old_acc.name as eski_name,
            new_acc.id as yeni_id,
            new_acc.code as yeni_code,
            new_acc.name as yeni_name,
            COUNT(tl.id) as kayit_sayisi
        FROM accounts old_acc
        JOIN accounts new_acc ON new_acc.code = CONCAT('335.', SUBSTRING_INDEX(old_acc.name, ' ', -1))
        LEFT JOIN transaction_lines tl ON tl.account_id = old_acc.id
        WHERE old_acc.code LIKE '335.%'
        AND old_acc.name LIKE '%ESKİ%'
        AND new_acc.code LIKE '335.%'
        AND new_acc.code REGEXP '^335\.[0-9]{11}$'
        GROUP BY old_acc.id, new_acc.id
        LIMIT 5
    """)).fetchall()
    
    if sample:
        print("\n📋 ÖRNEK EŞLEŞTİRMELER VE TRANSAKSİYON SAYILARI:")
        for row in sample:
            print(f"\nESKİ: {row[1]} (ID: {row[0]})")
            print(f"  -> {row[2][:60]}")
            print(f"YENİ:  {row[4]} (ID: {row[3]})")
            print(f"  -> {row[5][:60]}")
            print(f"📊 Transaction sayısı: {row[6]}")

db.close()
