from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Örnek: VYF2024000000010 faturası
# Tutar: 75.00₺
# Contact: Vefa Yalıtım (ID: 5458)
# Tarih: 2024-01-09

print("ÖRNEK FATURA ARAMA:")
print("="*60)
print("Fatura: VYF2024000000010")
print("Tutar: 75.00₺")
print("Contact ID: 5458 (Vefa Yalıtım)")
print("Tarih: 2024-01-09")
print()

# Contact 5458 için TÜM transaction_lines kayıtlarını bul
transactions = db.execute(text("""
    SELECT 
        t.id,
        t.transaction_date,
        t.description,
        tl.debit,
        tl.credit,
        a.code as account_code,
        a.name as account_name
    FROM transaction_lines tl
    JOIN transactions t ON tl.transaction_id = t.id
    JOIN accounts a ON tl.account_id = a.id
    WHERE tl.contact_id = 5458
    AND t.transaction_date BETWEEN '2023-11-01' AND '2024-03-15'
    ORDER BY t.transaction_date
    LIMIT 20
""")).fetchall()

print(f"Bu contact için toplam {len(transactions)} kayıt bulundu:")
print()

for tr in transactions:
    marker = "🎯" if abs(tr.credit - 75.00) < 1 else ""
    print(f"{marker} T#{tr.id} | {tr.transaction_date} | " +
          f"Borç: {tr.debit:.2f}₺ | Alacak: {tr.credit:.2f}₺")
    print(f"   Hesap: {tr.account_code} - {tr.account_name}")
    print(f"   Açıklama: {tr.description}")
    print()

db.close()
