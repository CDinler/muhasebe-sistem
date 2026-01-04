"""
Takvimli Puantaj Sistemi - Test Script
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

print("=" * 80)
print("TAKVİMLİ PUANTAJ SİSTEMİ - API TEST")
print("=" * 80)

# 1. Vardiya listesi
print("\n1. Vardiya Listesi")
print("-" * 40)
try:
    response = requests.get(f"{BASE_URL}/daily-attendance/shifts")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ {data['total']} vardiya tanımı bulundu")
        for shift in data['shifts']:
            print(f"  - {shift['code']}: {shift['name']} ({shift['start_time']} - {shift['end_time']})")
    else:
        print(f"✗ Hata: {response.status_code}")
except Exception as e:
    print(f"✗ Bağlantı hatası: {e}")

# 2. Resmi tatiller
print("\n2. Resmi Tatiller (2025)")
print("-" * 40)
try:
    response = requests.get(f"{BASE_URL}/daily-attendance/holidays/2025")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ {data['total']} resmi tatil tanımlı")
        for holiday in data['holidays'][:5]:
            print(f"  - {holiday['date']}: {holiday['name']}")
        print("  ...")
    else:
        print(f"✗ Hata: {response.status_code}")
except Exception as e:
    print(f"✗ Bağlantı hatası: {e}")

# 3. Aylık takvim oluşturma (örnek)
print("\n3. Aylık Takvim Oluşturma")
print("-" * 40)
donem = datetime.now().strftime("%Y-%m")
print(f"Dönem: {donem}")
print("⚠️  Gerçek veri için bu endpoint'i manuel çalıştırın:")
print(f"   POST {BASE_URL}/daily-attendance/generate-month?donem={donem}")

# 4. Takvim verilerini çek (varsa)
print("\n4. Takvim Verileri")
print("-" * 40)
try:
    response = requests.get(f"{BASE_URL}/daily-attendance/calendar/{donem}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ {data['total']} günlük kayıt bulundu")
        if data['total'] > 0:
            print(f"  İlk kayıt: {data['records'][0]['attendance_date']} - {data['records'][0]['adi_soyadi']}")
        else:
            print("  ℹ️  Henüz kayıt yok. 'Aylık Takvim Oluştur' butonunu kullanın.")
    else:
        print(f"✗ Hata: {response.status_code}")
except Exception as e:
    print(f"✗ Bağlantı hatası: {e}")

# 5. Aylık özet
print("\n5. Aylık Özet")
print("-" * 40)
try:
    response = requests.get(f"{BASE_URL}/daily-attendance/summary/{donem}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ {data['total']} personel özeti")
        for summary in data['summaries'][:3]:
            print(f"  - {summary['adi_soyadi']}: {summary['calisan_gun']} gün, {summary['toplam_normal_saat']:.1f} saat")
        if data['total'] > 3:
            print("  ...")
    else:
        print(f"✗ Hata: {response.status_code}")
except Exception as e:
    print(f"✗ Bağlantı hatası: {e}")

print("\n" + "=" * 80)
print("✅ API TEST TAMAMLANDI")
print("=" * 80)

print("\n📝 Sonraki Adımlar:")
print("1. Backend'i başlatın: cd backend && uvicorn app.main:app --reload")
print("2. Frontend'i başlatın: cd frontend && npm run dev")
print("3. Tarayıcıda açın: http://localhost:5173/daily-attendance")
print("4. 'Aylık Takvim Oluştur' butonuna tıklayın")
print("5. Excel yükleyin veya manuel kayıt ekleyin")
