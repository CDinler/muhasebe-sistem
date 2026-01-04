import http.client
import json

conn = http.client.HTTPConnection("localhost", 8000)
conn.request("GET", "/api/v1/daily-attendance/grid?donem=2026-01&cost_center_id=32")
response = conn.getresponse()
data = response.read()

result = json.loads(data)

print(f"Status: {response.status}")
print(f"Success: {result.get('success')}")
print(f"Total: {result.get('total')}")
print(f"Holidays: {result.get('holidays')}")

if result.get('records'):
    first = result['records'][0]
    print(f"\nFirst record:")
    print(f"  Name: {first.get('adi_soyadi')}")
    print(f"  gun_1: {first.get('gun_1')}")
    print(f"  gun_2: {first.get('gun_2')}")
    
conn.close()
