"""
monthly_personnel_records tablosundaki dönemleri kontrol et
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

# Dönemleri göster
print("=" * 60)
print("MEVCUT DÖNEMLER")
print("=" * 60)

cursor.execute("""
    SELECT donem, COUNT(*) as kayit_sayisi,
           COUNT(DISTINCT personnel_id) as personel_sayisi,
           MIN(ise_giris_tarihi) as ilk_giris,
           MAX(ise_giris_tarihi) as son_giris
    FROM monthly_personnel_records
    GROUP BY donem
    ORDER BY donem DESC
""")

for row in cursor:
    donem, kayit, personel, ilk, son = row
    print(f"\n📅 Dönem: {donem}")
    print(f"   Kayıt sayısı: {kayit}")
    print(f"   Personel sayısı: {personel}")
    print(f"   İlk giriş: {ilk}")
    print(f"   Son giriş: {son}")

# Excel dosyasındaki dönem ne idi?
print("\n" + "=" * 60)
print("EXCEL DOSYASI BİLGİSİ")
print("=" * 60)
print("Dosya: personel_sicil_listesi_kadiogulla (18).xlsx")
print("Excel adı '(18)' - muhtemelen 18. ay yani Haziran değil")
print("Ağustos 2025 olması bekleniyor")

conn.close()
