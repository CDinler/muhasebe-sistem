"""ESKİ 335 hesapları YENİ 335.{TCKN} hesaplara migration"""
from app.core.database import SessionLocal
from sqlalchemy import text
import re

db = SessionLocal()

print("=" * 80)
print("335 HESAP MİGRATİON - ESKİ -> YENİ (335.{TCKN})")
print("=" * 80)

try:
    # ADIM 1: ESKİ -> YENİ eşleştirmelerini bul
    print("\n[1/5] ESKİ -> YENİ hesap eşleştirmeleri bulunuyor...")
    
    mappings = db.execute(text("""
        SELECT 
            old_acc.id as eski_id,
            old_acc.code as eski_code,
            new_acc.id as yeni_id,
            new_acc.code as yeni_code,
            COUNT(tl.id) as transaction_count
        FROM accounts old_acc
        JOIN accounts new_acc ON new_acc.code = CONCAT('335.', SUBSTRING_INDEX(old_acc.name, ' ', -1))
        LEFT JOIN transaction_lines tl ON tl.account_id = old_acc.id
        WHERE old_acc.code LIKE '335.%'
        AND (old_acc.name LIKE '%ESKİ%' OR old_acc.code REGEXP '^335\\.[0-9]{5}$')
        AND new_acc.code LIKE '335.%'
        AND new_acc.code REGEXP '^335\\.[0-9]{11}$'
        GROUP BY old_acc.id, new_acc.id
        HAVING COUNT(tl.id) > 0
        ORDER BY old_acc.code
    """)).fetchall()
    
    print(f"   ✅ {len(mappings)} adet ESKİ hesapta transaction kaydı bulundu")
    
    if not mappings:
        print("\n⚠️  Migrate edilecek kayıt yok!")
        db.close()
        exit(0)
    
    # Toplam transaction sayısını göster
    total_tx = sum(m[4] for m in mappings)
    print(f"   📊 Toplam {total_tx} transaction_lines kaydı migrate edilecek")
    
    # ADIM 2: Transaction_lines güncellemeleri
    print("\n[2/5] Transaction_lines kayıtları güncelleniyor...")
    
    updated_count = 0
    for eski_id, eski_code, yeni_id, yeni_code, tx_count in mappings:
        if tx_count > 0:
            # Transaction_lines'daki account_id'yi güncelle
            result = db.execute(text("""
                UPDATE transaction_lines
                SET account_id = :yeni_id
                WHERE account_id = :eski_id
            """), {"yeni_id": yeni_id, "eski_id": eski_id})
            
            updated_count += result.rowcount
            print(f"   ✅ {eski_code:15} -> {yeni_code:20} | {result.rowcount} kayıt")
    
    print(f"\n   📊 Toplam {updated_count} kayıt güncellendi")
    
    # ADIM 3: Personnel account_id güncellemeleri (eğer varsa)
    print("\n[3/5] Personnel tablosundaki ESKİ hesap referansları kontrol ediliyor...")
    
    pers_check = db.execute(text("""
        SELECT COUNT(*)
        FROM personnel p
        JOIN accounts a ON a.id = p.account_id
        WHERE a.code LIKE '335.%'
        AND (a.name LIKE '%ESKİ%' OR a.code REGEXP '^335\\.[0-9]{5}$')
    """)).scalar()
    
    if pers_check > 0:
        print(f"   ⚠️  {pers_check} personelde ESKİ hesap referansı var, güncelleniyor...")
        
        # Personnel'deki ESKİ account_id'leri YENİ'lere güncelle
        for eski_id, eski_code, yeni_id, yeni_code, _ in mappings:
            db.execute(text("""
                UPDATE personnel
                SET account_id = :yeni_id
                WHERE account_id = :eski_id
            """), {"yeni_id": yeni_id, "eski_id": eski_id})
        
        print(f"   ✅ Personnel güncellemeleri tamamlandı")
    else:
        print(f"   ✅ Personnel'de ESKİ hesap referansı yok")
    
    # ADIM 4: ESKİ hesapları SİL
    print("\n[4/5] ESKİ 335 hesapları siliniyor...")
    
    # Önce tüm ESKİ hesapları listele
    all_eski = db.execute(text("""
        SELECT id, code, name
        FROM accounts
        WHERE code LIKE '335.%'
        AND (name LIKE '%ESKİ%' OR code REGEXP '^335\\.[0-9]{5}$')
        ORDER BY code
    """)).fetchall()
    
    print(f"   📊 Silinecek ESKİ hesap sayısı: {len(all_eski)}")
    
    # ESKİ hesapları sil
    delete_result = db.execute(text("""
        DELETE FROM accounts
        WHERE code LIKE '335.%'
        AND (name LIKE '%ESKİ%' OR code REGEXP '^335\\.[0-9]{5}$')
    """))
    
    print(f"   ✅ {delete_result.rowcount} ESKİ hesap silindi")
    
    # ADIM 5: Doğrulama
    print("\n[5/5] Migration doğrulanıyor...")
    
    # Kalan 335 hesap sayısı
    remaining = db.execute(text("""
        SELECT COUNT(*)
        FROM accounts
        WHERE code LIKE '335.%'
    """)).scalar()
    
    print(f"   📊 Kalan 335 hesap sayısı: {remaining}")
    
    # YENİ hesaplarda transaction sayısı
    new_tx = db.execute(text("""
        SELECT COUNT(*)
        FROM transaction_lines tl
        JOIN accounts a ON a.id = tl.account_id
        WHERE a.code LIKE '335.%'
        AND a.code REGEXP '^335\\.[0-9]{11}$'
    """)).scalar()
    
    print(f"   📊 YENİ hesaplarda transaction sayısı: {new_tx}")
    
    # ESKİ hesap kontrolü
    old_check = db.execute(text("""
        SELECT COUNT(*)
        FROM accounts
        WHERE code LIKE '335.%'
        AND (name LIKE '%ESKİ%' OR code REGEXP '^335\\.[0-9]{5}$')
    """)).scalar()
    
    if old_check == 0:
        print(f"   ✅ ESKİ hesap kalmadı!")
    else:
        print(f"   ⚠️  UYARI: {old_check} ESKİ hesap hala mevcut!")
    
    # COMMIT
    print("\n" + "=" * 80)
    confirm = input("Migration tamamlandı. COMMIT edilsin mi? (evet/hayır): ")
    
    if confirm.lower() in ['evet', 'e', 'yes', 'y']:
        db.commit()
        print("✅ MİGRATİON BAŞARILI! Değişiklikler kaydedildi.")
    else:
        db.rollback()
        print("❌ ROLLBACK yapıldı. Değişiklikler geri alındı.")
    
except Exception as e:
    print(f"\n❌ HATA: {e}")
    db.rollback()
    raise
finally:
    db.close()

print("=" * 80)
