"""
Takvimli puantaj tablolarını kontrol et
"""
import pymysql
from datetime import datetime

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='muhasebe_sistem',
    charset='utf8mb4'
)

cursor = conn.cursor()

print("=" * 80)
print("TAKVİMLİ PUANTAJ SİSTEMİ - TABLO KONTROLÜ")
print("=" * 80)

# 1. personnel_daily_attendance
cursor.execute("SHOW COLUMNS FROM personnel_daily_attendance")
columns = cursor.fetchall()
print(f"\n1️⃣  personnel_daily_attendance ({len(columns)} kolon)")
print("   Günlük detaylı puantaj kayıtları")
print("   Öne çıkan kolonlar:")
print("   - attendance_date: Puantaj tarihi")
print("   - calisma_durumu: CALISTI, IZINLI, RAPORLU, GELMEDI, TATIL")
print("   - normal_saat, fazla_mesai_saat, tatil_mesai_saat")
print("   - yillik_izin, ucretsiz_izin, rapor (gün)")
print("   - gunluk_kazanc, fm_kazanc, tatil_kazanc")

# 2. personnel_leave_balance
cursor.execute("SHOW COLUMNS FROM personnel_leave_balance")
columns = cursor.fetchall()
print(f"\n2️⃣  personnel_leave_balance ({len(columns)} kolon)")
print("   Yıllık izin bakiyeleri")
print("   Öne çıkan kolonlar:")
print("   - annual_leave_entitlement: Yıllık izin hakkı")
print("   - annual_leave_used: Kullanılan izin")
print("   - annual_leave_balance: Kalan izin")

# 3. shift_definitions
cursor.execute("SELECT * FROM shift_definitions")
shifts = cursor.fetchall()
print(f"\n3️⃣  shift_definitions ({len(shifts)} vardiya)")
print("   Vardiya tanımları:")
for shift in shifts:
    print(f"   - {shift[1]}: {shift[2]} ({shift[3]} - {shift[4]})")

# 4. calendar_holidays
cursor.execute("SELECT COUNT(*) FROM calendar_holidays WHERE year = 2025")
holiday_count = cursor.fetchone()[0]
print(f"\n4️⃣  calendar_holidays ({holiday_count} tatil - 2025)")
print("   2025 Resmi tatiller:")
cursor.execute("SELECT holiday_date, name FROM calendar_holidays WHERE year = 2025 ORDER BY holiday_date LIMIT 5")
for holiday in cursor.fetchall():
    print(f"   - {holiday[0]}: {holiday[1]}")
print("   ...")

# 5. Views
print(f"\n5️⃣  View'ler")
cursor.execute("""
    SELECT TABLE_NAME 
    FROM information_schema.VIEWS 
    WHERE TABLE_SCHEMA = 'muhasebe_sistem' 
    AND TABLE_NAME LIKE 'v_%attendance%'
    OR TABLE_NAME LIKE 'v_%calendar%'
    ORDER BY TABLE_NAME
""")
views = cursor.fetchall()
for view in views:
    print(f"   - {view[0]}")

print("\n" + "=" * 80)
print("✅ TAKVİMLİ PUANTAJ SİSTEMİ BAŞARIYLA KURULDU!")
print("=" * 80)

print("\n📝 SONRAKİ ADIMLAR:")
print("   1. API endpoint oluştur (personnel_daily_attendance için)")
print("   2. Excel import fonksiyonu yaz (Luca formatı)")
print("   3. Frontend takvim bileşeni geliştir")
print("   4. Aylık özet raporları hazırla")

cursor.close()
conn.close()
