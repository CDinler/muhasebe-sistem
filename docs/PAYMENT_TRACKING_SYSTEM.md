# Fatura Ödeme Takip Sistemi

## 🎯 Gereksinimler

1. **Ödeme Durumu Takibi**: Hangi faturalar ödendi, hangisi ödenmedi?
2. **Kısmi Ödeme**: Bir faturanın bir kısmı ödendi (örn: 10,000 TL faturadan 6,000 TL ödendi)
3. **Çoklu Ödeme**: Bir fatura birden fazla ödeme fişi ile ödenebilir (taksitli)
4. **Ödeme-Fiş İlişkisi**: Hangi fiş hangi faturaya ödeme yaptı?
5. **Rapor**: Ödenmeyen/gecikmiş faturalar listesi

---

## 📊 Mevcut Yapı

### `invoice_transaction_mappings` Tablosu

Zaten fatura-fiş ilişkisini tutuyor:

```sql
CREATE TABLE invoice_transaction_mappings (
    id INT PRIMARY KEY,
    einvoice_id INT,              -- Fatura
    transaction_id INT,           -- Fiş (ödeme fişi olabilir)
    document_number VARCHAR(100),
    mapping_type ENUM('auto', 'manual'),
    confidence_score DECIMAL(3,2),
    mapped_by INT,
    mapped_at TIMESTAMP,
    notes TEXT
);
```

**Problem:** Ödeme tutarı bilgisi YOK!

---

## ✅ Çözüm: Ödeme Tutarı Ekleme

### Migration: `payment_amount` Kolonu

```sql
-- 20260105_add_payment_tracking.sql

-- 1. payment_amount kolonu ekle
ALTER TABLE invoice_transaction_mappings
ADD COLUMN payment_amount DECIMAL(18,2) DEFAULT NULL 
COMMENT 'Bu fiş ile yapılan ödeme tutarı (NULL = ödeme değil, sadece ilişki)';

-- 2. payment_date kolonu ekle
ALTER TABLE invoice_transaction_mappings
ADD COLUMN payment_date DATE DEFAULT NULL
COMMENT 'Ödeme tarihi (transaction.transaction_date\'den cache)';

-- 3. Index ekle
CREATE INDEX idx_payment_amount ON invoice_transaction_mappings(payment_amount);
CREATE INDEX idx_payment_date ON invoice_transaction_mappings(payment_date);

-- 4. Mevcut verileri güncelle (transaction date'i cache'le)
UPDATE invoice_transaction_mappings m
JOIN transactions t ON m.transaction_id = t.id
SET m.payment_date = t.transaction_date
WHERE m.payment_amount IS NOT NULL;
```

---

## 🗃️ Fatura Modelinde Computed Fields

### Backend: `einvoice.py`

```python
from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func

class EInvoice(Base):
    __tablename__ = "einvoices"
    
    # ... existing fields ...
    
    payable_amount = Column(Numeric(18, 2), comment='Ödenecek tutar')
    
    @hybrid_property
    def paid_amount(self) -> Decimal:
        """
        Bu faturaya yapılan toplam ödeme tutarı
        invoice_transaction_mappings.payment_amount toplamı
        """
        from sqlalchemy.orm import object_session
        from app.models.invoice_transaction_mapping import InvoiceTransactionMapping
        
        session = object_session(self)
        if session:
            result = session.query(
                func.coalesce(func.sum(InvoiceTransactionMapping.payment_amount), 0)
            ).filter(
                InvoiceTransactionMapping.einvoice_id == self.id,
                InvoiceTransactionMapping.payment_amount.isnot(None)
            ).scalar()
            return result or Decimal('0.00')
        return Decimal('0.00')
    
    @hybrid_property
    def remaining_amount(self) -> Decimal:
        """Kalan ödeme tutarı"""
        return (self.payable_amount or Decimal('0.00')) - self.paid_amount
    
    @hybrid_property
    def payment_status(self) -> str:
        """
        Ödeme durumu:
        - UNPAID: Hiç ödeme yapılmamış
        - PARTIALLY_PAID: Kısmi ödeme yapılmış
        - PAID: Tam ödendi
        - OVERPAID: Fazla ödeme yapılmış
        """
        if not self.payable_amount:
            return 'UNKNOWN'
        
        paid = self.paid_amount
        total = self.payable_amount
        
        if paid == 0:
            return 'UNPAID'
        elif paid < total:
            return 'PARTIALLY_PAID'
        elif paid == total:
            return 'PAID'
        else:
            return 'OVERPAID'
    
    @hybrid_property
    def payment_percentage(self) -> float:
        """Ödeme yüzdesi (0-100)"""
        if not self.payable_amount or self.payable_amount == 0:
            return 0.0
        return float((self.paid_amount / self.payable_amount) * 100)
```

