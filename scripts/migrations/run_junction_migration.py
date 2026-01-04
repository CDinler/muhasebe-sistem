from app.core.database import SessionLocal
from sqlalchemy import text
import os

db = SessionLocal()

print("JUNCTION TABLE OLUŞTURMA VE VERİ MİGRASYONU")
print("="*60)

# Migration dosyasını oku ve çalıştır
migration_file = r"C:\Projects\muhasebe-sistem\database\migrations\20251224_create_invoice_transaction_mappings.sql"

with open(migration_file, 'r', encoding='utf-8') as f:
    sql_content = f.read()

# SQL komutlarını ayır (-- ile başlayan comment'ler ve boş satırları atla)
statements = []
current_statement = []

for line in sql_content.split('\n'):
    line = line.strip()
    if not line or line.startswith('--'):
        continue
    current_statement.append(line)
    if line.endswith(';'):
        statements.append(' '.join(current_statement))
        current_statement = []

print(f"Toplam {len(statements)} SQL komutu bulundu")
print()

# Her statement'i ayrı ayrı çalıştır
for i, stmt in enumerate(statements, 1):
    try:
        # Sadece ilk 100 karakteri göster
        preview = stmt[:100].replace('\n', ' ')
        print(f"{i}. {preview}...")
        
        result = db.execute(text(stmt))
        
        if "INSERT INTO invoice_transaction_mappings" in stmt:
            print(f"   ✅ {result.rowcount} kayıt migrate edildi")
        else:
            print(f"   ✅ Başarılı")
            
    except Exception as e:
        print(f"   ❌ Hata: {e}")
        break

db.commit()

# Kontrol
stats = db.execute(text("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN mapping_type = 'auto' THEN 1 ELSE 0 END) as auto_mapped,
        SUM(CASE WHEN mapping_type = 'manual' THEN 1 ELSE 0 END) as manual_mapped
    FROM invoice_transaction_mappings
""")).fetchone()

print()
print("="*60)
print("SONUÇ:")
print(f"  Toplam mapping: {stats.total}")
print(f"  Otomatik: {stats.auto_mapped}")
print(f"  Manuel: {stats.manual_mapped}")

db.close()
