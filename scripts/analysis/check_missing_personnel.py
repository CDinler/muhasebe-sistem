"""
Eksik TC'leri kontrol et - Personnel tablosunda olmayanları göster
"""
from app.core.database import engine
from sqlalchemy import text

# Log dosyasındaki TC'ler
missing_tcs = [
    '61171395340', '46804748472', '15134819282', '63529051304', '12287969420',
    '44278693014', '59659514352', '45016061676', '40849559420', '54412221652',
    '56956485682', '10715812690', '46819748344', '33428209472', '35789077400',
    '46849542608', '46891871992', '64444070920', '24062118442', '62668439936',
    '14771250120', '43072236748', '63157063786', '41614781800', '11720996320',
    '10605081618', '20818855838', '62272248160', '33446180616', '27823631372',
    '10796745368', '39601848964', '26188950852', '64213293628', '17239994970',
    '22210818992'
]

print("=" * 80)
print(f"EKSIK PERSONEL KONTROLÜ - {len(missing_tcs)} TC")
print("=" * 80)

with engine.connect() as conn:
    # Personnel tablosunda var mı kontrol et
    placeholders = ','.join([f"'{tc}'" for tc in missing_tcs])
    result = conn.execute(text(f"""
        SELECT tckn, first_name, last_name, is_active
        FROM personnel
        WHERE tckn IN ({placeholders})
    """))
    
    found = {row[0]: row for row in result}
    
    print(f"\n✅ Veritabanında bulunan: {len(found)}")
    print(f"❌ Veritabanında OLMAYAN: {len(missing_tcs) - len(found)}")
    
    if found:
        print("\n" + "=" * 80)
        print("BULUNANLAR (Pasif olabilir)")
        print("=" * 80)
        for tc, (tckn, first_name, last_name, is_active) in found.items():
            status = "✅ Aktif" if is_active else "❌ Pasif"
            print(f"  {tc} - {first_name} {last_name} - {status}")
    
    not_found = [tc for tc in missing_tcs if tc not in found]
    
    if not_found:
        print("\n" + "=" * 80)
        print(f"VERITABANINDA OLMAYANLAR - {len(not_found)} TC")
        print("=" * 80)
        print("Bu TC'leri personnel tablosuna eklemek için:")
        print("  python create_missing_personnel.py")
        print("\nYa da Excel'i tekrar yükleyin - otomatik oluşturma özelliği eklenecek")
        
        # TC'leri yazdır
        for i, tc in enumerate(not_found, 1):
            print(f"  {i:2d}. {tc}")

print("\n" + "=" * 80)
print("ÖNERİ")
print("=" * 80)
print("Bu personeller Excel'de var ama personnel tablosunda yok.")
print("Sicil import endpoint'ini güncelleyerek otomatik personnel oluşturabilirsiniz.")
print("Ya da manuel olarak personnel tablosuna ekleyin.")
