# 🏗️ PERSONEL SİSTEMİ - Mimari Tasarım

## 📐 SİSTEM ARŞİTEKTÜRÜ

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                          │
├─────────────────────────────────────────────────────────────────┤
│  PersonnelPage        │  LucaBordroPage  │  BordroCalculationPage│
│  - Liste/Filtre       │  - Excel Upload  │  - Hesaplama          │
│  - CRUD İşlemleri     │  - Import        │  - Doğrulama          │
│  - İstatistikler      │  - Validation    │  - Onay               │
└──────────────┬────────────────────┬────────────────────┬─────────┘
               │                    │                    │
               │ HTTP REST API      │                    │
               │                    │                    │
┌──────────────┴────────────────────┴────────────────────┴─────────┐
│                      BACKEND (FastAPI)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │ Personnel API   │  │ Luca Bordro API  │  │ Yevmiye API     │ │
│  │ /personnel/     │  │ /luca-bordro/    │  │ /bordro-yevmiye/│ │
│  │                 │  │                  │  │                 │ │
│  │ • List          │  │ • Upload Excel   │  │ • Generate      │ │
│  │ • Create        │  │ • Parse & Save   │  │ • Validate      │ │
│  │ • Update        │  │ • Match TC       │  │ • Export CSV    │ │
│  │ • Delete        │  │ • Validate       │  │                 │ │
│  │ • Filters       │  │                  │  │                 │ │
│  └────────┬────────┘  └────────┬─────────┘  └────────┬────────┘ │
│           │                    │                     │           │
│           └────────────────────┴─────────────────────┘           │
│                              │                                   │
│                    ┌─────────┴──────────┐                        │
│                    │   CRUD Layer       │                        │
│                    │   Business Logic   │                        │
│                    └─────────┬──────────┘                        │
│                              │                                   │
│                    ┌─────────┴──────────┐                        │
│                    │  SQLAlchemy ORM    │                        │
│                    └─────────┬──────────┘                        │
└──────────────────────────────┼────────────────────────────────────┘
                               │
┌──────────────────────────────┴────────────────────────────────────┐
│                    DATABASE (MySQL/MariaDB)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │ personnel   │  │personnel_contracts│ │payroll_calculations│  │
│  │             │  │                  │  │                  │   │
│  │ id (PK)     │  │ id (PK)          │  │ id (PK)          │   │
│  │ code        │  │ personnel_id (FK)│  │ personnel_id (FK)│   │
│  │ tckn        │  │ ise_giris_tarihi │  │ donem            │   │
│  │ first_name  │  │ isten_cikis_...  │  │ tckn             │   │
│  │ last_name   │  │ ucret_nevi       │  │ adi_soyadi       │   │
│  │ department  │  │ maas1_tutar      │  │ maas1_net_odenen │   │
│  │ start_date  │  │ cost_center_id   │  │ maas1_ssk_isci   │   │
│  │ end_date    │  │ ...              │  │ maas1_ssk_isveren│   │
│  │ account_id ─┼─┐│                  │  │ ...              │   │
│  │ ...         │ ││                  │  │ yevmiye_created  │   │
│  └─────────────┘ ││                  │  │ ...              │   │
│                  ││                  │  └──────────────────┘   │
│  ┌───────────────┘│                  │                         │
│  │               └┐                  │                         │
│  ▼                ▼                  ▼                         │
│  ┌─────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │ accounts    │  │ cost_centers     │  │ transactions     │   │
│  │             │  │                  │  │                  │   │
│  │ id (PK)     │  │ id (PK)          │  │ id (PK)          │   │
│  │ code        │  │ code             │  │ transaction_no   │   │
│  │ name        │  │ name             │  │ document_type    │   │
│  │ (335.xxx)   │  │ (ŞANT-001)       │  │ donem            │   │
│  └─────────────┘  └──────────────────┘  │ ...              │   │
│                                         └─────────┬──────────┘   │
│                                                   │              │
│                                         ┌─────────┴──────────┐   │
│                                         │ transaction_lines  │   │
│                                         │                    │   │
│                                         │ id (PK)            │   │
│                                         │ transaction_id (FK)│   │
│                                         │ account_id (FK)    │   │
│                                         │ debit              │   │
│                                         │ credit             │   │
│                                         │ description        │   │
│                                         └────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 VERİ AKIŞ DİYAGRAMI

### 1. Personel Ekleme/Güncelleme

