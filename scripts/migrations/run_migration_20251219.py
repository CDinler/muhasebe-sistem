"""
Migration çalıştır - dogum_tarihi, meslek_kodu, sgk_no ekle
"""
from app.core.database import engine
from sqlalchemy import text

print("=" * 80)
print("MIGRATION: Doğum tarihi, meslek kodu ve SGK no ekleniyor...")
print("=" * 80)

with engine.connect() as conn:
    try:
        # Sütunları ekle
        conn.execute(text("""
            ALTER TABLE monthly_personnel_records
            ADD COLUMN dogum_tarihi DATE NULL COMMENT 'Doğum tarihi' AFTER isten_cikis_tarihi,
            ADD COLUMN meslek_kodu VARCHAR(20) NULL COMMENT 'Luca meslek kodu' AFTER meslek_adi,
            ADD COLUMN sgk_no VARCHAR(50) NULL COMMENT 'SSK/SGK numarası' AFTER meslek_kodu
        """))
        print("✅ Sütunlar eklendi")
        
        # Index ekle
        conn.execute(text("""
            CREATE INDEX idx_monthly_personnel_dogum_tarihi 
            ON monthly_personnel_records(dogum_tarihi)
        """))
        print("✅ dogum_tarihi index eklendi")
        
        conn.execute(text("""
            CREATE INDEX idx_monthly_personnel_meslek_kodu
            ON monthly_personnel_records(meslek_kodu)
        """))
        print("✅ meslek_kodu index eklendi")
        
        conn.commit()
        print("\n" + "=" * 80)
        print("✅ Migration başarıyla tamamlandı")
        print("=" * 80)
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Hata: {e}")
        import traceback
        traceback.print_exc()
