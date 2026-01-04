from app.core.database import SessionLocal
from sqlalchemy import text
from decimal import Decimal

db = SessionLocal()

print("E-FATURA - YEVMİYE EŞLEŞTİRME")
print("="*60)

# Matching logic:
# 1. Contact VKN eşleşmesi (einvoices.supplier_tax_number = contacts.tax_number)
# 2. Tutar eşleşmesi ±1% (einvoices.payable_amount ~ transaction_lines.credit)
# 3. Tarih eşleşmesi ±60 gün (einvoices.issue_date ~ transactions.transaction_date)

matched_count = 0
unmatched_count = 0

# Tüm incoming e-invoices'ları al
einvoices = db.execute(text("""
    SELECT 
        e.id,
        e.invoice_number,
        e.supplier_tax_number,
        e.payable_amount,
        e.issue_date,
        e.transaction_id,
        c.id as contact_id,
        c.name as contact_name
    FROM einvoices e
    LEFT JOIN contacts c ON e.supplier_tax_number = c.tax_number
    WHERE e.invoice_category = 'incoming'
    ORDER BY e.issue_date
""")).fetchall()

print(f"📋 Toplam {len(einvoices)} gelen e-fatura bulundu")
print()

for einv in einvoices[:50]:  # İlk 50'yi test edelim
    # Eşleşen transaction bul
    # Koşullar:
    # - transaction_lines.contact_id = einvoice.contact_id
    # - transaction_lines.credit (alacak) = einvoice.payable_amount ±1%
    # - transactions.transaction_date = einvoice.issue_date ±60 gün
    # - transaction_lines.credit > 0 (alacak satırı)
    
    if not einv.contact_id:
        unmatched_count += 1
        print(f"❌ {einv.invoice_number}: Contact bulunamadı (VKN: {einv.supplier_tax_number})")
        continue
    
    # Tutar toleransı %1
    amount_min = float(einv.payable_amount) * 0.99
    amount_max = float(einv.payable_amount) * 1.01
    
    match = db.execute(text("""
        SELECT 
            t.id as transaction_id,
            t.transaction_date,
            t.description,
            tl.credit,
            tl.debit,
            ABS(tl.credit - :amount) as diff
        FROM transaction_lines tl
        JOIN transactions t ON tl.transaction_id = t.id
        WHERE tl.contact_id = :contact_id
        AND tl.credit >= :amount_min
        AND tl.credit <= :amount_max
        AND t.transaction_date BETWEEN DATE_SUB(:issue_date, INTERVAL 60 DAY) 
                                   AND DATE_ADD(:issue_date, INTERVAL 60 DAY)
        AND tl.credit > 0
        ORDER BY ABS(tl.credit - :amount), ABS(DATEDIFF(t.transaction_date, :issue_date))
        LIMIT 1
    """), {
        'contact_id': einv.contact_id,
        'amount': float(einv.payable_amount),
        'amount_min': amount_min,
        'amount_max': amount_max,
        'issue_date': einv.issue_date
    }).fetchone()
    
    if match:
        # Match bulundu! einvoices.transaction_id güncelle
        if einv.transaction_id != match.transaction_id:
            db.execute(text("""
                UPDATE einvoices 
                SET transaction_id = :tid
                WHERE id = :eid
            """), {
                'tid': match.transaction_id,
                'eid': einv.id
            })
            matched_count += 1
            print(f"✅ {einv.invoice_number} → T#{match.transaction_id} " +
                  f"({einv.payable_amount:.2f}₺ ≈ {match.credit:.2f}₺)")
        else:
            print(f"⏭️  {einv.invoice_number}: Zaten eşleşmiş")
    else:
        unmatched_count += 1
        print(f"❌ {einv.invoice_number}: Eşleşme bulunamadı " +
              f"({einv.contact_name}, {einv.payable_amount:.2f}₺, {einv.issue_date})")

db.commit()

print()
print("="*60)
print(f"✅ Eşleştirilen: {matched_count}")
print(f"❌ Eşleştirilemedi: {unmatched_count}")
print(f"📊 Toplam işlenen: {matched_count + unmatched_count}")

# Final istatistik
final_stats = db.execute(text("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN transaction_id IS NOT NULL THEN 1 ELSE 0 END) as matched,
        SUM(CASE WHEN transaction_id IS NULL THEN 1 ELSE 0 END) as unmatched
    FROM einvoices
    WHERE invoice_category = 'incoming'
""")).fetchone()

print()
print("GENEL DURUM:")
print(f"  Toplam gelen e-fatura: {final_stats.total}")
print(f"  Eşleşmiş: {final_stats.matched} ({final_stats.matched/final_stats.total*100:.1f}%)")
print(f"  Eşleşmemiş: {final_stats.unmatched} ({final_stats.unmatched/final_stats.total*100:.1f}%)")

db.close()