```
┌──────────────┐
│   FRONTEND   │
│ PersonnelPage│
└──────┬───────┘
       │ 1. Form Submit
       │ POST /api/v1/personnel/
       ▼
┌──────────────────┐
│   BACKEND API    │
│ personnel.py     │
│                  │
│ 2. Validation    │
│ 3. Check TCKN    │
│ 4. Create Model  │
└──────┬───────────┘
       │ 5. Save to DB
       ▼
┌──────────────────┐
│    DATABASE      │
│ INSERT personnel │
│                  │
│ 6. Generate ID   │
│ 7. account_id=NULL
└──────┬───────────┘
       │ 8. Return with ID
       ▼
┌──────────────────┐
│   BACKEND API    │
│                  │
│ 9. Create Account│
│    335.{tckn}    │
└──────┬───────────┘
       │ 10. Link account_id
       ▼
┌──────────────────┐
│    DATABASE      │
│ UPDATE personnel │
│ SET account_id=X │
└──────┬───────────┘
       │ 11. Success Response
       ▼
┌──────────────────┐
│   FRONTEND       │
│ Refresh List     │
└──────────────────┘
```

### 2. Luca Bordro Import

```
┌──────────────────┐
│    FRONTEND      │
│ LucaBordroPage   │
│                  │
│ 1. Select Excel  │
│ 2. Upload        │
└──────┬───────────┘
       │ POST /luca-bordro/upload
       │ (multipart/form-data)
       ▼
┌──────────────────────────┐
│      BACKEND API         │
│ luca_bordro.py           │
│                          │
│ 3. Parse Excel (pandas)  │
│ 4. Validate Columns      │
│ 5. Check Required Fields │
└──────┬───────────────────┘
       │ For Each Row:
       ▼
┌──────────────────────────┐
│   PERSONNEL MATCHING     │
│                          │
│ 6. Find by TCKN          │
│    personnel = query(    │
│      Personnel           │
│    ).filter(             │
│      tckn == row['TC']   │
│    ).first()             │
└──────┬───────────────────┘
       │
       ├─ FOUND ────────────────────┐
       │                            │
       ▼                            ▼
┌────────────────┐        ┌──────────────────┐
│ GET PERSONNEL  │        │  PERSONNEL NOT   │
│ ID             │        │  FOUND           │
│                │        │                  │
│ personnel_id = │        │ → Error/Warning  │
│ personnel.id   │        │ → Skip or Create │
└────────┬───────┘        └──────────────────┘
         │
         ▼
┌──────────────────────────────┐
│   CONTRACT MATCHING          │
│                              │
│ 7. Find active contract      │
│    by date range:            │
│    ise_giris <= bordro_date  │
│    AND (isten_cikis IS NULL  │
│         OR isten_cikis >= ..)│
└──────┬───────────────────────┘
       │
       ├─ CONTRACT FOUND ──┐
       │                   │
       ▼                   ▼
┌────────────────┐  ┌────────────────┐
│ USE CONTRACT   │  │ NO CONTRACT    │
│ ucret_nevi     │  │ contract_id=NULL
│ cost_center_id │  │ ucret_nevi=NULL│
│ account_code   │  │                │
└────────┬───────┘  └────────┬───────┘
         │                   │
         └─────────┬─────────┘
                   ▼
         ┌──────────────────────────┐
         │ CREATE PAYROLL_CALCULATION│
         │                          │
         │ INSERT INTO              │
         │ payroll_calculations     │
         │ (personnel_id,           │
         │  contract_id,            │
         │  donem,                  │
         │  maas1_net_odenen,       │
         │  maas1_ssk_isci,         │
         │  maas1_ssk_isveren,      │
         │  ...)                    │
         └──────┬───────────────────┘
                │
                ▼
         ┌──────────────────────────┐
         │    SAVE TO DATABASE      │
         │                          │
         │ db.add(payroll_calc)     │
         │ db.commit()              │
         └──────┬───────────────────┘
                │
                ▼
         ┌──────────────────────────┐
         │   RETURN RESULTS         │
         │                          │
         │ {                        │
         │   success: true,         │
         │   total: 369,            │
         │   inserted: 369,         │
         │   errors: []             │
         │ }                        │
         └──────┬───────────────────┘
                │
                ▼
         ┌──────────────────────────┐
         │      FRONTEND            │
         │ Show Success Message     │
         │ Navigate to Calculation  │
         └──────────────────────────┘
```

### 3. Bordro Yevmiye Oluşturma

