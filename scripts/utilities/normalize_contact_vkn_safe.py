"""
Contact VKN Normalizasyonu v2 - Duplicate kontrolü ile
"""
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print('='*80)
print('CONTACT VKN/TCKN NORMALİZASYONU (Duplicate Safe)')
print('='*80)

# 1. Duplicate problemi tespit et
print('\n1. DUPLICATE ANALİZİ:')
print('-'*80)

# Normalize edilince duplicate olacak kayıtları bul
duplicates = db.execute(text("""
    SELECT 
        LPAD(tax_number, 10, '0') as normalized_vkn,
        GROUP_CONCAT(DISTINCT id ORDER BY id) as contact_ids,
        GROUP_CONCAT(DISTINCT name ORDER BY name SEPARATOR ' | ') as contact_names,
        COUNT(*) as duplicate_count
    FROM contacts
    WHERE tax_number IS NOT NULL
    AND tax_number REGEXP '^[0-9]+$'
    AND LENGTH(tax_number) IN (8, 9)
    GROUP BY LPAD(tax_number, 10, '0')
    HAVING COUNT(*) > 1
       OR EXISTS (
           SELECT 1 FROM contacts c2 
           WHERE c2.tax_number = LPAD(contacts.tax_number, 10, '0')
       )
""")).fetchall()

if duplicates:
    print(f'\n⚠️  {len(duplicates)} VKN duplicate olacak:')
    for dup in duplicates[:5]:
        print(f'  {dup.normalized_vkn}: {dup.duplicate_count} kayıt → [{dup.contact_ids}]')
        print(f'    İsimler: {dup.contact_names[:100]}...')

# 2. Stratejik UPDATE - Duplicate olmayacak şekilde
print('\n2. GÜVENLİ NORMALİZASYON:')
print('-'*80)

# 2a. Önce duplicate olmayacak olanları güncelle (8 hane)
safe_8 = db.execute(text("""
    SELECT COUNT(*) FROM contacts c1
    WHERE LENGTH(c1.tax_number) = 8
    AND c1.tax_number REGEXP '^[0-9]+$'
    AND NOT EXISTS (
        SELECT 1 FROM contacts c2
        WHERE c2.tax_number = LPAD(c1.tax_number, 10, '0')
        AND c2.id != c1.id
    )
""")).scalar()

print(f'\n8 hane → 10 hane (duplicate olmayan): {safe_8} kayıt')

result = db.execute(text("""
    UPDATE contacts c1
    SET tax_number = LPAD(tax_number, 10, '0')
    WHERE LENGTH(c1.tax_number) = 8
    AND c1.tax_number REGEXP '^[0-9]+$'
    AND NOT EXISTS (
        SELECT 1 FROM contacts c2
        WHERE c2.tax_number = LPAD(c1.tax_number, 10, '0')
        AND c2.id != c1.id
    )
"""))
print(f'✅ Güncellendi: {result.rowcount} kayıt')

# 2b. 9 hane → 10 hane (duplicate olmayan)
safe_9 = db.execute(text("""
    SELECT COUNT(*) FROM contacts c1
    WHERE LENGTH(c1.tax_number) = 9
    AND c1.tax_number REGEXP '^[0-9]+$'
    AND NOT EXISTS (
        SELECT 1 FROM contacts c2
        WHERE c2.tax_number = LPAD(c1.tax_number, 10, '0')
        AND c2.id != c1.id
    )
""")).scalar()

print(f'\n9 hane → 10 hane (duplicate olmayan): {safe_9} kayıt')

result = db.execute(text("""
    UPDATE contacts c1
    SET tax_number = LPAD(tax_number, 10, '0')
    WHERE LENGTH(c1.tax_number) = 9
    AND c1.tax_number REGEXP '^[0-9]+$'
    AND NOT EXISTS (
        SELECT 1 FROM contacts c2
        WHERE c2.tax_number = LPAD(c1.tax_number, 10, '0')
        AND c2.id != c1.id
    )
"""))
print(f'✅ Güncellendi: {result.rowcount} kayıt')

db.commit()

# 3. Kalan duplicate'leri raporla
remaining_dups = db.execute(text("""
    SELECT 
        c1.id, 
        c1.name, 
        c1.tax_number as eski_vkn,
        LPAD(c1.tax_number, 10, '0') as yeni_vkn,
        c2.id as mevcut_id,
        c2.name as mevcut_isim
    FROM contacts c1
    JOIN contacts c2 ON c2.tax_number = LPAD(c1.tax_number, 10, '0') AND c2.id != c1.id
    WHERE c1.tax_number REGEXP '^[0-9]+$'
    AND LENGTH(c1.tax_number) IN (8, 9)
    ORDER BY LPAD(c1.tax_number, 10, '0'), c1.id
    LIMIT 20
""")).fetchall()

if remaining_dups:
    print(f'\n⚠️  DUPLICATE KALAN: {len(remaining_dups)} kayıt (MANUEL İNCELEME GEREKLİ)')
    print('\nÖrnekler:')
    for dup in remaining_dups[:10]:
        print(f'  ID:{dup.id:4d} | {dup.eski_vkn} → {dup.yeni_vkn}')
        print(f'    Bu isim: {dup.name}')
        print(f'    Var olan: ID:{dup.mevcut_id} - {dup.mevcut_isim}')
        print()

# 4. Sonuç raporu
print('='*80)
print('SONUÇ:')
print('='*80)

vkn_after = db.execute(text("""
    SELECT 
        LENGTH(tax_number) as uzunluk,
        COUNT(*) as adet
    FROM contacts
    WHERE tax_number IS NOT NULL
    AND tax_number REGEXP '^[0-9]+$'
    GROUP BY LENGTH(tax_number)
    ORDER BY LENGTH(tax_number)
""")).fetchall()

print('\nGüncel VKN/TCKN dağılımı:')
for v in vkn_after:
    print(f'  {v.uzunluk} hane: {v.adet:4d} contact')

# 5. E-Fatura eşleşme kontrolü
missing = db.execute(text("""
    SELECT COUNT(DISTINCT e.supplier_tax_number)
    FROM einvoices e
    LEFT JOIN contacts c ON e.supplier_tax_number = c.tax_number
    WHERE e.invoice_category = 'incoming'
    AND c.id IS NULL
    AND e.supplier_tax_number IS NOT NULL
""")).scalar()

print(f'\n✅ Eksik contact: {missing}')

if missing > 0:
    samples = db.execute(text("""
        SELECT DISTINCT
            e.supplier_tax_number,
            e.supplier_name,
            COUNT(*) as fatura_sayisi
        FROM einvoices e
        LEFT JOIN contacts c ON e.supplier_tax_number = c.tax_number
        WHERE e.invoice_category = 'incoming'
        AND c.id IS NULL
        GROUP BY e.supplier_tax_number, e.supplier_name
        ORDER BY fatura_sayisi DESC
        LIMIT 10
    """)).fetchall()
    
    print('\nEksik contact örnekleri:')
    for s in samples:
        print(f'  {s.supplier_tax_number} ({len(s.supplier_tax_number)} hane) | {s.fatura_sayisi:3d} fatura | {s.supplier_name}')

db.close()
print('\n✨ İşlem tamamlandı!')
