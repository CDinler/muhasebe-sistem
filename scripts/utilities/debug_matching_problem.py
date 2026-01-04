"""
Eşleşmeme nedenlerini detaylı analiz et
"""
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print('=== NEDEN EŞLEŞTİREMİYORUZ? ===\n')

# 1. Cari problemi
print('1. CARİ KONTROLÜ:')
result = db.execute(text("""
    SELECT 
        e.invoice_number,
        e.supplier_name,
        e.supplier_tax_number,
        COUNT(c.id) as cari_varmi
    FROM einvoices e
    LEFT JOIN contacts c ON e.supplier_tax_number = c.tax_number
    WHERE e.transaction_id IS NULL
    AND e.invoice_category = 'incoming'
    GROUP BY e.id
    HAVING cari_varmi = 0
    LIMIT 5
""")).fetchall()

cari_yok_count = db.execute(text("""
    SELECT COUNT(*) FROM (
        SELECT e.id
        FROM einvoices e
        LEFT JOIN contacts c ON e.supplier_tax_number = c.tax_number
        WHERE e.transaction_id IS NULL
        AND e.invoice_category = 'incoming'
        GROUP BY e.id
        HAVING COUNT(c.id) = 0
    ) sub
""")).scalar()

if result:
    print(f'❌ {cari_yok_count} faturanın carisi contacts tablosunda YOK')
    for r in result[:3]:
        print(f'  - {r.invoice_number}: {r.supplier_name} ({r.supplier_tax_number})')
else:
    print('✅ Tüm faturaların carisi mevcut')

# 2. Transaction lines kontrolü  
print('\n2. YEVMİYE SATIRLARI (320 hesaplar):')
result = db.execute(text("""
    SELECT COUNT(*) 
    FROM transaction_lines tl
    JOIN accounts a ON tl.account_id = a.id
    WHERE a.code LIKE '320.%' AND tl.credit > 0
""")).scalar()
print(f'Toplam 320 alacak satırı: {result:,}')

result = db.execute(text("""
    SELECT COUNT(DISTINCT tl.contact_id)
    FROM transaction_lines tl
    JOIN accounts a ON tl.account_id = a.id
    WHERE a.code LIKE '320.%' AND tl.credit > 0 AND tl.contact_id IS NOT NULL
""")).scalar()
print(f'Farklı cari sayısı: {result:,}')

# 3. Örnek eşleştirme denemesi (tutar kontrolü olmadan)
print('\n3. GEVŞEK EŞLEŞTİRME (Sadece cari):')
results = db.execute(text("""
    SELECT 
        e.invoice_number,
        e.payable_amount as fatura_tutar,
        t.transaction_number,
        ABS(tl.credit) as odeme_tutar,
        DATEDIFF(t.transaction_date, e.issue_date) as gun_fark,
        a.code as hesap_kodu
    FROM einvoices e
    JOIN contacts c ON e.supplier_tax_number = c.tax_number
    JOIN transaction_lines tl ON tl.contact_id = c.id AND tl.credit > 0
    JOIN transactions t ON tl.transaction_id = t.id
    JOIN accounts a ON tl.account_id = a.id
    WHERE e.transaction_id IS NULL
    AND e.invoice_category = 'incoming'
    AND a.code LIKE '320.%'
    LIMIT 10
""")).fetchall()

if results:
    print(f'✅ {len(results)} örnek (tutar farkı olabilir):')
    for r in results[:5]:
        tutar_fark = abs(float(r.fatura_tutar) - float(r.odeme_tutar))
        fark_percent = (tutar_fark / float(r.fatura_tutar)) * 100 if r.fatura_tutar > 0 else 0
        print(f'  {r.invoice_number}:')
        print(f'    Fatura: {r.fatura_tutar:,.2f} TL')
        print(f'    Ödeme: {r.odeme_tutar:,.2f} TL ({r.hesap_kodu})')
        print(f'    Fark: {tutar_fark:,.2f} TL ({fark_percent:.1f}%) | {r.gun_fark} gün')
else:
    print('❌ Cari bazlı bile eşleşme yok!')
    
# 4. E-fatura ve Contact VKN karşılaştırması
print('\n4. VKN FORMAT KONTROLÜ:')
results = db.execute(text("""
    SELECT 
        e.supplier_tax_number as efatura_vkn,
        c.tax_number as contact_vkn,
        COUNT(*) as eslesme_sayisi
    FROM einvoices e
    JOIN contacts c ON e.supplier_tax_number = c.tax_number
    WHERE e.invoice_category = 'incoming'
    GROUP BY e.supplier_tax_number, c.tax_number
    LIMIT 5
""")).fetchall()

if results:
    print(f'✅ VKN eşleşmeleri çalışıyor:')
    for r in results:
        print(f'  {r.efatura_vkn} = {r.contact_vkn} ({r.eslesme_sayisi} fatura)')
else:
    print('❌ VKN formatları uyuşmuyor!')

db.close()
