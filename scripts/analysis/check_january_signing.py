"""
Ocak ayı tüm faturaları analiz - signing_time durumu
"""
from sqlalchemy import create_engine, text

engine = create_engine('mysql+pymysql://root@localhost/muhasebe_sistem')
conn = engine.connect()

print("\n=== OCAK AYI DETAYLI ANALİZ ===\n")

# Tüm kategoriler
result = conn.execute(text("""
    SELECT 
        has_xml,
        source,
        pdf_path IS NOT NULL as has_pdf,
        COUNT(*) as total,
        SUM(CASE WHEN signing_time IS NOT NULL THEN 1 ELSE 0 END) as with_signing,
        SUM(CASE WHEN signing_time IS NULL THEN 1 ELSE 0 END) as without_signing
    FROM einvoices 
    WHERE issue_date >= '2025-01-01' 
      AND issue_date < '2025-02-01'
    GROUP BY has_xml, source, has_pdf
    ORDER BY has_xml, source, has_pdf
"""))

print("has_xml | source    | has_pdf | TOPLAM | signing_time VAR | signing_time YOK")
print("-" * 80)

for row in result:
    pdf_status = "VAR" if row.has_pdf else "YOK"
    print(f"{row.has_xml:7} | {row.source:9} | {pdf_status:7} | {row.total:6} | {row.with_signing:16} | {row.without_signing:16}")

# Signing_time eksik olanları detaylı göster
print("\n=== signing_time OLMAYAN FATURALAR ===\n")

result2 = conn.execute(text("""
    SELECT 
        invoice_number,
        invoice_uuid,
        has_xml,
        source,
        pdf_path IS NOT NULL as has_pdf,
        xml_file_path IS NOT NULL as has_xml_file
    FROM einvoices 
    WHERE issue_date >= '2025-01-01' 
      AND issue_date < '2025-02-01'
      AND signing_time IS NULL
    ORDER BY invoice_number
    LIMIT 20
"""))

eksik_count = 0
for row in result2:
    eksik_count += 1
    pdf = "PDF" if row.has_pdf else "---"
    xml = "XML" if row.has_xml_file else "---"
    print(f"{row.invoice_number:20} | {pdf:3} | {xml:3} | has_xml={row.has_xml} | source={row.source}")

if eksik_count == 0:
    print("✅ HİÇBİR FATURA EKSİK DEĞİL!")
else:
    print(f"\n⚠️ TOPLAM {eksik_count}+ fatura signing_time eksik")

conn.close()
