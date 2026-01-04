"""
Mevcut e-faturaları yevmiye kayıtları ile eşleştir
Cari VKN/TCKN + Tutar (±1%) + Tarih (±60 gün) bazlı
"""
from app.core.database import SessionLocal
from sqlalchemy import text
from decimal import Decimal

db = SessionLocal()

print('=== MEVCUT E-FATURA - YEVMİYE EŞLEŞTİRME ===\n')

# 1. Potansiyel eşleştirmeleri bul
print('Adım 1: Potansiyel eşleştirmeler bulunuyor...')

matches_query = text("""
    SELECT 
        e.id as einvoice_id,
        e.invoice_number,
        e.issue_date,
        e.supplier_name,
        e.supplier_tax_number,
        e.payable_amount,
        t.id as transaction_id,
        t.transaction_number,
        t.transaction_date,
        t.description,
        ABS(tl.credit) as payment_amount,
        c.name as contact_name,
        DATEDIFF(t.transaction_date, e.issue_date) as date_diff_days,
        ABS(ABS(tl.credit) - e.payable_amount) / e.payable_amount * 100 as amount_diff_percent
    FROM einvoices e
    JOIN contacts c ON e.supplier_tax_number = c.tax_number
    JOIN transaction_lines tl ON tl.contact_id = c.id AND tl.credit > 0
    JOIN transactions t ON tl.transaction_id = t.id
    WHERE e.transaction_id IS NULL
    AND e.invoice_category = 'incoming'
    AND e.payable_amount > 0
    AND ABS(ABS(tl.credit) - e.payable_amount) / e.payable_amount <= 0.01  -- ±1%
    AND t.transaction_date BETWEEN DATE_SUB(e.issue_date, INTERVAL 60 DAY) 
                               AND DATE_ADD(e.issue_date, INTERVAL 60 DAY)
    ORDER BY e.issue_date DESC, ABS(DATEDIFF(t.transaction_date, e.issue_date))
""")

potential_matches = db.execute(matches_query).fetchall()
print(f'✅ {len(potential_matches)} potansiyel eşleştirme bulundu\n')

if not potential_matches:
    print('❌ Eşleştirilebilir kayıt bulunamadı!')
    print('\nOlası sebepler:')
    print('1. Cari VKN/TCKN eşleşmiyor (contacts tablosunda eksik cari)')
    print('2. Tutarlar farklı (±1% tolerans dışında)')
    print('3. Tarih farkı çok fazla (60 günden fazla)')
    print('\nDetaylı analiz için şu sorguyu çalıştırın:')
    print("""
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
    LIMIT 10;
    """)
    db.close()
    exit(0)

# 2. İlk 10 eşleştirmeyi göster
print('=== İLK 10 EŞLEŞTİRME ÖRNEĞİ ===')
for i, m in enumerate(potential_matches[:10], 1):
    print(f'\n{i}. {m.invoice_number}')
    print(f'   Fatura: {m.issue_date} | {m.payable_amount:,.2f} TL | {m.supplier_name}')
    print(f'   Yevmiye: {m.transaction_number} | {m.transaction_date} | {m.payment_amount:,.2f} TL')
    print(f'   Fark: {m.date_diff_days} gün | {m.amount_diff_percent:.2f}%')

# 3. Kullanıcıya sor
print('\n' + '='*60)
response = input(f'\n{len(potential_matches)} adet eşleştirme yapılsın mı? (E/H): ').strip().upper()

if response != 'E':
    print('❌ İşlem iptal edildi')
    db.close()
    exit(0)

# 4. Eşleştirmeleri uygula
print('\nEşleştirmeler uygulanıyor...')

# Aynı einvoice_id için birden fazla eşleşme varsa ilkini al
unique_matches = {}
for m in potential_matches:
    if m.einvoice_id not in unique_matches:
        unique_matches[m.einvoice_id] = m

success_count = 0
error_count = 0
duplicate_count = 0

for einvoice_id, match in unique_matches.items():
    try:
        # transaction_id'yi güncelle
        db.execute(text("""
            UPDATE einvoices 
            SET transaction_id = :tx_id,
                processing_status = 'TRANSACTION_CREATED'
            WHERE id = :einvoice_id
        """), {
            'tx_id': match.transaction_id,
            'einvoice_id': match.einvoice_id
        })
        
        # related_invoice_number'ı güncelle (varsa ekle, yoksa yaz)
        existing = db.execute(text("""
            SELECT related_invoice_number 
            FROM transactions 
            WHERE id = :tx_id
        """), {'tx_id': match.transaction_id}).scalar()
        
        if existing:
            invoice_numbers = set(existing.split(','))
            invoice_numbers.add(match.invoice_number)
            new_value = ','.join(sorted(invoice_numbers))
        else:
            new_value = match.invoice_number
        
        db.execute(text("""
            UPDATE transactions
            SET related_invoice_number = :invoice_nums
            WHERE id = :tx_id
        """), {
            'invoice_nums': new_value,
            'tx_id': match.transaction_id
        })
        
        success_count += 1
        
        if success_count % 50 == 0:
            print(f'  ✅ {success_count} eşleştirme tamamlandı...')
        
    except Exception as e:
        error_count += 1
        print(f'  ❌ Hata ({match.invoice_number}): {e}')

# Birden fazla eşleşme olanları say
duplicate_count = len(potential_matches) - len(unique_matches)

# Commit
db.commit()

print('\n' + '='*60)
print('=== ÖZET ===')
print(f'✅ Başarılı eşleştirme: {success_count}')
print(f'⚠️ Çoklu eşleşme (ilki alındı): {duplicate_count}')
print(f'❌ Hata: {error_count}')
print(f'📊 Toplam: {len(potential_matches)} potansiyel → {success_count} gerçekleşen')

# Doğrulama
result = db.execute(text('SELECT COUNT(*) FROM einvoices WHERE transaction_id IS NOT NULL')).scalar()
print(f'\n✅ Şu an {result:,} e-fatura yevmiye ile eşleşmiş durumda')

db.close()
print('\n✨ İşlem tamamlandı!')
