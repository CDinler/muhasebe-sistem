"""
2025-01 dönemindeki kayıtları kontrol et
"""
from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT donem, 
               COUNT(*) as kayit_sayisi, 
               COUNT(DISTINCT personnel_id) as personel_sayisi,
               COUNT(DISTINCT bolum_adi) as bolum_sayisi
        FROM monthly_personnel_records
        WHERE donem = '2025-01'
        GROUP BY donem
    """))
    
    print("=" * 80)
    print("2025-01 DÖNEMİ KONTROL")
    print("=" * 80)
    
    rows = result.fetchall()
    
    if not rows:
        print("❌ 2025-01 döneminde hiç kayıt yok!")
    else:
        for row in rows:
            print(f"Dönem: {row[0]}")
            print(f"Kayıt sayısı: {row[1]}")
            print(f"Personel sayısı: {row[2]}")
            print(f"Bölüm sayısı: {row[3]}")
    
    # Tüm dönemleri göster
    result2 = conn.execute(text("""
        SELECT donem, COUNT(*) as kayit_sayisi
        FROM monthly_personnel_records
        GROUP BY donem
        ORDER BY donem DESC
    """))
    
    print("\n" + "=" * 80)
    print("TÜM DÖNEMLER")
    print("=" * 80)
    
    for row in result2:
        print(f"  {row[0]}: {row[1]} kayıt")
