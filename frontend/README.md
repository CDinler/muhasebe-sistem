# Frontend Dizin Yapısı

React TypeScript tabanlı muhasebe frontend uygulaması

## 📂 Ana Dizinler

### `/src`
```
src/
├── assets/           # Statik dosyalar (resimler, fontlar)
├── components/       # Reusable React bileşenleri
│   └── layout/      # Layout bileşenleri (AppLayout, Header, Sidebar)
├── config/          # Konfigürasyon dosyaları
├── contexts/        # React Context'leri (Auth, Theme vb.)
├── features/        # Feature-based modüller
├── hooks/           # Custom React hooks
├── pages/           # Sayfa bileşenleri (Routes)
├── routes/          # Route konfigürasyonları
├── services/        # API servisleri
├── store/           # State management (Redux/Zustand)
├── styles/          # Global CSS/SCSS dosyaları
├── types/           # TypeScript type tanımları
└── utils/           # Yardımcı fonksiyonlar
```

## 📄 Sayfalar (`/pages`)

### Muhasebe Modülü
- **TransactionsPage.tsx** - Fiş listesi ve yönetimi
- **NewTransactionPage.tsx** - Yeni fiş oluşturma
- **TransactionDetailPage.tsx** - Fiş detayı görüntüleme
- **MuavinPage.tsx** - Muavin defteri görüntüleme

### Fatura Yönetimi
- **EInvoicesPage.tsx** - Fatura takip (E-Fatura/E-Arşiv)
- **InvoiceMatchingPage.tsx** - Fatura eşleştirme sistemi

### Cari & Hesap Yönetimi
- **ContactsPage.tsx** - Cari hesaplar yönetimi
- **AccountsPage.tsx** - Personel hesapları (Hesap planı)
- **CostCentersPage.tsx** - Masraf merkezleri yönetimi

### Personel Modülü
- **PersonnelPage.tsx** - Personel listesi
- **PersonnelContractsPage.tsx** - Personel sözleşmeleri
- **LucaBordroPage.tsx** - Luca bordro entegrasyonu
- **LucaSicilPage.tsx** - Luca sicil kayıtları (v1)
- **LucaSicilPage_v2.tsx** - Luca sicil kayıtları (v2)
- **LucaSicilPageTest.tsx** - Luca sicil test sayfası
- **PuantajGridPage.tsx** - Puantaj takip (Excel benzeri grid)
- **PuantajPage.tsx** - Puantaj yönetimi
- **DailyAttendancePage.tsx** - Takvimli puantaj sistemi
- **BordroCalculationPage.tsx** - Bordro hesaplama
- **SystemConfigPage.tsx** - Sistem ayarları (bordro parametreleri)

### Genel Sayfalar
- **Dashboard.tsx** - Ana dashboard
- **LoginPage.tsx** - Giriş sayfası
- **ReportsPage.tsx** - Raporlar modülü

## 🎨 Stil Yapısı

### CSS Dosyaları
- **EInvoicesPage.compact.css** - E-Fatura sayfası özel stilleri

### Global Stiller
- `styles/` dizininde global CSS/SCSS dosyaları

## 🔧 Konfigürasyon

### API Servisleri (`/services`)
Backend API'ye yapılan tüm HTTP istekleri

### Type Definitions (`/types`)
TypeScript interface ve type tanımları

### Utilities (`/utils`)
Yardımcı fonksiyonlar, formatters, validators

## 📱 Responsive Tasarım

Tüm sayfalar mobil, tablet ve desktop için optimize edilmiştir.

## 🚀 Kullanılan Teknolojiler

- **React 18** - UI Framework
- **TypeScript** - Type safety
- **Ant Design** - UI Component Library
- **React Router v6** - Routing
- **Axios** - HTTP Client
- **Vite** - Build tool
- **Day.js** - Date manipulation

## 🔐 Authentication

- JWT token tabanlı kimlik doğrulama
- Protected routes için `ProtectedRoute` component
- `AuthContext` ile kullanıcı state yönetimi
