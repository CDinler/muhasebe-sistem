from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Eksik 3 contact'ı einvoice'lardan al ve contacts'a ekle
missing_contacts = [
    ('5890476431', 'KRC ELEKTRO MARKET SAN.ve TİC.A.Ş.')  # Son kalan
]

print("EKSİK 3 CONTACT OLUŞTURULUYOR...")
print("="*60)

for vkn, name in missing_contacts:
    # einvoice'dan detayları al
    invoice = db.execute(text("""
        SELECT 
            supplier_tax_number,
            supplier_name,
            supplier_tax_office,
            supplier_address,
            supplier_city
        FROM einvoices
        WHERE supplier_tax_number = :vkn
        LIMIT 1
    """), {'vkn': vkn}).fetchone()
    
    if not invoice:
        # Eğer normalize edilmişse original VKN ile dene
        original_vkn = vkn.lstrip('0') if len(vkn) == 10 else vkn
        invoice = db.execute(text("""
            SELECT 
                supplier_tax_number,
                supplier_name,
                supplier_tax_office,
                supplier_address,
                supplier_city
            FROM einvoices
            WHERE supplier_tax_number = :vkn
            LIMIT 1
        """), {'vkn': original_vkn}).fetchone()
    
    if invoice:
        # Contact tipini belirle
        contact_type = 'individual' if len(vkn) == 11 else 'company'
        
        # Contact oluştur
        db.execute(text("""
            INSERT INTO contacts (
                name,
                tax_number,
                tax_office,
                address,
                city,
                country,
                contact_type
            ) VALUES (
                :name,
                :vkn,
                :tax_office,
                :address,
                :city,
                'Türkiye',
                :contact_type
            )
        """), {
            'name': invoice.supplier_name or name,
            'vkn': vkn,
            'tax_office': invoice.supplier_tax_office,
            'address': invoice.supplier_address,
            'city': invoice.supplier_city,
            'contact_type': contact_type
        })
        
        print(f"✅ {vkn} - {invoice.supplier_name or name} ({contact_type})")
    else:
        print(f"❌ {vkn} için fatura bulunamadı!")

db.commit()

# Kontrol et
remaining = db.execute(text("""
    SELECT COUNT(DISTINCT e.supplier_tax_number) as missing_count
    FROM einvoices e
    LEFT JOIN contacts c ON e.supplier_tax_number = c.tax_number
    WHERE e.invoice_category = 'incoming'
    AND c.id IS NULL
""")).fetchone()

print()
print(f"📊 Eksik contact sayısı: {remaining.missing_count}")

db.close()
