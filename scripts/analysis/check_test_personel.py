"""Test personel ekleme ve kontrol"""
from sqlalchemy import text
from app.core.database import engine

def check_and_create_test():
    with engine.connect() as conn:
        # Önce kontrol et
        result = conn.execute(text("SELECT sicil_no, adi_soyadi, donem FROM personnel_puantaj_grid WHERE donem = '2025-01'"))
        rows = result.fetchall()
        
        print(f"2025-01 döneminde {len(rows)} kayıt var:")
        for row in rows:
            print(f"  {row[0]} - {row[1]} ({row[2]})")
        
        if len(rows) == 0:
            print("\nTest personel ekleniyor...")
            
            # Önce personnel tablosundan bir ID bul veya ekle
            pers_result = conn.execute(text("SELECT id, sicil_no, adi, soyadi FROM personnel LIMIT 1"))
            pers = pers_result.fetchone()
            
            if pers:
                print(f"Personel bulundu: {pers[1]} - {pers[2]} {pers[3]}")
                
                # Test kaydı ekle
                insert_sql = text("""
                    INSERT INTO personnel_puantaj_grid 
                    (personnel_id, donem, yil, ay, sicil_no, adi_soyadi,
                     gun_1, fm_gun_1, gun_2, fm_gun_2, gun_8, fm_gun_8)
                    VALUES 
                    (:pid, '2025-01', 2025, 1, :sicil, :adi_soyadi,
                     'N', 2.0, 'N', 1.5, 'N', 3.0)
                """)
                
                conn.execute(insert_sql, {
                    'pid': pers[0],
                    'sicil': pers[1],
                    'adi_soyadi': f"{pers[2]} {pers[3]}"
                })
                conn.commit()
                
                print("✅ Test personel eklendi!")
            else:
                print("⚠️ Personnel tablosunda kayıt yok!")
        else:
            print("\n✅ Test personel zaten mevcut")

if __name__ == '__main__':
    check_and_create_test()
