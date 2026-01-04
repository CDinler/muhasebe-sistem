# Backend Dizin Yapısı

FastAPI tabanlı muhasebe backend uygulaması

## 📂 Ana Dizinler

### `/backend`
```
backend/
├── alembic/              # Database migration tool
│   └── versions/        # Migration dosyaları
├── app/                  # Ana uygulama dizini
│   ├── api/             # API endpoints (v1, v2)
│   ├── core/            # Core konfigürasyon (auth, config, security)
│   ├── crud/            # CRUD operasyonları (database logic)
│   ├── middleware/      # Custom middleware'ler
│   ├── models/          # SQLAlchemy ORM modelleri
│   ├── routers/         # API router'ları (deprecated, api/ kullan)
│   ├── routes/          # API route tanımları
│   ├── schemas/         # Pydantic şemaları (request/response)
│   ├── services/        # Business logic servisleri
│   ├── tasks/           # Background tasks (Celery vb.)
│   ├── utils/           # Yardımcı fonksiyonlar
│   └── main.py          # FastAPI app entry point
├── data/                 # Data dosyaları
│   └── import/          # Import için kullanılan dosyalar
├── logs/                 # Application log dosyaları
├── reports/              # Generated reports
├── templates/            # Email/PDF şablonları
├── tests/                # Test dosyaları (moved to /scripts/tests)
├── .env                  # Environment variables (local)
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
└── requirements-dev.txt  # Development dependencies
```

## 🗄️ Database Modelleri (`/app/models`)

### Muhasebe Modülleri
- **transaction.py** - Fiş kayıtları
- **transaction_line.py** - Fiş satırları
- **account.py** - Hesap planı
- **contact.py** - Cari hesaplar
- **cost_center.py** - Masraf merkezleri
- **document_type.py** - Evrak tipleri (E-Fatura, Bordro vb.)

### E-Fatura Modülleri
- **einvoice.py** - E-Fatura/E-Arşiv kayıtları
- **einvoice_pdf.py** - PDF dosyaları
- **invoice_mapping.py** - Fatura-Fiş eşleştirme

### Personel Modülleri
- **personnel.py** - Personel bilgileri
- **personnel_contract.py** - Personel sözleşmeleri
- **daily_attendance.py** - Günlük puantaj
- **puantaj_record.py** - Puantaj kayıtları
- **luca_bordro.py** - Luca bordro kayıtları
- **luca_sicil.py** - Luca sicil kayıtları

### Sistem Modülleri
- **user.py** - Kullanıcılar
- **system_config.py** - Sistem ayarları

## 🔌 API Endpoints (`/app/api`)

### v1 Endpoints
```
/api/v1/
├── /auth              # Authentication (login, register)
├── /transactions      # Fiş CRUD
├── /accounts          # Hesap planı
├── /contacts          # Cari hesaplar
├── /cost-centers      # Masraf merkezleri
├── /einvoices         # E-Fatura yönetimi
├── /invoice-matching  # Fatura eşleştirme
├── /personnel         # Personel yönetimi
├── /puantaj           # Puantaj sistemi
├── /daily-attendance  # Takvimli puantaj
├── /luca-bordro       # Luca bordro
├── /luca-sicil        # Luca sicil
├── /reports           # Raporlar
└── /system-config     # Sistem ayarları
```

## 🔧 Servisler (`/app/services`)

### Business Logic Servisleri
- **einvoice_accounting_service.py** - E-Fatura → Fiş dönüşümü
- **transaction_service.py** - Fiş işlemleri
- **contact_service.py** - Cari işlemleri
- **personnel_service.py** - Personel işlemleri
- **puantaj_service.py** - Puantaj işlemleri
- **report_service.py** - Rapor oluşturma

### Entegrasyon Servisleri
- **luca_service.py** - Luca API entegrasyonu
- **gib_service.py** - GİB XML parsing
- **pdf_service.py** - PDF işlemleri
- **excel_service.py** - Excel import/export

## 📊 CRUD Operasyonları (`/app/crud`)

Database CRUD işlemleri için repository pattern
- **transaction.py** - Fiş CRUD
- **account.py** - Hesap CRUD
- **contact.py** - Cari CRUD
- **einvoice.py** - E-Fatura CRUD
- **personnel.py** - Personel CRUD
- **reports.py** - Rapor sorguları

## 🔐 Core Konfigürasyon (`/app/core`)

- **config.py** - Uygulama konfigürasyonu
- **security.py** - JWT token, password hashing
- **database.py** - Database connection
- **auth.py** - Authentication logic

## 📝 Schemas (`/app/schemas`)

Pydantic şemaları (request/response validation)
- **transaction.py** - TransactionCreate, TransactionResponse
- **account.py** - AccountCreate, AccountResponse
- **contact.py** - ContactCreate, ContactResponse
- **einvoice.py** - EInvoiceCreate, EInvoiceResponse
- **personnel.py** - PersonnelCreate, PersonnelResponse

## 🛠️ Utilities (`/app/utils`)

Yardımcı fonksiyonlar
- **helpers.py** - Genel helper fonksiyonlar
- **validators.py** - Veri validasyonları
- **formatters.py** - Veri formatlamaları
- **xml_parser.py** - XML parsing
- **pdf_parser.py** - PDF parsing
- **excel_helper.py** - Excel işlemleri

## 🗃️ Database Migration

### Alembic Migration
```bash
# Yeni migration oluştur
alembic revision --autogenerate -m "migration açıklaması"

# Migration uygula
alembic upgrade head

# Migration geri al
alembic downgrade -1
```

## 📦 Dependencies

### Ana Bağımlılıklar
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **Alembic** - Database migrations
- **psycopg2** - PostgreSQL driver
- **python-jose** - JWT tokens
- **passlib** - Password hashing
- **python-multipart** - File upload
- **openpyxl** - Excel işlemleri
- **lxml** - XML parsing
- **PyPDF2** - PDF işlemleri

## 🚀 Çalıştırma

```bash
# Virtual environment aktive et
.venv\Scripts\Activate.ps1

# Bağımlılıkları yükle
pip install -r requirements.txt

# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔍 Logging

- Log dosyaları: `logs/` dizininde
- Log seviyesi: `.env` dosyasında `LOG_LEVEL` ile ayarlanır
- Format: JSON (structured logging)

## 🧪 Testing

Test dosyaları `/scripts/tests/` dizinine taşınmıştır.

```bash
cd backend
python ../scripts/tests/test_*.py
```