---

## 🔄 Mapping Model Güncellemesi

### `invoice_transaction_mapping.py`

```python
class InvoiceTransactionMapping(Base):
    __tablename__ = "invoice_transaction_mappings"
    
    id = Column(Integer, primary_key=True)
    einvoice_id = Column(Integer, ForeignKey('einvoices.id'))
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    document_number = Column(String(100))
    
    # ÖDEME BİLGİLERİ
    payment_amount = Column(Numeric(18, 2), nullable=True,
                           comment='Bu fiş ile yapılan ödeme tutarı')
    payment_date = Column(Date, nullable=True,
                         comment='Ödeme tarihi (cached from transaction)')
    
    # Metadata
    mapping_type = Column(Enum('auto', 'manual', name='mapping_type_enum'))
    confidence_score = Column(Numeric(3, 2))
    mapped_by = Column(Integer, ForeignKey('users.id'))
    mapped_at = Column(TIMESTAMP, server_default=func.now())
    notes = Column(Text)
    
    # İlişkiler
    einvoice = relationship("EInvoice", backref="transaction_mappings")
    transaction = relationship("Transaction", backref="invoice_mappings")
```

---

## 💡 Kullanım Senaryoları

### Senaryo 1: Tam Ödeme

```python
# Fatura: 10,000 TL
# Ödeme fişi: 10,000 TL

mapping = InvoiceTransactionMapping(
    einvoice_id=invoice.id,
    transaction_id=payment_transaction.id,
    document_number=invoice.invoice_number,
    payment_amount=Decimal('10000.00'),  # TAM ÖDEME
    payment_date=payment_transaction.transaction_date,
    mapping_type='manual',
    confidence_score=1.00,
    mapped_by=current_user.id,
    notes='Tam ödeme - banka havalesi'
)

db.add(mapping)
db.commit()

# Sonuç:
invoice.paid_amount        # 10,000.00
invoice.remaining_amount   # 0.00
invoice.payment_status     # 'PAID'
invoice.payment_percentage # 100.0
```

### Senaryo 2: Kısmi Ödeme

```python
# Fatura: 10,000 TL
# 1. Ödeme: 4,000 TL
# 2. Ödeme: 3,000 TL
# Kalan: 3,000 TL

# 1. ödeme
mapping1 = InvoiceTransactionMapping(
    einvoice_id=invoice.id,
    transaction_id=payment1.id,
    payment_amount=Decimal('4000.00'),
    payment_date=date(2026, 1, 5),
    notes='1. taksit'
)
db.add(mapping1)

# 2. ödeme
mapping2 = InvoiceTransactionMapping(
    einvoice_id=invoice.id,
    transaction_id=payment2.id,
    payment_amount=Decimal('3000.00'),
    payment_date=date(2026, 2, 5),
    notes='2. taksit'
)
db.add(mapping2)

db.commit()

# Sonuç:
invoice.paid_amount        # 7,000.00
invoice.remaining_amount   # 3,000.00
invoice.payment_status     # 'PARTIALLY_PAID'
invoice.payment_percentage # 70.0
```

### Senaryo 3: Toplu Ödeme (Bir Fiş, Birden Fazla Fatura)

```python
# 1 ödeme fişi ile 3 fatura ödeniyor
# Fatura A: 5,000 TL
# Fatura B: 3,000 TL
# Fatura C: 2,000 TL
# Toplam ödeme: 10,000 TL

payment_transaction = Transaction(...)  # 10,000 TL ödeme fişi

# Her faturaya kendi tutarını eşleştir
for invoice, amount in [(invoice_a, 5000), (invoice_b, 3000), (invoice_c, 2000)]:
    mapping = InvoiceTransactionMapping(
        einvoice_id=invoice.id,
        transaction_id=payment_transaction.id,
        payment_amount=Decimal(str(amount)),
        notes=f'Toplu ödeme - {invoice.invoice_number}'
    )
    db.add(mapping)
```