```
┌──────────────────────┐
│     FRONTEND         │
│ BordroCalculationPage│
│                      │
│ 1. Select Period     │
│    "2025-12"         │
│ 2. Click Generate    │
└──────┬───────────────┘
       │ POST /bordro-yevmiye-v2/generate
       │ {donem: "2025-12"}
       ▼
┌────────────────────────────────┐
│        BACKEND API             │
│ bordro_yevmiye_v2.py           │
│                                │
│ 3. Get Payroll Calculations    │
│    WHERE donem = "2025-12"     │
│    AND yevmiye_created = FALSE │
└──────┬─────────────────────────┘
       │ For Each Payroll:
       ▼
┌────────────────────────────────┐
│   GET PERSONNEL & ACCOUNT      │
│                                │
│ 4. personnel = get(personnel_id)│
│                                │
│ 5. account = OPTIMIZED:        │
│    if personnel.account_id:    │
│       account = get(account_id)│ ← FAST (PK lookup)
│    else:                       │
│       account = query(Account) │
│         .filter(               │
│           code = '335.'+tckn   │
│         ).first()              │ ← SLOW (CONCAT)
│                                │
│ 6. Link account_id if missing  │
│    personnel.account_id = id   │
└──────┬─────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│   GET OTHER ACCOUNTS           │
│                                │
│ 7. acc_740 = get_by_code(      │
│       "740.00100")             │
│    acc_361_ssk = get_by_code(  │
│       "361.00001")             │
│    acc_360_gelir = get_by_code(│
│       "360.00004")             │
│    ... (10+ hesap)             │
└──────┬─────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│   CREATE TRANSACTION           │
│                                │
│ 8. transaction = Transaction(  │
│      transaction_number =      │
│        get_next_fis_no(),      │
│      accounting_period = donem,│
│      document_type = "BORDRO", │
│      description = "..."       │
│    )                           │
│                                │
│ 9. db.add(transaction)         │
│    db.flush() → Get ID         │
└──────┬─────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│   CREATE TRANSACTION LINES          │
│                                     │
│ 10. For Each Payroll Item:          │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ BORÇ: 740.00100                 │ │
│ ├─────────────────────────────────┤ │
│ │ • Net Ödenen     (if > 0)       │ │
│ │ • İşçi SSK       (if > 0)       │ │
│ │ • İşveren SSK    (if > 0)       │ │
│ │ • İşçi İşsizlik  (if > 0)       │ │
│ │ • İşveren İşsizlik (if > 0)     │ │
│ │ • Gelir Vergisi  (if > 0)       │ │
│ │ • Damga Vergisi  (if > 0)       │ │
│ │ • BES            (if > 0)       │ │
│ │ • İcra           (if > 0)       │ │
│ │ • Avans          (if > 0)       │ │
│ │ • Yıllık Ücretli İzinler (if > 0)│ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ ALACAK                          │ │
│ ├─────────────────────────────────┤ │
│ │ • 335.{tckn}  (Net Ödenen)      │ │
│ │ • 361.00001   (İşçi SSK)        │ │
│ │ • 361.00002   (İşveren SSK)     │ │
│ │ • 361.00003   (İşçi İşsizlik)   │ │
│ │ • 361.00004   (İşveren İşsizlik)│ │
│ │ • 360.00004   (Gelir Vergisi)   │ │
│ │ • 360.00005   (Damga Vergisi)   │ │
│ │ • 369.00001   (BES)             │ │
│ │ • 369.00002   (İcra)            │ │
│ │ • 196         (Avans)           │ │
│ └─────────────────────────────────┘ │
│                                     │
│ 11. For each line:                  │
│     line = TransactionLine(         │
│       transaction_id = trans.id,    │
│       account_id = account.id,      │
│       debit = amount,               │
│       credit = 0,                   │
│       description = "..."           │
│     )                               │
│     db.add(line)                    │
└──────┬──────────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│   VALIDATE BALANCE             │
│                                │
│ 12. total_debit = sum(debit)   │
│     total_credit = sum(credit) │
│                                │
│ 13. if debit != credit:        │
│       raise Error              │
└──────┬─────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│   MARK AS COMPLETED            │
│                                │
│ 14. payroll.yevmiye_created    │
│       = TRUE                   │
│                                │
│ 15. db.commit()                │
└──────┬─────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│   RETURN RESPONSE              │
│                                │
│ 16. {                          │
│       success: true,           │
│       personnel_count: 369,    │
│       transaction_count: 369,  │
│       total_lines: 4428,       │
│       total_debit: 9250000.50, │
│       total_credit: 9250000.50,│
│       errors: []               │
│     }                          │
└──────┬─────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│      FRONTEND                  │
│ Show Success                   │
│ Refresh List                   │
│ Show Statistics                │
└────────────────────────────────┘
```

