"""
Mevcut e-fatura ve yevmiye eşleştirme analizi
"""
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# E-fatura istatistikleri
print('=== E-FATURA İSTATİSTİKLERİ ===')
result = db.execute(text('SELECT COUNT(*) FROM einvoices')).scalar()
print(f'Toplam e-fatura: {result:,}')

result = db.execute(text('SELECT COUNT(*) FROM einvoices WHERE transaction_id IS NOT NULL')).scalar()
print(f'Yevmiye ile eşleşmiş: {result:,}')

result = db.execute(text('SELECT COUNT(*) FROM einvoices WHERE transaction_id IS NULL')).scalar()
print(f'Eşleşmemiş: {result:,}')

print('\n=== CARİ BAZLI ANALİZ ===')
result = db.execute(text("""
    SELECT 
        COUNT(*) as adet,
        COUNT(DISTINCT supplier_tax_number) as unique_cari
    FROM einvoices 
    WHERE transaction_id IS NULL 
    AND invoice_category = 'incoming'
    AND supplier_tax_number IS NOT NULL
""")).fetchone()
print(f'Eşleşmemiş gelen faturalar: {result.adet:,} ({result.unique_cari} farklı cari)')

print('\n=== TUTAR BAZLI ANALİZ ===')
result = db.execute(text("""
    SELECT 
        MIN(payable_amount) as min_tutar,
        MAX(payable_amount) as max_tutar,
        AVG(payable_amount) as avg_tutar,
        SUM(payable_amount) as toplam
    FROM einvoices 
    WHERE transaction_id IS NULL
    AND invoice_category = 'incoming'
""")).fetchone()
if result.min_tutar:
    print(f'Min: {result.min_tutar:,.2f} TL')
    print(f'Max: {result.max_tutar:,.2f} TL')
    print(f'Ortalama: {result.avg_tutar:,.2f} TL')
    print(f'Toplam: {result.toplam:,.2f} TL')
else:
    print('Veri yok')

print('\n=== POTANSİYEL EŞLEŞTİRME (Cari + Tutar) ===')
result = db.execute(text("""
    SELECT COUNT(*) FROM (
        SELECT DISTINCT
            e.id as einvoice_id,
            t.id as transaction_id
        FROM einvoices e
        JOIN contacts c ON e.supplier_tax_number = c.tax_number
        JOIN transaction_lines tl ON tl.contact_id = c.id
        JOIN transactions t ON tl.transaction_id = t.id
        WHERE e.transaction_id IS NULL
        AND e.invoice_category = 'incoming'
        AND ABS(ABS(tl.credit) - e.payable_amount) / e.payable_amount <= 0.01
        AND t.transaction_date BETWEEN DATE_SUB(e.issue_date, INTERVAL 60 DAY) 
                                   AND DATE_ADD(e.issue_date, INTERVAL 60 DAY)
        LIMIT 1000
    ) sub
""")).scalar()
print(f'Otomatik eşleştirilebilir (±60 gün, ±1% tutar): {result:,} adet')

print('\n=== ÖRNEK EŞLEŞTİRİLEBİLİR KAYITLAR ===')
results = db.execute(text("""
    SELECT 
        e.invoice_number,
        e.issue_date as fatura_tarihi,
        e.supplier_name,
        e.payable_amount as fatura_tutari,
        t.transaction_number as yevmiye_no,
        t.transaction_date as yevmiye_tarihi,
        ABS(tl.credit) as odeme_tutari,
        DATEDIFF(t.transaction_date, e.issue_date) as gun_farki
    FROM einvoices e
    JOIN contacts c ON e.supplier_tax_number = c.tax_number
    JOIN transaction_lines tl ON tl.contact_id = c.id
    JOIN transactions t ON tl.transaction_id = t.id
    WHERE e.transaction_id IS NULL
    AND e.invoice_category = 'incoming'
    AND ABS(ABS(tl.credit) - e.payable_amount) / e.payable_amount <= 0.01
    AND t.transaction_date BETWEEN DATE_SUB(e.issue_date, INTERVAL 60 DAY) 
                               AND DATE_ADD(e.issue_date, INTERVAL 60 DAY)
    ORDER BY e.issue_date DESC
    LIMIT 10
""")).fetchall()

if results:
    for r in results:
        print(f'\n{r.invoice_number}')
        print(f'  Fatura: {r.fatura_tarihi} - {r.fatura_tutari:,.2f} TL - {r.supplier_name}')
        print(f'  Yevmiye: {r.yevmiye_no} - {r.yevmiye_tarihi} - {r.odeme_tutari:,.2f} TL')
        print(f'  Tarih farkı: {r.gun_farki} gün')
else:
    print('Eşleştirilebilir kayıt bulunamadı')

db.close()
