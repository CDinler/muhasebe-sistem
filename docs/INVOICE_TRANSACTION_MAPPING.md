# Fatura-Fiş İlişkilendirme Sistemi

## Mevcut Yapı

### 🔗 Junction Table: `invoice_transaction_mappings`

Fatura ve fiş arasındaki ilişkileri yöneten **many-to-many** junction table:

```sql
CREATE TABLE invoice_transaction_mappings (
    id INT PRIMARY KEY,
    einvoice_id INT REFERENCES einvoices(id),
    transaction_id INT REFERENCES transactions(id),
    document_number VARCHAR(100),  -- Cached invoice number
    mapping_type ENUM('auto', 'manual'),
    confidence_score DECIMAL(3,2),
    mapped_by INT REFERENCES users(id),
    mapped_at TIMESTAMP,
    notes TEXT
);
```

**Avantajları:**
- ✅ Bir faturaya birden fazla fiş bağlanabilir (örn: taksitli ödemeler)
- ✅ Bir fişe birden fazla fatura bağlanabilir (örn: toplu ödeme)
- ✅ Otomatik/manuel eşleştirme takibi
- ✅ Güven skoru ile eşleştirme kalitesi
- ✅ Kim ne zaman eşleştirdi bilgisi
- ✅ Transaction yeniden oluşturulursa ilişki korunur

## ⚠️ Deprecated Alan

### `transactions.related_invoice_number` 

**KULLANILMAYIN!** Bu alan artık kullanılmıyor:

```sql
-- DEPRECATED FIELD
transactions.related_invoice_number VARCHAR(100)  -- ❌ ESKİ YÖN
```

**Neden Kaldırılıyor:**
1. **Normalizasyon:** Junction table ile zaten ilişki kuruluyor
2. **Sınırlı:** Sadece 1-1 ilişki destekliyordu
3. **Senkronizasyon sorunu:** İki yerde aynı bilgi tutuyorduk
4. **Denormalize:** Veri tutarlılığı riski

**Ne Kullanmalı:**
```python
# ✅ DOĞRU YÖL - Junction table ile ilişki
from app.models.invoice_transaction_mapping import InvoiceTransactionMapping

# Fişin faturalarını bul
mappings = db.query(InvoiceTransactionMapping)\
    .filter(InvoiceTransactionMapping.transaction_id == transaction_id)\
    .all()

invoices = [mapping.einvoice for mapping in mappings]

# Faturanın fişlerini bul
mappings = db.query(InvoiceTransactionMapping)\
    .filter(InvoiceTransactionMapping.einvoice_id == invoice_id)\
    .all()

transactions = [mapping.transaction for mapping in mappings]
```

## Alan Tanımları

### `transactions.document_number`

Fişin **evrak numarası** - faturadan FARKLI:

- Dekont numarası
- Banka kayıt numarası
- Çek/senet numarası
- Tahsilat/tediye numarası

**Örnek:**
```
transaction.document_number = "DEKONT-2025-001"  # Ödeme dekontu
                                                  # ≠ Fatura numarası
```

### Fatura Numarası

Fatura numarası **junction table** üzerinden erişilir:

```python
# Fiş için ilişkili faturaları bul
transaction_mappings = transaction.invoice_mappings
invoice_numbers = [m.document_number for m in transaction_mappings]
# Örn: ["ABC2025000001", "ABC2025000002"]
```

## Migration Planı

### Faz 1: ✅ Deprecation (ŞU AN)
- Model'de DEPRECATED işaretlendi
- Frontend'den kaldırıldı
- Documentation eklendi

### Faz 2: 🔜 Data Migration
```sql
-- Mevcut related_invoice_number değerlerini kontrol et
SELECT COUNT(*) FROM transactions 
WHERE related_invoice_number IS NOT NULL;

-- Eğer varsa invoice_transaction_mappings'e taşı
```

### Faz 3: 🔜 Column Drop (6+ ay sonra)
```sql
-- FUTURE_remove_related_invoice_number.sql
ALTER TABLE transactions DROP COLUMN related_invoice_number;
```

## Best Practices

### ✅ Fatura-Fiş Eşleştirme

```python
from app.models.invoice_transaction_mapping import InvoiceTransactionMapping

# Otomatik eşleştirme
mapping = InvoiceTransactionMapping(
    einvoice_id=invoice.id,
    transaction_id=transaction.id,
    document_number=invoice.invoice_number,
    mapping_type='auto',
    confidence_score=0.95
)
db.add(mapping)
db.commit()

# Manuel eşleştirme
mapping = InvoiceTransactionMapping(
    einvoice_id=invoice.id,
    transaction_id=transaction.id,
    document_number=invoice.invoice_number,
    mapping_type='manual',
    confidence_score=1.00,
    mapped_by=current_user.id,
    notes='Kullanıcı tarafından manuel eşleştirildi'
)
db.add(mapping)
db.commit()
```

### ❌ Yapılmaması Gerekenler

```python
# ❌ YANLIŞ - related_invoice_number kullanma
transaction.related_invoice_number = "ABC2025000001"

# ❌ YANLIŞ - document_number'a fatura numarası yazma
transaction.document_number = "ABC2025000001"  # Bu evrak no için!
```

## Soru-Cevap

**S: Neden iki tane numara var?**
- `document_number` = Fişin evrak numarası (dekont, banka kaydı, vb.)
- Fatura numarası = `invoice_transaction_mappings` üzerinden ilişki

**S: Related invoice number neden boş?**
- Çünkü artık kullanılmıyor! Junction table kullanıyoruz.

**S: Fatura-fiş ilişkisini nasıl görürüm?**
- `invoice_transaction_mappings` tablosunu kullan

**S: Eski veriler kaybolacak mı?**
- Hayır, migration ile junction table'a aktarılacak
- Sonra deprecated alan kaldırılacak
