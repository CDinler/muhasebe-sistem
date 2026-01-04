# Muhasebe Otomasyon Sistemi

**Proje:** Muhasebe kayıt ve raporlama otomasyonu  
**Tech Stack:** PostgreSQL 15+ | FastAPI | React TypeScript  
**Başlangıç:** 14 Aralık 2025  
**Hedef Süre:** 10 gün

---

## 📁 Proje Yapısı

```
C:\Projects\muhasebe-sistem\
├── backend/               # FastAPI Backend (Port 8000)
│   ├── app/              # Ana uygulama kodu
│   ├── alembic/          # Database migrations
│   └── logs/             # Application logs
├── frontend/              # React TypeScript Frontend (Port 5173)
│   └── src/              # React source code
├── database/              # PostgreSQL backup ve scripts
├── data/                  # Import/export data dosyaları
├── excel-integration/     # Excel ↔ Database sync
├── docs/                  # 📚 Dokümantasyon (bkz. docs/README.md)
│   ├── analysis/         # Analiz ve raporlar
│   ├── api/              # API dokümantasyonu
│   ├── architecture/     # Mimari dokümanlar
│   ├── gib-docs/         # GİB resmi dokümanları
│   └── user-manual/      # Kullanıcı kılavuzları
└── scripts/               # 🛠️ Yönetim scriptleri (bkz. scripts/README.md)
    ├── analysis/         # Veri analiz scriptleri
    ├── migrations/       # Database migration scriptleri
    ├── tests/            # Test scriptleri
    └── utilities/        # Genel utility scriptleri
```

---

## 🚀 Kurulum

### Backend
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```powershell
cd frontend
npm install
npm run dev
```

### Database
```powershell
# PostgreSQL kurulumu gerekli
cd database
psql -U postgres -f schema.sql
```

---

## 🔗 Bağlantılar

- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Frontend:** http://localhost:5173
- **Database:** localhost:5432/muhasebe_db

---

## 📊 Veri Konumları

- **Proje:** `C:\Projects\muhasebe-sistem\`
- **Excel Dosyaları:** `C:\Users\CAGATAY\OneDrive\Desktop\MUHASEBE - KADIOĞULLARI END\`
- **Database Backups:** `C:\Database\Backups\muhasebe-sistem\`

---

## 🛠️ Teknolojiler

**Backend:**
- FastAPI 0.109+
- SQLAlchemy 2.0+
- PostgreSQL 15+
- Alembic (migrations)
- Pydantic (validation)

**Frontend:**
- React 18
- TypeScript 5
- Vite
- Ant Design
- Redux Toolkit
- Recharts

**Excel Integration:**
- openpyxl
- pandas
- xlwings

---

## 📝 Mimari

**API Design:** RESTful, versioned (v1)  
**Database:** Luca-compatible, English table names  
**Authentication:** JWT with role-based access  
**Testing:** Pytest (backend), Vitest (frontend)

---

## 👥 Kullanıcı Rolleri

1. **Patron:** Read-only, mobil raporlar
2. **Muhasebeci:** Full access, Excel + Web
3. **Şantiye Muhasebeci:** Limited, kendi maliyet merkezi

---

## 📅 10-Gün Planı

- **Gün 1-2:** PostgreSQL + FastAPI altyapı
- **Gün 3-4:** Zirve fatura otomasyonu
- **Gün 5-7:** React dashboard + raporlar
- **Gün 8-9:** Deployment (DigitalOcean)
- **Gün 10:** Eğitim + dokümantasyon

---

## 📞 İletişim

**Geliştirici:** GitHub Copilot + User  
**Tarih:** 14 Aralık 2025
