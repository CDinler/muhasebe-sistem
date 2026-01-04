"""
Personnel Contract Cost Center Updater
Excel dosyasından personel-cost center eşleştirmelerini okur ve personnel_contracts tablosunu günceller
"""
import pandas as pd
import mysql.connector
from datetime import datetime

# Excel dosyasını oku
print("Excel dosyası okunuyor...")
df = pd.read_excel(r'C:\Projects\muhasebe-sistem\personel_costcenters.xlsx')

print(f"Toplam kayıt: {len(df)}")
print(f"Unique cost centers: {sorted(df['cost center'].unique())}")

# Database bağlantısı
print("\nDatabase'e bağlanılıyor...")
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',  # Password yok
    database='muhasebe_sistem',
    charset='utf8mb4'
)
cursor = conn.cursor(dictionary=True)

# Cost centers tablosunu oku
print("\nCost centers tablosu okunuyor...")
cursor.execute("SELECT id, code, name FROM cost_centers ORDER BY name")
cost_centers = cursor.fetchall()

print("\nDatabase'deki cost centers:")
for cc in cost_centers:
    print(f"  ID: {cc['id']}, Code: {cc['code']}, Name: {cc['name']}")

# Cost center name -> ID mapping oluştur
cost_center_map = {cc['name']: cc['id'] for cc in cost_centers}

print("\n\nEksik cost center'ları ekle:")
unique_cc_names = df['cost center'].unique()
new_cost_centers = []

for cc_name in unique_cc_names:
    if cc_name not in cost_center_map:
        # Yeni cost center ekle
        code = cc_name.replace(' ', '_').upper()[:20]
        cursor.execute(
            "INSERT INTO cost_centers (code, name, is_active) VALUES (%s, %s, 1)",
            (code, cc_name)
        )
        new_id = cursor.lastrowid
        cost_center_map[cc_name] = new_id
        new_cost_centers.append((new_id, code, cc_name))
        print(f"  Eklendi: ID={new_id}, Code={code}, Name={cc_name}")

if new_cost_centers:
    conn.commit()
    print(f"\n{len(new_cost_centers)} yeni cost center eklendi.")
else:
    print("\nTüm cost center'lar zaten mevcut.")

# Personel bilgilerini oku
print("\n\nPersonel bilgileri okunuyor...")
cursor.execute("""
    SELECT p.id, p.tckn, p.first_name, p.last_name, p.start_date
    FROM personnel p
    ORDER BY p.tckn
""")
personnel_list = cursor.fetchall()
personnel_map = {str(p['tckn']): p for p in personnel_list if p['tckn']}

print(f"Database'de {len(personnel_map)} personel bulundu (TCKN ile)")

# Personnel contracts tablosunu kontrol et
print("\n\nPersonnel contracts tablosu kontrol ediliyor...")
cursor.execute("""
    SELECT COUNT(*) as total FROM personnel_contracts
""")
contract_count = cursor.fetchone()['total']
print(f"Mevcut contract sayısı: {contract_count}")

# Her kayıt için işlem yap
print("\n\nPersonel contract kayıtları güncelleniyor...")
updates = 0
inserts = 0
skipped = 0
errors = []

for idx, row in df.iterrows():
    tckn = str(row['tckn'])
    cost_center_name = row['cost center']
    giris_tarihi = row['giris tarihi'].date() if pd.notna(row['giris tarihi']) else None
    
    if not giris_tarihi:
        skipped += 1
        errors.append(f"TCKN {tckn}: Giriş tarihi yok")
        continue
    
    # Personel bul
    if tckn not in personnel_map:
        skipped += 1
        errors.append(f"TCKN {tckn}: Personel bulunamadı")
        continue
    
    personnel = personnel_map[tckn]
    personnel_id = personnel['id']
    
    # Cost center ID bul
    cost_center_id = cost_center_map.get(cost_center_name)
    if not cost_center_id:
        skipped += 1
        errors.append(f"TCKN {tckn}: Cost center '{cost_center_name}' bulunamadı")
        continue
    
    # Bu personelin bu tarihte bir contract'ı var mı kontrol et
    cursor.execute("""
        SELECT id, cost_center_id 
        FROM personnel_contracts 
        WHERE personnel_id = %s AND ise_giris_tarihi = %s
    """, (personnel_id, giris_tarihi))
    
    existing_contract = cursor.fetchone()
    
    if existing_contract:
        # Mevcut contract'ı güncelle
        if existing_contract['cost_center_id'] != cost_center_id:
            cursor.execute("""
                UPDATE personnel_contracts 
                SET cost_center_id = %s, cost_center_name = %s
                WHERE id = %s
            """, (cost_center_id, cost_center_name, existing_contract['id']))
            updates += 1
            if idx < 10 or idx % 50 == 0:
                print(f"  [{idx+1}/{len(df)}] Güncellendi: {personnel['first_name']} {personnel['last_name']} (TCKN: {tckn}) -> {cost_center_name}")
    else:
        # Yeni contract oluştur (temel bilgilerle)
        cursor.execute("""
            INSERT INTO personnel_contracts 
            (personnel_id, ise_giris_tarihi, cost_center_id, cost_center_name, 
             ucret_nevi, is_active)
            VALUES (%s, %s, %s, %s, 'AYLIK', 1)
        """, (personnel_id, giris_tarihi, cost_center_id, cost_center_name))
        inserts += 1
        if idx < 10 or idx % 50 == 0:
            print(f"  [{idx+1}/{len(df)}] Eklendi: {personnel['first_name']} {personnel['last_name']} (TCKN: {tckn}) -> {cost_center_name}, Tarih: {giris_tarihi}")

# Değişiklikleri kaydet
conn.commit()

print("\n" + "="*80)
print("ÖZET:")
print(f"  Toplam işlenen kayıt: {len(df)}")
print(f"  Güncellenen contract: {updates}")
print(f"  Yeni eklenen contract: {inserts}")
print(f"  Atlanan kayıt: {skipped}")
print("="*80)

if errors:
    print(f"\nHATALAR ({len(errors)}):")
    for err in errors[:20]:  # İlk 20 hatayı göster
        print(f"  - {err}")
    if len(errors) > 20:
        print(f"  ... ve {len(errors) - 20} hata daha")

# Verification - her cost center'da kaç personel var?
print("\n\nCOST CENTER DAĞILIMI:")
cursor.execute("""
    SELECT 
        cc.name,
        COUNT(DISTINCT pc.personnel_id) as personel_sayisi,
        COUNT(pc.id) as contract_sayisi
    FROM cost_centers cc
    LEFT JOIN personnel_contracts pc ON cc.id = pc.cost_center_id AND pc.is_active = 1
    GROUP BY cc.id, cc.name
    ORDER BY personel_sayisi DESC
""")
distribution = cursor.fetchall()

for row in distribution:
    if row['personel_sayisi'] > 0:
        print(f"  {row['name']}: {row['personel_sayisi']} personel, {row['contract_sayisi']} contract")

cursor.close()
conn.close()

print("\n✅ İşlem tamamlandı!")
