# 📚 PERSONEL SİSTEMİ DOKÜMANTASYON İNDEKSİ

Personel modülü dokümantasyonuna hoş geldiniz! Bu sistem, şirket personelinin yönetimi, bordro hesaplamaları ve muhasebe yevmiye entegrasyonunu sağlar.

---

## 📖 DÖKÜMANLAR

### 1. 📋 [PERSONEL_MODULU.md](./PERSONEL_MODULU.md)
**Detaylı Teknik Dokümantasyon**

En kapsamlı dokümantasyon. Tüm teknik detaylar, veritabanı yapısı, API endpoint'leri ve örnekler.

**İçerik:**
- Veritabanı tabloları (personnel, personnel_contracts, payroll_calculations, monthly_puantaj)
- API endpoint'leri ve parametreleri
- Bordro yevmiye sistemi detayları
- Hesap kodları ve yevmiye örnekleri
- Optimizasyon detayları (account_id FK)
- Gelecek geliştirmeler
- Kontrol listeleri

**Hedef Kitle:** Backend geliştiriciler, sistem yöneticileri, veritabanı yöneticileri

---

### 2. 🏗️ [PERSONEL_SISTEM_MIMARİSİ.md](./PERSONEL_SISTEM_MIMARİSİ.md)
**Sistem Mimarisi ve Veri Akış Diyagramları**

Sistemin genel yapısını ve veri akışını görsel olarak anlatan dokümantasyon.

**İçerik:**
- Sistem mimarisi diyagramı
- Veri akış diyagramları (Personel ekleme, Luca import, Yevmiye oluşturma)
- Modül yapısı (backend/frontend)
- Güvenlik ve performans optimizasyonları
- İzleme ve loglama stratejisi
- Test stratejisi

**Hedef Kitle:** Yazılım mimarları, proje yöneticileri, yeni geliştiriciler

---

### 3. 📋 [PERSONEL_HIZLI_REFERANS.md](./PERSONEL_HIZLI_REFERANS.md)
**Hızlı Referans Kartı**

Günlük kullanım için hızlı erişim kartı. Sık kullanılan kod parçacıkları, SQL sorguları ve API çağrıları.

**İçerik:**
- Hızlı başlangıç örnekleri
- Önemli tablolar ve hesap kodları
- Sık kullanılan SQL sorguları
- API endpoint örnekleri
- İpuçları ve en iyi pratikler
- Sık karşılaşılan hatalar ve çözümleri
- Bakım ve destek komutları

**Hedef Kitle:** Günlük geliştirme yapan tüm ekip üyeleri

---

## 🚀 HIZLI ERİŞİM

### Senaryoya Göre Doküman Seçimi

#### "Sistemi ilk defa öğreniyorum"
1. **Başlangıç:** [PERSONEL_SISTEM_MIMARİSİ.md](./PERSONEL_SISTEM_MIMARİSİ.md) - Genel yapıyı öğren
2. **Detay:** [PERSONEL_MODULU.md](./PERSONEL_MODULU.md) - Teknik detaylara dal
3. **Pratik:** [PERSONEL_HIZLI_REFERANS.md](./PERSONEL_HIZLI_REFERANS.md) - Hızlı başla

#### "Yeni bir özellik geliştireceğim"
1. [PERSONEL_MODULU.md](./PERSONEL_MODULU.md) → Veritabanı Yapısı bölümü
2. [PERSONEL_SISTEM_MIMARİSİ.md](./PERSONEL_SISTEM_MIMARİSİ.md) → Modül Yapısı bölümü
3. [PERSONEL_HIZLI_REFERANS.md](./PERSONEL_HIZLI_REFERANS.md) → API örnekleri

#### "Bir hata ile karşılaştım"
1. [PERSONEL_HIZLI_REFERANS.md](./PERSONEL_HIZLI_REFERANS.md) → Sık Karşılaşılan Hatalar
2. [PERSONEL_MODULU.md](./PERSONEL_MODULU.md) → İlgili API/Veritabanı bölümü
3. [PERSONEL_SISTEM_MIMARİSİ.md](./PERSONEL_SISTEM_MIMARİSİ.md) → Veri akış diyagramları

#### "SQL sorgusu yazmam lazım"
→ [PERSONEL_HIZLI_REFERANS.md](./PERSONEL_HIZLI_REFERANS.md) → Sıkça Kullanılan Sorgular

#### "API endpoint'i nasıl çağrılıyor?"
→ [PERSONEL_HIZLI_REFERANS.md](./PERSONEL_HIZLI_REFERANS.md) → API Çağrıları  
→ [PERSONEL_MODULU.md](./PERSONEL_MODULU.md) → API Endpointleri

#### "Bordro yevmiye sistemi nasıl çalışıyor?"
1. [PERSONEL_SISTEM_MIMARİSİ.md](./PERSONEL_SISTEM_MIMARİSİ.md) → Bordro Yevmiye Akış Diyagramı
2. [PERSONEL_MODULU.md](./PERSONEL_MODULU.md) → Bordro Yevmiye Sistemi bölümü

---

## 📊 SİSTEM ÖZETİ

