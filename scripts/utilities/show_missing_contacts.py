from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("EKSİK 3 CONTACT DETAYI:")
print("="*60)

r = db.execute(text("""
    SELECT DISTINCT
        e.supplier_tax_number,
        e.supplier_name,
        COUNT(*) as fatura_sayisi
    FROM einvoices e
    LEFT JOIN contacts c ON e.supplier_tax_number = c.tax_number
    WHERE e.invoice_category = 'incoming'
    AND c.id IS NULL
    GROUP BY e.supplier_tax_number, e.supplier_name
""")).fetchall()

for x in r:
    print(f"{x.supplier_tax_number} ({len(x.supplier_tax_number)} hane) | {x.fatura_sayisi} fatura")
    print(f"  İsim: {x.supplier_name}")
    print()

db.close()
