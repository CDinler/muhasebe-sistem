"""
Önce PDF, sonra XML eklenen faturaları kontrol et
"""
from sqlalchemy import create_engine, text

engine = create_engine('mysql+pymysql://root@localhost/muhasebe_sistem')
conn = engine.connect()

print("\n=== ÖNCE PDF, SONRA XML YÜKLENENLER ===\n")

# has_xml=1 (XML var) VE pdf_path IS NOT NULL (PDF de var)
result = conn.execute(text("""
    SELECT 
        invoice_number,
        invoice_uuid,
        issue_date,
        has_xml,
        pdf_path IS NOT NULL as has_pdf,
        signing_time IS NOT NULL as has_signing_time,
        signing_time,
        xml_file_path
    FROM einvoices 
    WHERE issue_date >= '2025-12-01' 
      AND issue_date < '2026-01-01'
      AND has_xml = 1
      AND pdf_path IS NOT NULL
    ORDER BY invoice_number
"""))

total = 0
with_signing = 0
without_signing = 0

print("FATURA NO | ETTN (ilk 8) | PDF | XML | signing_time")
print("-" * 70)

for row in result:
    total += 1
    if row.has_signing_time:
        with_signing += 1
        status = "OK"
    else:
        without_signing += 1
        status = "EKSIK!"
    
    print(f"{row.invoice_number:20} | {str(row.invoice_uuid)[:8]} | {'VAR':3} | {'VAR':3} | {status:6} {row.signing_time or ''}")

print("\n" + "=" * 70)
print(f"TOPLAM: {total} fatura (PDF + XML)")
print(f"signing_time VAR:  {with_signing} ({with_signing/total*100:.1f}%)" if total > 0 else "")
print(f"signing_time YOK:  {without_signing} ({without_signing/total*100:.1f}%)" if total > 0 else "")

conn.close()
