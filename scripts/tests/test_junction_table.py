"""Test junction table model and service"""

from app.core.database import SessionLocal
from app.models.invoice_transaction_mapping import InvoiceTransactionMapping
from app.services.invoice_mapping_service import get_mapping_stats, auto_match_by_document_number

db = SessionLocal()

print("JUNCTION TABLE MODEL TEST")
print("="*60)

# Test 1: Model import
print("✅ Model imported successfully")

# Test 2: İstatistikler
stats = get_mapping_stats(db)
print("\n📊 Mapping İstatistikleri:")
for key, value in stats.items():
    print(f"  {key}: {value}")

# Test 3: Mapping sayısı kontrolü
total_mappings = db.query(InvoiceTransactionMapping).count()
print(f"\n✅ Junction table'da {total_mappings} mapping var")

# Test 4: İlk 5 mapping'i göster
mappings = db.query(InvoiceTransactionMapping).limit(5).all()
print(f"\nİLK 5 MAPPING:")
print("="*60)
for m in mappings:
    print(f"ID: {m.id} | E-Invoice: {m.einvoice_id} | Transaction: {m.transaction_id}")
    print(f"  Doc: {m.document_number} | Type: {m.mapping_type} | Score: {m.confidence_score}")
    print()

db.close()
print("✅ Test başarılı!")