### Senaryo 4: Sadece İlişkilendirme (Ödeme Değil)

```python
# Faturanın muhasebe kaydı yapılmış ama henüz ödeme yok
# mapping_type için payment_amount = NULL

mapping = InvoiceTransactionMapping(
    einvoice_id=invoice.id,
    transaction_id=accounting_entry.id,
    payment_amount=None,  # ÖDEME YOK, sadece muhasebe ilişkisi
    mapping_type='auto',
    notes='Alış faturası muhasebe kaydı'
)

# Sonuç:
invoice.paid_amount        # 0.00 (NULL değerler sayılmaz)
invoice.payment_status     # 'UNPAID'
```

---

## 📋 API Endpoints

### 1. Fatura Ödeme Durumu

```python
# GET /api/v1/einvoices/{id}/payment-status
@router.get("/{id}/payment-status")
def get_payment_status(id: int, db: Session = Depends(get_db)):
    invoice = db.query(EInvoice).filter(EInvoice.id == id).first()
    
    return {
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "total_amount": invoice.payable_amount,
        "paid_amount": invoice.paid_amount,
        "remaining_amount": invoice.remaining_amount,
        "payment_status": invoice.payment_status,
        "payment_percentage": invoice.payment_percentage,
        "payments": [
            {
                "transaction_id": m.transaction_id,
                "transaction_number": m.transaction.transaction_number,
                "amount": m.payment_amount,
                "date": m.payment_date,
                "notes": m.notes
            }
            for m in invoice.transaction_mappings
            if m.payment_amount is not None
        ]
    }
```

### 2. Ödenmeyen Faturalar Listesi

```python
# GET /api/v1/einvoices/unpaid
@router.get("/unpaid")
def get_unpaid_invoices(
    status: str = Query('UNPAID', regex='^(UNPAID|PARTIALLY_PAID)$'),
    days_overdue: int = Query(None, ge=0),
    db: Session = Depends(get_db)
):
    """
    Ödenmeyen/kısmen ödenen faturaları listele
    
    Args:
        status: UNPAID (hiç ödenmemiş) veya PARTIALLY_PAID (kısmen ödenmiş)
        days_overdue: Vadesi geçmiş (örn: 30 gün üzeri)
    """
    invoices = db.query(EInvoice).all()
    
    results = []
    for inv in invoices:
        if inv.payment_status == status:
            overdue_days = None
            if inv.issue_date:
                overdue_days = (date.today() - inv.issue_date).days
            
            if days_overdue is None or (overdue_days and overdue_days >= days_overdue):
                results.append({
                    "id": inv.id,
                    "invoice_number": inv.invoice_number,
                    "supplier_name": inv.supplier_name,
                    "issue_date": inv.issue_date,
                    "total_amount": inv.payable_amount,
                    "paid_amount": inv.paid_amount,
                    "remaining_amount": inv.remaining_amount,
                    "payment_percentage": inv.payment_percentage,
                    "days_overdue": overdue_days
                })
    
    return {
        "total": len(results),
        "items": sorted(results, key=lambda x: x['days_overdue'] or 0, reverse=True)
    }
```

### 3. Ödeme Kaydet

```python
# POST /api/v1/einvoices/{id}/payments
@router.post("/{id}/payments")
def record_payment(
    id: int,
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Faturaya ödeme kaydet
    
    Request:
        {
            "transaction_id": 12345,
            "payment_amount": 5000.00,
            "payment_date": "2026-01-05",
            "notes": "1. taksit ödeme"
        }
    """
    invoice = db.query(EInvoice).filter(EInvoice.id == id).first()
    transaction = db.query(Transaction).filter(Transaction.id == payment.transaction_id).first()
    
    # Ödeme tutarı kontrolü
    if payment.payment_amount > invoice.remaining_amount:
        raise HTTPException(400, f"Ödeme tutarı kalan tutardan fazla: {invoice.remaining_amount}")
    
    # Mapping oluştur
    mapping = InvoiceTransactionMapping(
        einvoice_id=invoice.id,
        transaction_id=transaction.id,
        document_number=invoice.invoice_number,
        payment_amount=payment.payment_amount,
        payment_date=payment.payment_date or transaction.transaction_date,
        mapping_type='manual',
        confidence_score=1.00,
        mapped_by=current_user.id,
        notes=payment.notes
    )
    
    db.add(mapping)
    db.commit()
    
    return {
        "message": "Ödeme kaydedildi",
        "invoice_id": invoice.id,
        "payment_id": mapping.id,
        "new_status": invoice.payment_status,
        "remaining": invoice.remaining_amount
    }
```

