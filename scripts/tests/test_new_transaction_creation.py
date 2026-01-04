"""
Test: create_accounting_transaction() yeni versiyon çalışıyor mu?
Turkcell faturasını import et ve database'e kaydedilen tüm alanları kontrol et
"""
import sys
sys.path.append('c:/Projects/muhasebe-sistem/backend')

from app.core.database import SessionLocal
from app.models.einvoice import EInvoice
from app.models.contact import Contact
from app.services.einvoice_accounting_service import create_accounting_transaction
from sqlalchemy import text

db = SessionLocal()

print("=" * 80)
print("TEST: create_accounting_transaction() YENİ VERSİYON")
print("=" * 80)

# Turkcell faturasını bul
turkcell_invoice = db.query(EInvoice).filter(
    EInvoice.invoice_number == 'TRE2024000026298'
).first()

if not turkcell_invoice:
    print("❌ Turkcell faturası bulunamadı (TRE2024000026298)")
    db.close()
    sys.exit(1)

print(f"\n✅ Turkcell faturası bulundu: {turkcell_invoice.invoice_number}")
print(f"   Toplam Tutar: {turkcell_invoice.payable_amount} TL")

# Contact bul
contact = db.query(Contact).filter(Contact.id == turkcell_invoice.contact_id).first()
if not contact:
    print("❌ Contact bulunamadı!")
    db.close()
    sys.exit(1)

print(f"✅ Contact: {contact.name}")

# Eski transaction varsa sil
if turkcell_invoice.transaction_id:
    print(f"\n⚠️  Eski transaction var (ID: {turkcell_invoice.transaction_id}), siliniyor...")
    db.execute(text("DELETE FROM transaction_lines WHERE transaction_id = :tid"), {'tid': turkcell_invoice.transaction_id})
    db.execute(text("DELETE FROM transactions WHERE id = :tid"), {'tid': turkcell_invoice.transaction_id})
    db.execute(text("DELETE FROM invoice_transaction_mappings WHERE transaction_id = :tid"), {'tid': turkcell_invoice.transaction_id})
    turkcell_invoice.transaction_id = None
    turkcell_invoice.processing_status = 'PENDING'
    db.commit()
    print("   Eski kayıtlar silindi")

# Yeni transaction oluştur
print("\n🔄 Yeni transaction oluşturuluyor (generate_transaction_lines_from_invoice kullanarak)...")

try:
    transaction = create_accounting_transaction(db, turkcell_invoice, contact)
    db.commit()
    print(f"✅ Transaction oluşturuldu: {transaction.transaction_number}")
    
    # Transaction alanlarını kontrol et
    print("\n" + "=" * 80)
    print("TRANSACTION ALANLARI KONTROLÜ")
    print("=" * 80)
    
    print(f"✅ transaction_number: {transaction.transaction_number}")
    print(f"✅ transaction_date: {transaction.transaction_date}")
    print(f"✅ accounting_period: {transaction.accounting_period}")
    print(f"✅ document_number: {transaction.document_number}")
    
    if transaction.cost_center_id:
        print(f"✅ cost_center_id: {transaction.cost_center_id}")
    else:
        print(f"❌ cost_center_id: NULL")
    
    if transaction.document_type_id:
        print(f"✅ document_type_id: {transaction.document_type_id}")
    else:
        print(f"❌ document_type_id: NULL")
    
    if transaction.document_subtype_id:
        print(f"✅ document_subtype_id: {transaction.document_subtype_id}")
    else:
        print(f"❌ document_subtype_id: NULL")
    
    # Transaction lines kontrolü
    print("\n" + "=" * 80)
    print("TRANSACTION LINES KONTROLÜ")
    print("=" * 80)
    
    query = text("""
    SELECT 
        tl.id,
        a.code as account_code,
        a.name as account_name,
        tl.description,
        tl.debit,
        tl.credit,
        tl.quantity,
        tl.unit,
        tl.vat_rate,
        tl.withholding_rate,
        tl.vat_base
    FROM transaction_lines tl
    JOIN accounts a ON tl.account_id = a.id
    WHERE tl.transaction_id = :transaction_id
    ORDER BY tl.id;
    """)
    
    lines = db.execute(query, {'transaction_id': transaction.id}).fetchall()
    
    print(f"\n📊 Toplam {len(lines)} satır")
    print()
    
    null_count = 0
    filled_count = 0
    
    for line in lines:
        print(f"Line ID {line[0]}: {line[1]} - {line[2]}")
        print(f"  Açıklama: {line[3]}")
        print(f"  Borç: {line[4]}, Alacak: {line[5]}")
        
        # quantity, unit kontrolü
        if line[6] is not None:
            print(f"  ✅ Miktar: {line[6]} {line[7] or ''}")
            filled_count += 1
        else:
            print(f"  ⚠️  Miktar: NULL (bazı satırlar için normal)")
            null_count += 1
        
        # vat_rate kontrolü
        if line[8] is not None:
            print(f"  ✅ KDV Oranı: {float(line[8]):.2%}")
            filled_count += 1
        else:
            print(f"  ⚠️  KDV Oranı: NULL (bazı satırlar için normal)")
            null_count += 1
        
        # vat_base kontrolü
        if line[10] is not None:
            print(f"  ✅ KDV Matrahı: {line[10]}")
            filled_count += 1
        else:
            print(f"  ⚠️  KDV Matrahı: NULL (bazı satırlar için normal)")
            null_count += 1
        
        print()
    
    print("=" * 80)
    print("ÖZET")
    print("=" * 80)
    
    # Kritik alanlar: transaction metadata
    critical_passed = (
        transaction.cost_center_id is not None and
        transaction.document_type_id is not None and
        transaction.document_subtype_id is not None
    )
    
    if critical_passed:
        print("✅ TRANSACTION METADATA: Tüm alanlar dolu!")
    else:
        print("❌ TRANSACTION METADATA: Bazı alanlar NULL!")
    
    # Kritik satırlar: Gider satırları quantity, vat_rate, vat_base olmalı
    # KDV satırı: vat_base olmalı, quantity NULL olabilir
    # Cari satırı: Hepsi NULL olabilir
    gider_lines = [l for l in lines if l[1].startswith('770') or l[1].startswith('689')]
    vat_lines = [l for l in lines if l[1].startswith('191')]
    
    gider_ok = all(l[6] is not None and l[8] is not None for l in gider_lines)  # quantity ve vat_rate
    vat_ok = all(l[10] is not None for l in vat_lines)  # vat_base
    
    if gider_ok:
        print("✅ GİDER SATIRLARI: quantity, vat_rate dolu!")
    else:
        print("❌ GİDER SATIRLARI: quantity veya vat_rate NULL!")
    
    if vat_ok:
        print("✅ KDV SATIRLARI: vat_base dolu!")
    else:
        print("❌ KDV SATIRLARI: vat_base NULL!")
    
    if critical_passed and gider_ok and vat_ok:
        print("\n🎉 TÜM KRİTİK ALANLAR DOLU! SORUN ÇÖZÜLDÜ!")
    else:
        print("\n⚠️  Bazı kritik alanlar hala NULL!")

except Exception as e:
    print(f"\n❌ HATA: {str(e)}")
    import traceback
    traceback.print_exc()
    db.rollback()

db.close()
