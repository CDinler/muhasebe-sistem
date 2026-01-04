"""
personnel_attendance vs personnel_daily_attendance karşılaştırması
"""
import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='muhasebe_sistem',
    charset='utf8mb4'
)

cursor = conn.cursor()

print("=" * 100)
print("PERSONNEL_ATTENDANCE vs PERSONNEL_DAILY_ATTENDANCE - KARŞILAŞTIRMA")
print("=" * 100)

# Tabloları kontrol et
cursor.execute("SHOW TABLES LIKE '%attendance%'")
tables = cursor.fetchall()
print("\nMevcut Attendance Tabloları:")
for table in tables:
    print(f"  - {table[0]}")

print("\n" + "=" * 100)
print("1. PERSONNEL_ATTENDANCE (ESKİ - Basit Yapı)")
print("=" * 100)

cursor.execute("SHOW TABLES LIKE 'personnel_attendance'")
if cursor.fetchone():
    cursor.execute("SHOW COLUMNS FROM personnel_attendance")
    columns = cursor.fetchall()
    print(f"\nKolon Sayısı: {len(columns)}")
    print("\nKolonlar:")
    for col in columns:
        print(f"  - {col[0]:25} {col[1]:20} {col[2]:10} {col[3]}")
    
    cursor.execute("SELECT COUNT(*) FROM personnel_attendance")
    count = cursor.fetchone()[0]
    print(f"\nKayıt Sayısı: {count}")
else:
    print("\n⚠️  TABLO BULUNAMADI - Henüz oluşturulmamış")

print("\n" + "=" * 100)
print("2. PERSONNEL_DAILY_ATTENDANCE (YENİ - Takvimli Sistem)")
print("=" * 100)

cursor.execute("SHOW TABLES LIKE 'personnel_daily_attendance'")
if cursor.fetchone():
    cursor.execute("SHOW COLUMNS FROM personnel_daily_attendance")
    columns = cursor.fetchall()
    print(f"\nKolon Sayısı: {len(columns)}")
    print("\nKolonlar:")
    for col in columns:
        print(f"  - {col[0]:25} {col[1]:30} {col[2]:10}")
    
    cursor.execute("SELECT COUNT(*) FROM personnel_daily_attendance")
    count = cursor.fetchone()[0]
    print(f"\nKayıt Sayısı: {count}")
else:
    print("\n⚠️  TABLO BULUNAMADI")

print("\n" + "=" * 100)
print("TEMEL FARKLAR")
print("=" * 100)

print("""
┌─────────────────────────────┬──────────────────────────┬────────────────────────────────┐
│ ÖZELLİK                     │ personnel_attendance     │ personnel_daily_attendance     │
├─────────────────────────────┼──────────────────────────┼────────────────────────────────┤
│ Amaç                        │ Basit giriş-çıkış        │ Detaylı takvimli puantaj       │
│ Kolon Sayısı                │ 9 kolon                  │ 39 kolon                       │
│ Tarih Bilgisi               │ Sadece tarih             │ Tarih + Gün adı + Tip          │
│ Çalışma Durumu              │ Basit (PRESENT, ABSENT)  │ Detaylı ENUM (6 durum)         │
│ Saat Bilgisi                │ Toplam saat              │ Normal+FM+Tatil+Gece ayrı      │
│ İzin Yönetimi               │ Yok                      │ 8 farklı izin türü             │
│ Kazanç Hesabı               │ Yok                      │ Günlük+FM+Tatil kazanç         │
│ Gün Tipi                    │ Yok                      │ Normal/Cumartesi/Tatil         │
│ Şantiye/Maliyet Merkezi     │ Yok                      │ Var (cost_center_id)           │
│ Vardiya Desteği             │ Yok                      │ Var (vardiya_kodu)             │
│ Resmi Tatil Entegrasyonu    │ Yok                      │ Var (calendar_holidays)        │
│ İzin Bakiye Takibi          │ Yok                      │ Var (personnel_leave_balance)  │
│ Aylık Özet View             │ Yok                      │ Var (v_monthly_attendance_*)   │
│ Trigger Desteği             │ Yok                      │ Var (izin bakiye güncelleme)   │
│ Luca Uyumluluğu             │ Hayır                    │ Evet                           │
└─────────────────────────────┴──────────────────────────┴────────────────────────────────┘

KULLANIM ALANLARI:

📌 PERSONNEL_ATTENDANCE (Basit):
   - Sadece giriş-çıkış takibi gerekiyorsa
   - Basit puantaj kayıtları için
   - Minimal veri gereksinimleri
   - Hızlı sorgular

📌 PERSONNEL_DAILY_ATTENDANCE (Gelişmiş):
   - Luca mali müşavir entegrasyonu
   - Detaylı bordro hesaplamaları
   - İzin yönetimi ve bakiye takibi
   - Fazla mesai, tatil mesaisi ayrımı
   - Vardiya bazlı çalışma
   - Maliyet merkezi bazında raporlama
   - Resmi tatil otomasyonu
   - Aylık özet raporlar

ÖNERİ:
------
✓ Yeni sistemler için: personnel_daily_attendance kullanın
✓ Luca entegrasyonu için: personnel_daily_attendance zorunlu
✓ Basit takip için: personnel_attendance yeterli
✓ İkisini birlikte kullanmayın - veri tutarsızlığı yaratır

GEÇIŞ SENARYOSU:
---------------
Eğer personnel_attendance kullanıyorsanız:
1. Verileri personnel_daily_attendance'a migrate edin
2. Eski tabloyu yedekleyin
3. Yeni sisteme geçin
4. API endpoint'leri güncelleyin
""")

cursor.close()
conn.close()

print("\n" + "=" * 100)