---

## 🗂️ MODÜL YAPISI

```
backend/
├── app/
│   ├── models/
│   │   ├── personnel.py                    ← Personel modeli
│   │   ├── personnel_contract.py           ← Sözleşme modeli
│   │   ├── payroll_calculation.py          ← Bordro hesaplama
│   │   ├── monthly_puantaj.py              ← Puantaj
│   │   ├── account.py                      ← Hesap planı
│   │   ├── transaction.py                  ← Muhasebe fişi
│   │   └── transaction_line.py             ← Fiş satırları
│   │
│   ├── schemas/
│   │   ├── personnel.py                    ← Pydantic schemas
│   │   ├── payroll.py
│   │   └── transaction.py
│   │
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── personnel.py            ← Personnel CRUD API
│   │           ├── personnel_contracts.py  ← Contract API
│   │           ├── luca_bordro.py          ← Luca import API
│   │           ├── bordro_calculation.py   ← Bordro hesaplama
│   │           ├── bordro_yevmiye_v2.py    ← Yevmiye generation
│   │           └── puantaj.py              ← Puantaj API
│   │
│   ├── crud/
│   │   ├── personnel.py                    ← DB operations
│   │   ├── payroll.py
│   │   └── transaction.py
│   │
│   ├── services/
│   │   ├── bordro_service.py               ← Business logic
│   │   ├── yevmiye_service.py
│   │   └── excel_parser.py                 ← Luca Excel parser
│   │
│   └── utils/
│       ├── transaction_numbering.py        ← Fiş no generator
│       ├── date_helpers.py
│       └── validators.py
│
└── templates/
    └── yevmiye_kayit_sablonu.csv           ← Export template

frontend/
└── src/
    ├── pages/
    │   ├── PersonnelPage.tsx               ← Personel listesi
    │   ├── PersonnelContractsPage.tsx      ← Sözleşme yönetimi
    │   ├── LucaBordroPage.tsx              ← Luca bordro upload
    │   ├── BordroCalculationPage.tsx       ← Bordro hesaplama
    │   └── YevmiyeExportPage.tsx           ← Yevmiye export
    │
    ├── components/
    │   ├── personnel/
    │   │   ├── PersonnelForm.tsx
    │   │   ├── PersonnelTable.tsx
    │   │   └── PersonnelStats.tsx
    │   │
    │   ├── bordro/
    │   │   ├── BordroUpload.tsx
    │   │   ├── BordroTable.tsx
    │   │   └── BordroStats.tsx
    │   │
    │   └── yevmiye/
    │       ├── YevmiyePreview.tsx
    │       └── YevmiyeExport.tsx
    │
    └── services/
        ├── personnelApi.ts
        ├── bordroApi.ts
        └── yevmiyeApi.ts
```

---

## 🔐 GÜVENLİK VE PERFORMANS

### Güvenlik Önlemleri

1. **SQL Injection Koruması**
   ```python
   # ✅ GÜVENLİ (ORM kullanımı)
   query = db.query(Personnel).filter(Personnel.tckn == tckn)
   
   # ❌ TEHLİKELİ (direkt SQL)
   query = f"SELECT * FROM personnel WHERE tckn = '{tckn}'"
   ```

2. **Veri Validasyonu**
   ```python
   class PersonnelCreate(BaseModel):
       tckn: str = Field(..., min_length=11, max_length=11)
       
       @validator('tckn')
       def validate_tckn(cls, v):
           if not v.isdigit():
               raise ValueError('TC sadece rakam içermeli')
           return v
   ```

3. **Authentication & Authorization**
   ```python
   @router.get("/personnel/")
   def get_personnel(
       current_user: User = Depends(get_current_active_user),
       db: Session = Depends(get_db)
   ):
       if not current_user.has_permission("view_personnel"):
           raise HTTPException(403, "Yetkisiz erişim")
   ```

### Performans Optimizasyonları

