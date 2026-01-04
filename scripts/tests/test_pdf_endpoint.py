"""
PDF endpoint'ini test et
"""
import requests

try:
    response = requests.get('http://127.0.0.1:8000/api/v1/einvoices/pdf/3489')
    
    if response.status_code == 200:
        print(f"✅ HTTP 200 OK")
        print(f"📊 Content-Type: {response.headers.get('content-type')}")
        print(f"📊 Content-Length: {len(response.content)} bytes")
        
        # PDF başlangıcını kontrol et
        if response.content[:4] == b'%PDF':
            print("✅ Geçerli PDF dosyası")
        else:
            print("⚠️ PDF formatı doğrulanamadı")
            print(f"İlk 50 byte: {response.content[:50]}")
    else:
        print(f"❌ HTTP {response.status_code}")
        print(f"Detay: {response.text}")
        
except Exception as e:
    print(f"❌ Hata: {e}")
