"""Login endpoint'ini test et"""
import requests

url = "http://127.0.0.1:8000/api/v1/auth/login"
data = {
    "username": "admin",
    "password": "admin123"
}

try:
    response = requests.post(url, data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ LOGIN BAŞARILI!")
        print(f"Token: {response.json().get('access_token', 'YOK')[:50]}...")
    else:
        print("\n❌ LOGIN BAŞARISIZ!")
        
except Exception as e:
    print(f"❌ HATA: {e}")