---

## 📊 Raporlar

### 1. Yaşlandırma Raporu (Aging Report)

```python
# GET /api/v1/reports/aging
def get_aging_report(db: Session = Depends(get_db)):
    """
    Fatura yaşlandırma raporu
    0-30 gün, 31-60 gün, 61-90 gün, 90+ gün
    """
    today = date.today()
    invoices = db.query(EInvoice).filter(
        EInvoice.invoice_category == 'incoming'  # Alış faturaları
    ).all()
    
    aging = {
        "0-30": {"count": 0, "amount": Decimal('0.00')},
        "31-60": {"count": 0, "amount": Decimal('0.00')},
        "61-90": {"count": 0, "amount": Decimal('0.00')},
        "90+": {"count": 0, "amount": Decimal('0.00')}
    }
    
    for inv in invoices:
        if inv.payment_status in ['UNPAID', 'PARTIALLY_PAID']:
            days = (today - inv.issue_date).days
            remaining = inv.remaining_amount
            
            if days <= 30:
                aging["0-30"]["count"] += 1
                aging["0-30"]["amount"] += remaining
            elif days <= 60:
                aging["31-60"]["count"] += 1
                aging["31-60"]["amount"] += remaining
            elif days <= 90:
                aging["61-90"]["count"] += 1
                aging["61-90"]["amount"] += remaining
            else:
                aging["90+"]["count"] += 1
                aging["90+"]["amount"] += remaining
    
    return aging
```

### 2. Tedarikçi Bazlı Bakiye

```python
# GET /api/v1/reports/supplier-balance
def get_supplier_balance(db: Session = Depends(get_db)):
    """Tedarikçi bazında ödeme durumu"""
    from sqlalchemy import func
    
    results = db.query(
        EInvoice.supplier_name,
        EInvoice.supplier_tax_number,
        func.count(EInvoice.id).label('invoice_count'),
        func.sum(EInvoice.payable_amount).label('total_amount')
    ).filter(
        EInvoice.invoice_category == 'incoming'
    ).group_by(
        EInvoice.supplier_name,
        EInvoice.supplier_tax_number
    ).all()
    
    suppliers = []
    for r in results:
        # Her tedarikçinin faturalarını kontrol et
        invoices = db.query(EInvoice).filter(
            EInvoice.supplier_tax_number == r.supplier_tax_number
        ).all()
        
        total_paid = sum(inv.paid_amount for inv in invoices)
        total_remaining = sum(inv.remaining_amount for inv in invoices)
        
        suppliers.append({
            "supplier_name": r.supplier_name,
            "tax_number": r.supplier_tax_number,
            "invoice_count": r.invoice_count,
            "total_amount": r.total_amount,
            "paid_amount": total_paid,
            "remaining_amount": total_remaining
        })
    
    return sorted(suppliers, key=lambda x: x['remaining_amount'], reverse=True)
```

---

## 🎨 Frontend

### Fatura Detay Sayfası - Ödeme Takibi

