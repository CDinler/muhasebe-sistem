"""FM kolonlarını ekle - basit versiyon"""
from sqlalchemy import text
from app.core.database import engine

def add_fm_columns():
    with engine.begin() as conn:
        print("FM kolonları ekleniyor...")
        
        for i in range(1, 32):
            try:
                sql = text(f"ALTER TABLE personnel_puantaj_grid ADD COLUMN fm_gun_{i} DECIMAL(4,1) DEFAULT NULL")
                conn.execute(sql)
                print(f"  fm_gun_{i} ✓")
            except Exception as e:
                if "Duplicate column" in str(e):
                    print(f"  fm_gun_{i} zaten var")
                else:
                    print(f"  fm_gun_{i} HATA: {e}")
        
        # Toplam FM kolonu
        try:
            sql = text("ALTER TABLE personnel_puantaj_grid ADD COLUMN toplam_fm DECIMAL(5,1) DEFAULT 0")
            conn.execute(sql)
            print("  toplam_fm ✓")
        except Exception as e:
            if "Duplicate column" in str(e):
                print("  toplam_fm zaten var")
            else:
                print(f"  toplam_fm HATA: {e}")
        
        print("\n✅ FM kolonları eklendi!")

if __name__ == '__main__':
    add_fm_columns()
