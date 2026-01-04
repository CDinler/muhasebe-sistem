"""Test personeli ekle"""
from sqlalchemy import text
from app.core.database import engine

def add_test_record():
    with engine.begin() as conn:
        # Önce personnel tablosundan bir ID bul
        result = conn.execute(text("SELECT id FROM personnel LIMIT 1"))
        pers = result.fetchone()
        
        if not pers:
            print("⚠️ Personnel tablosunda kayıt yok!")
            return
        
        personnel_id = pers[0]
        print(f"Personnel ID: {personnel_id}")
        
        # Test kaydı ekle
        sql = text("""
            INSERT INTO personnel_puantaj_grid 
            (personnel_id, donem, yil, ay,
             gun_1, fm_gun_1, gun_2, fm_gun_2, gun_3, gun_4, gun_5,
             gun_6, gun_7, gun_8, fm_gun_8, gun_9, fm_gun_9, gun_10, fm_gun_10,
             gun_11, gun_12, gun_13, fm_gun_13, gun_14, gun_15,
             gun_16, gun_17, gun_18, gun_19,
             gun_20, fm_gun_20, gun_21, gun_22, fm_gun_22,
             gun_23, gun_24, gun_25, gun_26, gun_27, gun_28, gun_29, gun_30, gun_31)
            VALUES 
            (:pid, '2025-01', 2025, 1,
             'N', 2.0, 'N', 1.5, 'N', 'H', 'H',
             'N', 'N', 'N', 3.0, 'N', 2.5, 'N', 4.0,
             'H', 'H', 'N', 1.0, 'N', 'N',
             'İ', 'İ', 'H', 'H',
             'N', 2.0, 'N', 'N', 1.5,
             'N', 'N', 'H', 'H', 'N', 'N', 'N', 'N', 'N')
            ON DUPLICATE KEY UPDATE
             gun_1='N', fm_gun_1=2.0, gun_2='N', fm_gun_2=1.5
        """)
        
        conn.execute(sql, {'pid': personnel_id})
        print(f"✅ Test personel eklendi (personnel_id={personnel_id}, donem=2025-01)")
        
        # Kontrol et
        check = conn.execute(text("SELECT id, personnel_id, donem, gun_1, fm_gun_1 FROM personnel_puantaj_grid WHERE donem='2025-01'"))
        row = check.fetchone()
        print(f"Kontrol: ID={row[0]}, PersonnelID={row[1]}, Dönem={row[2]}, Gun1={row[3]}, FM1={row[4]}")

if __name__ == '__main__':
    add_test_record()