```tsx
// EInvoiceDetailPage.tsx
import { Progress, Tag, Table, Button } from 'antd';

const PaymentSection: React.FC<{ invoice: EInvoice }> = ({ invoice }) => {
  const statusColor = {
    'UNPAID': 'red',
    'PARTIALLY_PAID': 'orange',
    'PAID': 'green',
    'OVERPAID': 'purple'
  };
  
  return (
    <Card title="Ödeme Durumu">
      <Descriptions column={2}>
        <Descriptions.Item label="Toplam Tutar">
          {invoice.payable_amount?.toFixed(2)} TL
        </Descriptions.Item>
        <Descriptions.Item label="Ödenen">
          {invoice.paid_amount?.toFixed(2)} TL
        </Descriptions.Item>
        <Descriptions.Item label="Kalan">
          <span style={{ color: 'red', fontWeight: 'bold' }}>
            {invoice.remaining_amount?.toFixed(2)} TL
          </span>
        </Descriptions.Item>
        <Descriptions.Item label="Durum">
          <Tag color={statusColor[invoice.payment_status]}>
            {invoice.payment_status}
          </Tag>
        </Descriptions.Item>
      </Descriptions>
      
      <div style={{ marginTop: 16 }}>
        <Progress 
          percent={invoice.payment_percentage} 
          status={invoice.payment_status === 'PAID' ? 'success' : 'active'}
        />
      </div>
      
      <Divider>Ödeme Geçmişi</Divider>
      
      <Table
        dataSource={invoice.payments}
        columns={[
          { title: 'Fiş No', dataIndex: 'transaction_number' },
          { title: 'Tarih', dataIndex: 'payment_date', render: d => dayjs(d).format('DD.MM.YYYY') },
          { title: 'Tutar', dataIndex: 'payment_amount', render: v => `${v.toFixed(2)} TL` },
          { title: 'Not', dataIndex: 'notes' }
        ]}
      />
      
      <Button 
        type="primary" 
        onClick={() => openPaymentModal(invoice.id)}
        disabled={invoice.payment_status === 'PAID'}
      >
        Ödeme Kaydet
      </Button>
    </Card>
  );
};
```

### Ödenmeyen Faturalar Sayfası

```tsx
// UnpaidInvoicesPage.tsx
const UnpaidInvoicesPage: React.FC = () => {
  const { data: unpaid } = useQuery(['unpaid-invoices'], () =>
    apiClient.get('/einvoices/unpaid?status=UNPAID')
  );
  
  return (
    <Table
      dataSource={unpaid?.items}
      columns={[
        { title: 'Fatura No', dataIndex: 'invoice_number' },
        { title: 'Tedarikçi', dataIndex: 'supplier_name' },
        { title: 'Tarih', dataIndex: 'issue_date' },
        { 
          title: 'Gecikme', 
          dataIndex: 'days_overdue',
          render: (days) => days > 30 ? <Tag color="red">{days} gün</Tag> : <Tag>{days} gün</Tag>
        },
        { title: 'Tutar', dataIndex: 'total_amount', render: v => `${v.toFixed(2)} TL` },
        { title: 'Ödenen', dataIndex: 'paid_amount', render: v => `${v.toFixed(2)} TL` },
        { 
          title: 'Kalan', 
          dataIndex: 'remaining_amount',
          render: v => <span style={{color: 'red', fontWeight: 'bold'}}>{v.toFixed(2)} TL</span>
        }
      ]}
    />
  );
};
```

---

## 🚀 Implementation Checklist

### Faz 1: Database
- [ ] Migration dosyası oluştur (`payment_amount`, `payment_date` kolonları)
- [ ] Migration'ı çalıştır
- [ ] Index'leri ekle

### Faz 2: Backend Models
- [ ] `InvoiceTransactionMapping` modelini güncelle
- [ ] `EInvoice` modelinde computed properties ekle
- [ ] Unit test'ler yaz

### Faz 3: API Endpoints
- [ ] Payment status endpoint
- [ ] Unpaid invoices endpoint
- [ ] Record payment endpoint
- [ ] Aging report endpoint
- [ ] Supplier balance endpoint

### Faz 4: Frontend
- [ ] Payment tracking components
- [ ] Unpaid invoices page
- [ ] Payment modal
- [ ] Aging report page

### Faz 5: Testing
- [ ] Full payment scenario test
- [ ] Partial payment scenario test
- [ ] Multiple payments scenario test
- [ ] Report accuracy test

---

## 📝 Özet

**Çözüm:**
1. ✅ `invoice_transaction_mappings` tablosuna `payment_amount` ve `payment_date` ekliyoruz
2. ✅ Fatura modelinde computed fields ile ödeme durumunu hesaplıyoruz
3. ✅ NULL `payment_amount` = sadece ilişki, ödeme değil
4. ✅ Birden fazla mapping ile taksitli/kısmi ödeme destekleniyor
5. ✅ Ödenmeyen faturalar için raporlar ve API'ler

**Avantajlar:**
- Many-to-many ilişki korunuyor
- Kısmi ödemeler takip ediliyor
- Taksitli ödemeler destekleniyor
- Ödeme geçmişi saklanıyor
- Muhasebe ilişkisi ile ödeme ilişkisi ayrılıyor
