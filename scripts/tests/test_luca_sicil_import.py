"""
Luca Sicil Import Testi
"""
import requests
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

# Excel dosya yolu
EXCEL_PATH = r"C:\Users\CAGATAY\Downloads\personel_sicil_listesi_kadiogulla (18).xlsx"

def test_luca_sicil_upload():
    """Luca sicil dosyasını upload et"""
    print("=" * 80)
    print("LUCA SİCİL UPLOAD TESTİ")
    print("=" * 80)
    
    # Dosya kontrolü
    excel_file = Path(EXCEL_PATH)
    if not excel_file.exists():
        print(f"❌ Dosya bulunamadı: {EXCEL_PATH}")
        return
    
    print(f"✅ Dosya bulundu: {excel_file.name}")
    print(f"   Boyut: {excel_file.stat().st_size / 1024:.2f} KB")
    
    # Upload
    print("\n📤 Upload başlatılıyor...")
    
    with open(excel_file, 'rb') as f:
        files = {'file': (excel_file.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        params = {'force_update': False}
        
        try:
            response = requests.post(
                f"{BASE_URL}/luca-sicil/upload",
                files=files,
                params=params,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ UPLOAD BAŞARILI!")
                print(f"   Dönem: {result['donem']}")
                print(f"   Toplam satır: {result['total_rows']}")
                print(f"   Import edilen: {result['imported_records']}")
                print(f"   Güncellenen: {result['updated_records']}")
                print(f"   Atlanan: {result['skipped_records']}")
                print(f"   Hata sayısı: {len(result['errors'])}")
                print(f"   Uyarı sayısı: {len(result['warnings'])}")
                
                if result['errors']:
                    print("\n⚠️ HATALAR:")
                    for error in result['errors'][:5]:  # İlk 5 hata
                        print(f"   - Satır {error.get('row')}: {error.get('message')}")
                
                if result['warnings']:
                    print("\n⚠️ UYARILAR:")
                    for warning in result['warnings'][:5]:  # İlk 5 uyarı
                        print(f"   - Satır {warning.get('row')}: {warning.get('message')}")
                
            else:
                print(f"\n❌ Upload hatası: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"\n❌ Hata: {str(e)}")


def test_get_records():
    """Kayıtları listele"""
    print("\n" + "=" * 80)
    print("KAYITLARI LİSTELE")
    print("=" * 80)
    
    try:
        # Dönemleri al
        response = requests.get(f"{BASE_URL}/luca-sicil/periods")
        if response.status_code == 200:
            periods = response.json()['periods']
            print(f"\n📅 Mevcut dönemler: {periods}")
            
            if periods:
                # İlk dönemin kayıtlarını göster
                donem = periods[0]
                print(f"\n📋 {donem} dönemi kayıtları:")
                
                response = requests.get(
                    f"{BASE_URL}/luca-sicil/records",
                    params={'donem': donem, 'limit': 10}
                )
                
                if response.status_code == 200:
                    records = response.json()
                    print(f"   Toplam gösterilen: {len(records)}")
                    
                    for i, record in enumerate(records[:5], 1):
                        print(f"\n   {i}. {record['personnel_name']}")
                        print(f"      Bölüm: {record['bolum_adi']}")
                        print(f"      Cost Center: {record['cost_center_code']}")
                        print(f"      Giriş: {record['ise_giris_tarihi']}")
                        print(f"      Çıkış: {record['isten_cikis_tarihi']}")
                        print(f"      Ücret: {record['ucret']} {record['ucret_tipi']}")
                else:
                    print(f"❌ Kayıtlar alınamadı: {response.status_code}")
        else:
            print(f"❌ Dönemler alınamadı: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Hata: {str(e)}")


def test_get_personnel_records():
    """Belirli bir personelin tüm dönem kayıtlarını göster"""
    print("\n" + "=" * 80)
    print("PERSONEL DÖNEM KAYITLARI")
    print("=" * 80)
    
    # Örnek: TC ile personel bul ve kayıtlarını göster
    try:
        # Önce bir personel seç (TC: 22499643278 - 8 farklı bölümde çalışan)
        personnel_id = 1  # Gerçek ID'yi buraya yazmalıyız
        
        response = requests.get(
            f"{BASE_URL}/luca-sicil/records",
            params={'personnel_id': personnel_id}
        )
        
        if response.status_code == 200:
            records = response.json()
            if records:
                print(f"\n📋 {records[0]['personnel_name']} - Tüm dönem kayıtları:")
                print(f"   Toplam kayıt: {len(records)}")
                
                for record in records:
                    print(f"\n   - Dönem: {record['donem']}")
                    print(f"     Bölüm: {record['bolum_adi']}")
                    print(f"     Giriş-Çıkış: {record['ise_giris_tarihi']} / {record['isten_cikis_tarihi']}")
            else:
                print("   Kayıt bulunamadı")
        else:
            print(f"❌ Kayıtlar alınamadı: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Hata: {str(e)}")


if __name__ == "__main__":
    # 1. Upload testi
    test_luca_sicil_upload()
    
    # 2. Kayıtları listele
    test_get_records()
    
    # 3. Personel dönem kayıtları (opsiyonel)
    # test_get_personnel_records()
    
    print("\n" + "=" * 80)
    print("✅ TEST TAMAMLANDI")
    print("=" * 80)
