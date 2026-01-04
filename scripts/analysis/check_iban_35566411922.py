"""
VKN 35566411922 için contact ve IBAN kontrolü
"""
from sqlalchemy import create_engine, text

engine = create_engine('mysql+pymysql://root@localhost/muhasebe_sistem')
conn = engine.connect()

print("\n=== VKN 35566411922 KONTROL ===\n")

# Contact bilgisi
result = conn.execute(text("""
    SELECT id, name, tax_number, tax_office, iban, address, city
    FROM contacts 
    WHERE CAST(tax_number AS UNSIGNED) = CAST('35566411922' AS UNSIGNED)
"""))

contact = result.first()

if contact:
    print(f"ID: {contact.id}")
    print(f"Unvan: {contact.name}")
    print(f"VKN: {contact.tax_number}")
    print(f"Vergi Dairesi: {contact.tax_office or 'YOK'}")
    print(f"IBAN: {contact.iban or 'YOK'}")
    print(f"Adres: {contact.address or 'YOK'}")
    print(f"Şehir: {contact.city or 'YOK'}")
    
    # Bu VKN ile ilgili faturalarda IBAN var mı?
    print(f"\n=== BU CONTACT'IN FATURALARI ===\n")
    
    result2 = conn.execute(text("""
        SELECT invoice_number, issue_date, supplier_name, supplier_iban, supplier_tax_number
        FROM einvoices 
        WHERE supplier_tax_number = '35566411922'
        ORDER BY issue_date DESC
        LIMIT 5
    """))
    
    for row in result2:
        print(f"Fatura: {row.invoice_number} | {row.issue_date}")
        print(f"  Tedarikçi: {row.supplier_name}")
        print(f"  IBAN: {row.supplier_iban or 'YOK'}")
        print()
else:
    print("❌ Bu VKN ile contact bulunamadı!")

# Genel IBAN istatistikleri
print("\n=== GENEL IBAN İSTATİSTİKLERİ ===\n")

result3 = conn.execute(text("""
    SELECT 
        COUNT(*) as toplam,
        SUM(CASE WHEN iban IS NOT NULL AND iban != '' THEN 1 ELSE 0 END) as iban_var,
        SUM(CASE WHEN iban IS NULL OR iban = '' THEN 1 ELSE 0 END) as iban_yok
    FROM contacts
"""))

stats = result3.first()
print(f"Toplam Contact: {stats.toplam}")
print(f"IBAN VAR:       {stats.iban_var} ({stats.iban_var/stats.toplam*100:.1f}%)")
print(f"IBAN YOK:       {stats.iban_yok} ({stats.iban_yok/stats.toplam*100:.1f}%)")

# XML'lerde IBAN bilgisi olan faturalar
print("\n=== XML'LERDE IBAN BİLGİSİ ===\n")

result4 = conn.execute(text("""
    SELECT 
        COUNT(*) as toplam,
        SUM(CASE WHEN supplier_iban IS NOT NULL AND supplier_iban != '' THEN 1 ELSE 0 END) as iban_var
    FROM einvoices
    WHERE has_xml = 1
"""))

xml_stats = result4.first()
print(f"XML'li Toplam Fatura: {xml_stats.toplam}")
print(f"IBAN Bilgisi Olan:    {xml_stats.iban_var} ({xml_stats.iban_var/xml_stats.toplam*100:.1f}%)")

conn.close()
