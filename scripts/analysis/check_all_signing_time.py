"""
TÜM VERİTABANI - signing_time eksik faturalar
"""
from sqlalchemy import create_engine, text

engine = create_engine('mysql+pymysql://root@localhost/muhasebe_sistem')
conn = engine.connect()

print("\n=== TÜM FATURALARDAKİ signing_time DURUMU ===\n")

# Genel istatistik
result = conn.execute(text("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN signing_time IS NOT NULL THEN 1 ELSE 0 END) as with_signing,
        SUM(CASE WHEN signing_time IS NULL THEN 1 ELSE 0 END) as without_signing
    FROM einvoices
"""))

row = result.first()
print(f"TOPLAM FATURA:     {row.total:5}")
print(f"signing_time VAR:  {row.with_signing:5} ({row.with_signing/row.total*100:.1f}%)")
print(f"signing_time YOK:  {row.without_signing:5} ({row.without_signing/row.total*100:.1f}%)")

# Eksik olanları kategorize et
print("\n=== signing_time EKSİK FATURALAR - KATEGORİ ANALİZİ ===\n")

result2 = conn.execute(text("""
    SELECT 
        has_xml,
        source,
        pdf_path IS NOT NULL as has_pdf,
        xml_file_path IS NOT NULL as has_xml_file,
        COUNT(*) as count
    FROM einvoices 
    WHERE signing_time IS NULL
    GROUP BY has_xml, source, has_pdf, has_xml_file
    ORDER BY count DESC
"""))

print("has_xml | source    | PDF | XML | Adet")
print("-" * 50)

for row in result2:
    pdf = "VAR" if row.has_pdf else "YOK"
    xml = "VAR" if row.has_xml_file else "YOK"
    print(f"{row.has_xml:7} | {row.source:9} | {pdf:3} | {xml:3} | {row.count:4}")

# Örnek kayıtlar
print("\n=== signing_time EKSİK - İLK 10 ÖRNEK ===\n")

result3 = conn.execute(text("""
    SELECT 
        invoice_number,
        issue_date,
        has_xml,
        source,
        pdf_path IS NOT NULL as has_pdf,
        xml_file_path
    FROM einvoices 
    WHERE signing_time IS NULL
    ORDER BY issue_date DESC
    LIMIT 10
"""))

print("Fatura No         | Tarih      | has_xml | source    | PDF | XML Path")
print("-" * 90)

for row in result3:
    pdf = "VAR" if row.has_pdf else "---"
    xml_info = "VAR" if row.xml_file_path else "YOK"
    print(f"{row.invoice_number:18} | {row.issue_date} | {row.has_xml:7} | {row.source:9} | {pdf:3} | {xml_info}")

conn.close()
