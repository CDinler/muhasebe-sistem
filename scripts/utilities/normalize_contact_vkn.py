"""
Contact VKN/TCKN Normalizasyonu
Başta sıfır eksik olanları düzelt (E-Fatura formatına uyumlu hale getir)
"""
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print('='*80)
print('CONTACT VKN/TCKN NORMALİZASYONU')
print('='*80)

# 1. Mevcut durumu kontrol et
print('\n1. MEVCUT DURUM:')
print('-'*80)

vkn_stats = db.execute(text("""
    SELECT 
        LENGTH(tax_number) as uzunluk,
        COUNT(*) as adet,
        MIN(tax_number) as ornek_min,
        MAX(tax_number) as ornek_max
    FROM contacts
    WHERE tax_number IS NOT NULL
    AND tax_number REGEXP '^[0-9]+$'
    GROUP BY LENGTH(tax_number)
    ORDER BY LENGTH(tax_number)
""")).fetchall()

print('\nVKN/TCKN uzunluk dağılımı:')
total = 0
for stat in vkn_stats:
    total += stat.adet
    print(f'  {stat.uzunluk} hane: {stat.adet:4d} adet | Örnek: {stat.ornek_min} - {stat.ornek_max}')
print(f'\nToplam: {total} contact')

# 2. Normalizasyon yapılacakları say
normalize_needed = db.execute(text("""
    SELECT COUNT(*) FROM contacts
    WHERE tax_number IS NOT NULL
    AND tax_number REGEXP '^[0-9]+$'
    AND (
        (LENGTH(tax_number) = 9)  -- 9 hane VKN (başa 1 sıfır)
        OR (LENGTH(tax_number) = 8)  -- 8 hane VKN (başa 2 sıfır)
        OR (LENGTH(tax_number) = 10 AND tax_number NOT LIKE '0%')  -- 10 hane ama başta sıfır yok (TCKN olabilir)
    )
""")).scalar()

print(f'\n⚠️  Normalizasyon gerekli: {normalize_needed} contact')

if normalize_needed == 0:
    print('\n✅ Tüm VKN/TCKN formatları zaten düzgün!')
    db.close()
    exit(0)

# 3. Kullanıcıya sor
print('\nYapılacak işlemler:')
print('  - 8 hane → 10 hane (başa 2 sıfır)')
print('  - 9 hane → 10 hane (başa 1 sıfır)')
print('  - 10 hane (TCKN olabilecekler) → 11 hane (TCKN formatı)')
print('\n⚠️  NOT: TCKN/VKN ayrımı yapılamadığı için 10 haneli olanlar elle kontrol edilmeli!')

response = input(f'\n{normalize_needed} contact normalize edilsin mi? (E/H): ').strip().upper()

if response != 'E':
    print('❌ İşlem iptal edildi')
    db.close()
    exit(0)

# 4. Normalizasyon işlemleri
print('\nNormalizasyon başlıyor...\n')

# 4a. 8 hane → 10 hane
result = db.execute(text("""
    UPDATE contacts 
    SET tax_number = LPAD(tax_number, 10, '0')
    WHERE tax_number IS NOT NULL
    AND tax_number REGEXP '^[0-9]+$'
    AND LENGTH(tax_number) = 8
"""))
print(f'✅ 8 hane → 10 hane: {result.rowcount} contact')

# 4b. 9 hane → 10 hane
result = db.execute(text("""
    UPDATE contacts 
    SET tax_number = LPAD(tax_number, 10, '0')
    WHERE tax_number IS NOT NULL
    AND tax_number REGEXP '^[0-9]+$'
    AND LENGTH(tax_number) = 9
"""))
print(f'✅ 9 hane → 10 hane: {result.rowcount} contact')

# 4c. 10 hane başta sıfır olmayan → İnceleme gerekli (şimdilik atla)
problematic = db.execute(text("""
    SELECT 
        id, name, tax_number
    FROM contacts
    WHERE tax_number IS NOT NULL
    AND tax_number REGEXP '^[0-9]+$'
    AND LENGTH(tax_number) = 10
    AND tax_number NOT LIKE '0%'
    LIMIT 10
""")).fetchall()

if problematic:
    print(f'\n⚠️  10 hane ama başta sıfır yok: {len(problematic)} örnek (TCKN olabilir)')
    print('   (Bunları şimdilik dokunmuyoruz - manuel kontrol gerekli)')
    for p in problematic[:5]:
        print(f'     ID:{p.id:4d} | {p.tax_number} | {p.name}')

# Commit
db.commit()

# 5. Sonuç kontrolü
print('\n' + '='*80)
print('SONUÇ:')
print('='*80)

vkn_stats_after = db.execute(text("""
    SELECT 
        LENGTH(tax_number) as uzunluk,
        COUNT(*) as adet
    FROM contacts
    WHERE tax_number IS NOT NULL
    AND tax_number REGEXP '^[0-9]+$'
    GROUP BY LENGTH(tax_number)
    ORDER BY LENGTH(tax_number)
""")).fetchall()

print('\nYeni VKN/TCKN uzunluk dağılımı:')
for stat in vkn_stats_after:
    print(f'  {stat.uzunluk} hane: {stat.adet:4d} adet')

# 6. E-Fatura ile karşılaştır
print('\n' + '='*80)
print('E-FATURA İLE EŞLEŞME KONTROLÜ:')
print('='*80)

# Şimdi kaç tane eksik contact kaldı?
missing_after = db.execute(text("""
    SELECT COUNT(DISTINCT e.supplier_tax_number)
    FROM einvoices e
    LEFT JOIN contacts c ON e.supplier_tax_number = c.tax_number
    WHERE e.invoice_category = 'incoming'
    AND c.id IS NULL
    AND e.supplier_tax_number IS NOT NULL
""")).scalar()

print(f'\n✅ Normalizasyon SONRASI eksik contact: {missing_after}')

if missing_after > 0:
    print('\nEksik contact örnekleri:')
    samples = db.execute(text("""
        SELECT DISTINCT
            e.supplier_tax_number,
            e.supplier_name,
            COUNT(DISTINCT e.id) as fatura_sayisi
        FROM einvoices e
        LEFT JOIN contacts c ON e.supplier_tax_number = c.tax_number
        WHERE e.invoice_category = 'incoming'
        AND c.id IS NULL
        AND e.supplier_tax_number IS NOT NULL
        GROUP BY e.supplier_tax_number, e.supplier_name
        ORDER BY fatura_sayisi DESC
        LIMIT 10
    """)).fetchall()
    
    for s in samples:
        print(f'  {s.supplier_tax_number} ({len(s.supplier_tax_number)} hane) | {s.fatura_sayisi:3d} fatura | {s.supplier_name}')

db.close()
print('\n✨ İşlem tamamlandı!')
