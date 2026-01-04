"""
Migration durumunu kontrol et - dogum_tarihi, meslek_kodu, sgk_no sütunları var mı?
"""
from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("""
        DESCRIBE monthly_personnel_records
    """))
    
    columns = [row[0] for row in result]
    
    print("=" * 80)
    print("MONTHLY_PERSONNEL_RECORDS SÜTUNLARI")
    print("=" * 80)
    
    for col in columns:
        print(f"  - {col}")
    
    print("\n" + "=" * 80)
    print("YENİ SÜTUN KONTROLÜ")
    print("=" * 80)
    
    new_columns = ['dogum_tarihi', 'meslek_kodu', 'sgk_no']
    for col in new_columns:
        exists = col in columns
        symbol = "✅" if exists else "❌"
        print(f"{symbol} {col}")
    
    if all(col in columns for col in new_columns):
        print("\n✅ Tüm yeni sütunlar mevcut - Migration çalıştırılmış")
    else:
        print("\n❌ Yeni sütunlar eksik - Migration çalıştırılmalı:")
        print("   database/migrations/20251219_add_dogum_tarihi_to_monthly_personnel.sql")