1. **Database İndeksler**
   ```sql
   -- Sık kullanılan sorgular için
   CREATE INDEX idx_personnel_tckn ON personnel(tckn);
   CREATE INDEX idx_personnel_account_id ON personnel(account_id);
   CREATE INDEX idx_payroll_donem ON payroll_calculations(donem);
   CREATE INDEX idx_payroll_personnel ON payroll_calculations(personnel_id);
   ```

2. **Eager Loading (N+1 Problem)**
   ```python
   # ❌ YAVAŞ (N+1 problem)
   personnel = db.query(Personnel).all()
   for p in personnel:
       account = p.account  # Her personel için ayrı sorgu
   
   # ✅ HIZLI (Eager loading)
   from sqlalchemy.orm import joinedload
   personnel = db.query(Personnel)\
       .options(joinedload(Personnel.account))\
       .all()
   ```

3. **Pagination**
   ```python
   # Büyük veri setlerinde mutlaka pagination
   def get_personnel(skip=0, limit=1000):
       query = db.query(Personnel)\
           .offset(skip)\
           .limit(limit)
       return query.all()
   ```

4. **Batch Processing**
   ```python
   # Yevmiye oluşturmada batch insert
   transaction_lines = []
   for payroll in payrolls:
       lines = create_lines(payroll)
       transaction_lines.extend(lines)
   
   db.bulk_save_objects(transaction_lines)  # Tek seferde kaydet
   ```

---

## 📊 İZLEME VE LOGLAMA

### Logging Stratejisi

```python
import logging

logger = logging.getLogger(__name__)

@router.post("/bordro-yevmiye-v2/generate")
def generate_yevmiye(request: GenerateYevmiyeRequest):
    logger.info(f"Yevmiye oluşturma başladı: {request.donem}")
    
    try:
        result = process_yevmiye(request)
        logger.info(f"Yevmiye başarılı: {result.personnel_count} personel")
        return result
        
    except Exception as e:
        logger.error(f"Yevmiye hatası: {str(e)}", exc_info=True)
        raise HTTPException(500, "Yevmiye oluşturulamadı")
```

### Metriks ve İstatistikler

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram

yevmiye_generated = Counter(
    'yevmiye_generated_total',
    'Total yevmiye generated',
    ['donem']
)

yevmiye_duration = Histogram(
    'yevmiye_generation_duration_seconds',
    'Yevmiye generation duration'
)
```

---

## 🧪 TEST STRATEJİSİ

### Unit Tests

```python
# test_personnel.py
def test_create_personnel():
    personnel = Personnel(
        code="P001",
        tckn="12345678901",
        first_name="Test",
        last_name="User"
    )
    assert personnel.code == "P001"
    assert personnel.full_name == "Test User"

def test_get_or_create_account():
    personnel = create_test_personnel()
    account = get_or_create_personnel_account(db, personnel)
    
    assert account.code == f"335.{personnel.tckn}"
    assert personnel.account_id == account.id
```

### Integration Tests

```python
# test_bordro_integration.py
def test_luca_import_to_yevmiye():
    # 1. Upload Luca Excel
    response = client.post(
        "/luca-bordro/upload",
        files={"file": test_excel_file}
    )
    assert response.status_code == 200
    
    # 2. Generate yevmiye
    response = client.post(
        "/bordro-yevmiye-v2/generate",
        json={"donem": "2025-12"}
    )
    assert response.json()["success"] == True
    
    # 3. Verify transactions
    transactions = db.query(Transaction)\
        .filter(Transaction.accounting_period == "2025-12")\
        .all()
    assert len(transactions) > 0
```

---

## 📈 GELECEKTEKİ GELİŞTİRMELER

### Öncelikli Özellikler

1. **Luca Personel Sicil Import**
   - Aylık personel sicil Excel import
   - Çoklu maliyet merkezi desteği
   - Ay içi giriş/çıkış takibi

2. **Redis Cache**
   - Aktif personel listesi
   - Departman listesi
   - İstatistikler

3. **Background Jobs**
   - Bordro hesaplama (Celery)
   - Yevmiye oluşturma (async)
   - Email bildirimleri

4. **Reporting**
   - Personel maliyet raporları
   - SGK prim beyanı
   - Bordro karşılaştırma

---

## 📞 REFERANSLAR

- **Detaylı Dokümantasyon:** [PERSONEL_MODULU.md](./PERSONEL_MODULU.md)
- **API Dokümantasyonu:** http://localhost:8000/docs
- **Veritabanı Schema:** [../database/schema.sql](../database/schema.sql)

**Son Güncelleme:** 18 Aralık 2025  
**Versiyon:** 2.0
