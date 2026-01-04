"""
Hesapları güncelle ve eksikleri ekle
"""
from app.core.database import engine
from sqlalchemy import text

conn = engine.connect()

# 191 hesapları mevcut mu kontrol et
result = conn.execute(text("SELECT code, name FROM accounts WHERE code LIKE '191%' ORDER BY code"))
print('MEVCUT 191 HESAPLARI:')
print('=' * 80)
for row in result:
    print(f'{row[0]:<15} {row[1]}')

# Yeni hesaplar ekleyelim (eğer yoksa)
new_accounts = [
    ('191.01.001', 'İndirilecek KDV %1', 'ASSET'),
    ('191.08.001', 'İndirilecek KDV %8', 'ASSET'),
    ('191.10.001', 'İndirilecek KDV %10', 'ASSET'),
    ('191.18.001', 'İndirilecek KDV %18', 'ASSET'),
    ('191.20.001', 'İndirilecek KDV %20', 'ASSET'),
    ('191.01.002', 'Sorumlu Sıfatıyla KDV Tevkifatı %1', 'ASSET'),
    ('191.08.002', 'Sorumlu Sıfatıyla KDV Tevkifatı %8', 'ASSET'),
    ('191.10.002', 'Sorumlu Sıfatıyla KDV Tevkifatı %10', 'ASSET'),
    ('191.18.002', 'Sorumlu Sıfatıyla KDV Tevkifatı %18', 'ASSET'),
    ('191.20.002', 'Sorumlu Sıfatıyla KDV Tevkifatı %20', 'ASSET'),
]

print('\nYENİ 191 HESAPLARI EKLENIYOR...')
for code, name, acc_type in new_accounts:
    try:
        conn.execute(text(f"""
            INSERT INTO accounts (code, name, account_type, is_active)
            VALUES ('{code}', '{name}', '{acc_type}', 1)
            ON DUPLICATE KEY UPDATE name = '{name}'
        """))
        print(f'✓ {code} - {name}')
    except Exception as e:
        print(f'✗ {code} - Hata: {e}')

# Diğer hesapları güncelle
updates = [
    ('602.00002', 'Alıştan İadeler'),
    ('689.00001', '5035 Sayılı Kanuna Göre Özel İletişim Vergisi'),
    ('689.00005', 'Telsiz Kullanım Ücreti'),
    ('679.00001', 'Düzeltmeler (Negatif Fark)'),
    ('659.00003', 'Düzeltmeler (Pozitif Fark)'),
    ('740.00209', 'Konaklama Vergisi'),
]

print('\nHESAPLAR GÜNCELLENİYOR...')
for code, name in updates:
    try:
        conn.execute(text(f"""
            INSERT INTO accounts (code, name, account_type, is_active)
            VALUES ('{code}', '{name}', 'EXPENSE', 1)
            ON DUPLICATE KEY UPDATE name = '{name}'
        """))
        print(f'✓ {code} - {name}')
    except Exception as e:
        print(f'✗ {code} - Hata: {e}')

conn.commit()

# Son kontrol
print('\n' + '=' * 80)
print('GÜNCEL 191 HESAPLARI:')
print('=' * 80)
result = conn.execute(text("SELECT code, name FROM accounts WHERE code LIKE '191%' ORDER BY code"))
for row in result:
    print(f'{row[0]:<15} {row[1]}')

conn.close()
print('\nİşlem tamamlandı!')
