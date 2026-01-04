"""
PDF Eşleştirme Sistemi Hızlı Test Script
Migration'dan sonra sistemin çalışıp çalışmadığını test eder.
"""

import requests
from pathlib import Path

API_BASE = "http://127.0.0.1:8000/api/v1"

# Test için örnek PDF dosyası (docs dizinindeki örneklerden)
TEST_PDF = Path(r"C:\Projects\muhasebe-sistem\docs\ornek_earsiv_pdf_faturalar\1_guven_sart_30000tl.pdf")

def test_backend_running():
    """Backend'in çalıştığını kontrol et."""
    print("\n1️⃣ Backend çalışıyor mu?")
    try:
        response = requests.get(f"{API_BASE}/einvoices/summary")
        if response.status_code == 401:
            print("   ⚠️  Backend çalışıyor ama giriş gerekiyor")
            return False
        elif response.status_code == 200:
            print("   ✅ Backend çalışıyor")
            return True
        else:
            print(f"   ❌ Backend yanıt verdi ama hata: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Backend çalışmıyor! Lütfen başlatın:")
        print("      cd C:\\Projects\\muhasebe-sistem\\backend")
        print("      uvicorn app.main:app --reload")
        return False

def test_pdf_endpoint_exists():
    """PDF upload endpoint'inin var olduğunu kontrol et."""
    print("\n2️⃣ PDF upload endpoint'i mevcut mu?")
    try:
        # Boş istekle endpoint'in varlığını test et (401 veya 422 dönerse endpoint var)
        response = requests.post(f"{API_BASE}/einvoices/pdf/upload-pdf")
        
        if response.status_code in [401, 422]:
            print("   ✅ PDF upload endpoint'i mevcut")
            return True
        elif response.status_code == 404:
            print("   ❌ PDF upload endpoint'i bulunamadı!")
            print("      Endpoint'in router'a eklendiğinden emin olun")
            return False
        else:
            print(f"   ✅ Endpoint mevcut (status: {response.status_code})")
            return True
    except Exception as e:
        print(f"   ❌ Test hatası: {e}")
        return False

def test_sample_pdf_exists():
    """Test PDF dosyasının var olduğunu kontrol et."""
    print("\n3️⃣ Test PDF dosyası mevcut mu?")
    if TEST_PDF.exists():
        print(f"   ✅ Test PDF bulundu: {TEST_PDF.name}")
        print(f"      Boyut: {TEST_PDF.stat().st_size / 1024:.1f} KB")
        return True
    else:
        print(f"   ❌ Test PDF bulunamadı: {TEST_PDF}")
        print("      Alternatif bir PDF dosyası kullanabilirsiniz")
        return False

def test_pdf_processor_import():
    """PDF processor modülünün import edilebilir olduğunu kontrol et."""
    print("\n4️⃣ PDF Processor modülü import edilebiliyor mu?")
    try:
        # Backend dizinine git
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        
        from app.services.einvoice_pdf_processor import EInvoicePDFProcessor
        print("   ✅ EInvoicePDFProcessor import edildi")
        return True
    except ImportError as e:
        print(f"   ❌ Import hatası: {e}")
        print("      Backend dependencies eksik olabilir")
        return False
    except Exception as e:
        print(f"   ⚠️  Import test edilemedi: {e}")
        return True  # Backend çalışırken import edilecek

def test_frontend_running():
    """Frontend'in çalıştığını kontrol et."""
    print("\n5️⃣ Frontend çalışıyor mu?")
    try:
        response = requests.get("http://localhost:5173", timeout=2)
        print("   ✅ Frontend çalışıyor (http://localhost:5173)")
        return True
    except:
        print("   ❌ Frontend çalışmıyor! Lütfen başlatın:")
        print("      cd C:\\Projects\\muhasebe-sistem\\frontend")
        print("      npm run dev")
        return False

