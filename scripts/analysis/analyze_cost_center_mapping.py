"""
Luca bölüm isimleri ile cost_centers eşleştirme analizi
"""
import pymysql

def analyze_mapping():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='muhasebe_sistem',
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    # 1. Luca bölüm isimlerini listele
    print("=" * 80)
    print("LUCA BÖLÜM İSİMLERİ (monthly_personnel_records)")
    print("=" * 80)
    cursor.execute("""
        SELECT DISTINCT bolum_adi, COUNT(*) as kayit_sayisi
        FROM monthly_personnel_records
        GROUP BY bolum_adi
        ORDER BY kayit_sayisi DESC
    """)
    
    luca_bolumler = []
    for row in cursor:
        bolum = row[0]
        count = row[1]
        luca_bolumler.append(bolum)
        print(f"{bolum:60} → {count:3} kayıt")
    
    # 2. Sistemdeki cost_centers'ı listele
    print("\n" + "=" * 80)
    print("SİSTEMDEKİ MALİYET MERKEZLERİ (cost_centers)")
    print("=" * 80)
    cursor.execute("""
        SELECT id, code, name, is_active
        FROM cost_centers
        ORDER BY code
    """)
    
    cost_centers = []
    for row in cursor:
        id, code, name, is_active = row
        cost_centers.append({'id': id, 'code': code, 'name': name, 'is_active': is_active})
        active = "✓" if is_active else "✗"
        print(f"[{active}] {code:10} | {name}")
    
    # 3. Eşleşme önerileri
    print("\n" + "=" * 80)
    print("EŞLEŞTİRME ÖNERİLERİ")
    print("=" * 80)
    
    for bolum in luca_bolumler:
        if not bolum:
            continue
            
        # Bölüm adından kod çıkar (başta sayı varsa)
        parts = bolum.split('-')
        if len(parts) > 0 and parts[0].strip().isdigit():
            luca_code = parts[0].strip()
            
            # Eşleşen cost_center var mı?
            matches = [cc for cc in cost_centers if cc['code'] == luca_code]
            
            if matches:
                cc = matches[0]
                print(f"✓ {bolum:60} → [{cc['code']}] {cc['name']}")
            else:
                print(f"✗ {bolum:60} → Kod: {luca_code} (EŞLEŞME YOK!)")
        else:
            # Kod yok, isim bazlı eşleşme dene
            print(f"? {bolum:60} → Kod yok, manuel eşleştirme gerekli")
    
    # 4. Özet
    print("\n" + "=" * 80)
    print("ÖZET")
    print("=" * 80)
    print(f"Toplam Luca bölüm: {len(luca_bolumler)}")
    print(f"Toplam cost_center: {len(cost_centers)}")
    print(f"Aktif cost_center: {len([cc for cc in cost_centers if cc['is_active']])}")
    
    conn.close()

if __name__ == "__main__":
    analyze_mapping()