### Temel Özellikler
- ✅ **2,172 personel** yönetimi
- ✅ **Dönem bazlı** filtreleme (YYYY-MM)
- ✅ **Departman/maliyet merkezi** takibi
- ✅ **Luca bordro** entegrasyonu
- ✅ **Otomatik yevmiye** oluşturma
- ✅ **335.xxx hesap** kodları ile muhasebe entegrasyonu

### Teknoloji Stack
- **Backend:** FastAPI + SQLAlchemy + MySQL
- **Frontend:** React + TypeScript + Ant Design
- **Import:** Pandas (Luca Excel parse)
- **Export:** CSV Template

### Ana Tablolar
1. `personnel` - Personel kartları (2,172 kayıt)
2. `personnel_contracts` - Sözleşmeler
3. `payroll_calculations` - Bordro hesaplamaları
4. `monthly_puantaj` - Puantaj kayıtları
5. `accounts` (335.xxx) - Personel hesap planı

---

## 🔗 İLGİLİ SİSTEMLER

### Muhasebe Sistemi
- Hesap planı (`accounts`)
- Muhasebe fişleri (`transactions`, `transaction_lines`)
- Maliyet merkezleri (`cost_centers`)

### Bordro Sistemi
- Luca bordro import
- Bordro hesaplama
- SGK ve vergi hesaplamaları
- Yevmiye oluşturma

### Entegrasyonlar
- Luca bordro yazılımı (Excel import/export)
- Muhasebe programı (CSV export)
- SGK e-bildirge (gelecek)

---

## 📝 VERSİYON GEÇMİŞİ

### v2.0 (18 Aralık 2025) - Production Ready ✅
- ✅ `personnel.account_id` FK eklendi (2,172 kayıt migrate edildi)
- ✅ Dönem ve departman filtreleri eklendi
- ✅ Frontend total count düzeltildi (2,172)
- ✅ Bordro yevmiye sistemi optimize edildi
- ✅ Proje temizliği yapıldı (180+ gereksiz dosya silindi)
- ✅ Kapsamlı dokümantasyon oluşturuldu

### v1.0 (Önceki versiyon)
- Personnel CRUD
- Luca bordro import
- Basit yevmiye oluşturma
- CONCAT('335.', tckn) ile account ilişkisi (yavaş)

---

## 🎯 GELECEK PLANLAR

### Öncelikli (Q1 2026)
- [ ] Luca personel sicil Excel import
- [ ] `monthly_personnel_records` tablosu
- [ ] Redis cache (departman listesi, istatistikler)
- [ ] Background jobs (Celery) için bordro hesaplama

### Orta Öncelik (Q2 2026)
- [ ] Personel transfer geçmişi
- [ ] İzin ve rapor takibi
- [ ] SGK e-bildirge entegrasyonu
- [ ] Performans dashboard

### Uzun Vadeli
- [ ] Mobile app (personel self-service)
- [ ] AI-powered bordro anomali tespiti
- [ ] Multi-company support
- [ ] Advanced reporting

---

## 👥 EKİP VE DESTEK

### Geliştirme Ekibi
- Backend Developer
- Frontend Developer
- Database Administrator
- QA Engineer

### Destek Kanalları
- **Teknik Dokümantasyon:** Bu klasör
- **API Dokümantasyonu:** http://localhost:8000/docs
- **Database Schema:** [../database/schema.sql](../database/schema.sql)
- **Kod Repository:** `backend/app/` ve `frontend/src/`

---

## 🔧 KURULUM VE ÇALIŞTIRMA

### Gereksinimler
- Python 3.9+
- Node.js 16+
- MySQL 8.0+
- Redis (opsiyonel, cache için)

### Backend Başlatma
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Başlatma
```bash
cd frontend
npm install
npm start
```

### Tüm Sistemi Başlatma
```bash
# Proje kök dizininde
.\start_all.bat
```

---

## 📞 İLETİŞİM

**Proje Adı:** Muhasebe Sistem - Personel Modülü  
**Versiyon:** 2.0  
**Son Güncelleme:** 18 Aralık 2025  
**Durum:** ✅ Production Ready

---

## 📚 EK KAYNAKLAR

### Kod Örnekleri
```python
# Personel ekleme
from app.models.personnel import Personnel
personnel = Personnel(code="P001", tckn="12345678901", ...)

# Bordro yevmiye oluşturma
POST /api/v1/bordro-yevmiye-v2/generate
{"donem": "2025-12"}

# Dönem filtreli sorgulama
GET /api/v1/personnel/?period=2025-12&department=İDARİ
```

### SQL Örnekleri
```sql
-- Aktif personel listesi
SELECT * FROM personnel WHERE is_active = TRUE;

-- Aralık 2025 bordroları
SELECT * FROM payroll_calculations WHERE donem = '2025-12';

-- Account_ID olmayan personeller
SELECT * FROM personnel WHERE account_id IS NULL;
```

---

**🎉 Dokümantasyonu okuduğunuz için teşekkürler!**

Sorularınız için dokümanlara göz atın veya ekiple iletişime geçin.