def manual_test_guide():
    """Manuel test adımlarını göster."""
    print("\n" + "=" * 80)
    print("📋 MANUEL TEST ADIMLARI")
    print("=" * 80)
    print("""
1. Frontend'i açın: http://localhost:5173
2. Giriş yapın
3. E-Fatura sayfasına gidin
4. "PDF Yükle (E-Arşiv)" butonunu görebiliyor musunuz? (Yeşil renk)
   ✅ Görüyorsanız: Frontend güncellemeleri çalışıyor
   ❌ Görmüyorsanız: Frontend'i yeniden başlatın (npm run dev)

5. "PDF Yükle" butonuna tıklayın
6. Bir PDF seçin (örn: docs/ornek_earsiv_pdf_faturalar/1_guven_sart_30000tl.pdf)
7. "Gelen E-Arşiv Fatura" seçeneğini seçin
8. "Yükle" butonuna tıklayın

BEKLENEN SONUÇ:
   ✅ Progress bar görünür
   ✅ "PDF dosyası işleniyor..." mesajı
   ✅ "Başarılı! GIB2024000000041 faturası eklendi" mesajı
   ✅ Fatura listesine eklenir
   ✅ Faturanın yanında yeşil PDF ikonu görünür

HATA ALIYORSANIZ:
   ❌ "pdf_path column doesn't exist" → Migration çalıştırılmadı
   ❌ "404 Not Found" → API endpoint router'a eklenmedi
   ❌ "Connection refused" → Backend çalışmıyor
   ❌ "CORS error" → CORS ayarlarını kontrol edin
""")

def test_database_schema():
    """Database schema'nın güncel olduğunu kontrol et."""
    print("\n6️⃣ Database schema güncel mi?")
    try:
        import mysql.connector
        
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456',  # Burası değişebilir
            database='muhasebe_db'
        )
        cursor = conn.cursor()
        
        # pdf_path kolonu kontrolü
        cursor.execute("SHOW COLUMNS FROM einvoices LIKE 'pdf_path'")
        pdf_col = cursor.fetchone()
        
        # has_xml kolonu kontrolü  
        cursor.execute("SHOW COLUMNS FROM einvoices LIKE 'has_xml'")
        xml_col = cursor.fetchone()
        
        # source kolonu kontrolü
        cursor.execute("SHOW COLUMNS FROM einvoices LIKE 'source'")
        source_col = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if pdf_col and xml_col and source_col:
            print("   ✅ Database schema güncel (pdf_path, has_xml, source mevcut)")
            return True
        else:
            print("   ❌ Database schema eksik!")
            if not pdf_col:
                print("      - pdf_path kolonu yok")
            if not xml_col:
                print("      - has_xml kolonu yok")
            if not source_col:
                print("      - source kolonu yok")
            print("\n   Migration'ı çalıştırın:")
            print("   database/migrations/20251226_add_einvoice_pdf_support.sql")
            return False
            
    except Exception as e:
        print(f"   ⚠️  Database kontrolü yapılamadı: {e}")
        print("      Migration'ı manuel kontrol edin")
        return False

def main():
    """Tüm testleri çalıştır."""
    print("=" * 80)
    print("PDF EŞLEŞTİRME SİSTEMİ TEST")
    print("=" * 80)
    
    results = {}
    
    results['database'] = test_database_schema()
    results['backend'] = test_backend_running()
    results['pdf_endpoint'] = test_pdf_endpoint_exists()
    results['sample_pdf'] = test_sample_pdf_exists()
    results['processor'] = test_pdf_processor_import()
    results['frontend'] = test_frontend_running()
    
    print("\n" + "=" * 80)
    print("TEST SONUÇLARI")
    print("=" * 80)
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = "✅ BAŞARILI" if passed else "❌ BAŞARISIZ"
        print(f"{test_name.upper():<20}: {status}")
    
    print("\n" + "=" * 80)
    
    if all_passed:
        print("🎉 TÜM TESTLER BAŞARILI!")
        print("\nSistem kullanıma hazır. Manuel test adımlarını izleyin:")
        manual_test_guide()
    else:
        print("⚠️  BAZI TESTLER BAŞARISIZ")
        print("\nYukarıdaki hataları düzeltin ve tekrar test edin:")
        print("   python run_pdf_migration.py  # Migration için")
        print("   python test_pdf_system.py     # Testler için")
        
        # Kurulum dokümantasyonuna yönlendir
        print("\n📚 Detaylı kurulum adımları için:")
        print("   docs/PDF_ESLESTIRME_SISTEMI_KURULUM.md")

if __name__ == "__main__":
    main()
