# Excel Benzeri Puantaj Girişi

## 📋 Genel Bakış

Luca muhasebe programındaki puantaj Excel formatıyla uyumlu, Excel benzeri bir puantaj giriş ekranı oluşturuldu.

## ✨ Özellikler

### 1. Excel Benzeri Grid Yapısı
- **31 günlük kolonlar** yan yana
- **Her personel bir satırda**
- **Inline editing** - hücrelere tıklayıp durum kodu seçilebilir
- **Luca uyumlu durum kodları**
- **Otomatik özet hesaplama**

### 2. Durum Kodları (Luca Uyumlu)

| Kod | Açıklama | Renk |
|-----|----------|------|
| N | Normal | Yeşil |
| H | Hafta Tatili | Gri |
| T | Resmi Tatil | Kırmızı |
| İ | İzinli | Turuncu |
| S | Yıllık İzin | Turuncu |
| R | Raporlu | Kırmızı |
| E | Eksik Gün | Açık Kırmızı |
| Y | Yarım Gün | Sarı |
| G | Gece Mesaisi | Mavi |
| O | Gündüz Mesaisi | Açık Mavi |
| K | Yarım Gün Resmi Tatil | Turuncu |
| C | Yarım Gün Hafta Tatili | Gri |

### 3. Otomatik Hesaplanan Alanlar

- **Çalışılan Gün**: N, G, O kodlarının toplamı
- **SSK Gün**: Çalışılan + Yıllık İzin + İzinli
- **İzin Gün**: İ kodlarının toplamı
- **Yıllık İzin**: S kodlarının toplamı
- **Rapor Gün**: R kodlarının toplamı
- **Eksik Gün**: E kodlarının toplamı
- **Yarım Gün**: Y, K, C kodlarının toplamı (0.5 olarak)

## 🗄️ Database Yapısı

### Tablo: `personnel_puantaj_grid`

```sql
CREATE TABLE personnel_puantaj_grid (
  id INT AUTO_INCREMENT PRIMARY KEY,
  personnel_id INT NOT NULL,
  donem VARCHAR(7) NOT NULL,  -- 'YYYY-MM'
  yil INT NOT NULL,
  ay INT NOT NULL,
  
  -- 31 günlük kolonlar
  gun_1 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C'),
  gun_2 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C'),
  ...
  gun_31 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C'),
  
  -- Otomatik hesaplanan özet alanlar
  calisilan_gun_sayisi INT DEFAULT 0,
  ssk_gun_sayisi INT DEFAULT 0,
  yillik_izin_gun INT DEFAULT 0,
  izin_gun_sayisi INT DEFAULT 0,
  rapor_gun_sayisi INT DEFAULT 0,
  eksik_gun_sayisi INT DEFAULT 0,
  yarim_gun_sayisi DECIMAL(3,1) DEFAULT 0,
  toplam_gun_sayisi INT DEFAULT 0,
  
  UNIQUE KEY (personnel_id, donem)
);
```

### Trigger'lar

**INSERT ve UPDATE Trigger'ları**: 31 günlük kolonları analiz ederek özet alanları otomatik hesaplar.

## 🚀 API Endpoint'leri

### GET /api/v1/daily-attendance/grid
Belirtilen dönem için tüm personelin puantaj grid verisini getirir.

**Query Params:**
- `donem`: YYYY-MM formatında dönem (örn: "2025-12")

**Response:**
```json
{
  "success": true,
  "donem": "2025-12",
  "total": 36,
  "records": [
    {
      "id": 1,
      "sicil_no": "001",
      "adi_soyadi": "AHMET YILMAZ",
      "tckn": "12345678901",
      "gun_1": "N",
      "gun_2": "N",
      ...
      "gun_31": "H"
    }
  ]
}
```

### POST /api/v1/daily-attendance/grid/save
Grid'de yapılan değişiklikleri kaydeder.

**Request Body:**
```json
{
  "donem": "2025-12",
  "records": [
    {
      "id": 1,
      "gun_1": "N",
      "gun_2": "N",
      ...
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "donem": "2025-12",
  "saved": 5,
  "updated": 31,
  "total": 36
}
```

## 🎨 Frontend Bileşeni

### Sayfa: `PuantajGridPage.tsx`

**Özellikler:**
- Ant Design Table ile grid yapısı
- 31 günlük kolonlar dinamik oluşturulur
- Her hücrede dropdown ile durum seçimi
- Değiştirilen hücreler sarı arka planla işaretlenir
- Kaydet butonu değişiklikleri server'a gönderir
- Ay seçici (DatePicker)
- Excel'den import desteği (gelecekte)

**Kolon Yapısı:**
1. Sicil No (sabit, sol)
2. Ad Soyad (sabit, sol)
3. 1-31 arası günler (gün numarası ve gün adı başlıkta)
4. Özet kolonlar: Çalışılan, İzin, Eksik

## 📱 Kullanım

### 1. Menüden Erişim
**Bordro → Puantaj Girişi (Excel)**

### 2. Dönem Seçimi
Sağ üstteki ay seçici ile ilgili dönemi seçin.

### 3. Veri Girişi
- Her personel için günlük durumları dropdown'dan seçin
- Değiştirilen hücreler sarı renkte gösterilir
- Durum kodları renkli gösterilir

### 4. Kaydetme
"Kaydet" butonuna tıklayın. Değişiklik sayısı butonda gösterilir.

### 5. Yenileme
"Yenile" butonu ile son kaydedilen veriyi yeniden yükleyin.

## 🔄 Luca Uyumluluğu

### Excel Import (Gelecek Özellik)
Luca'dan export edilen puantaj Excel dosyası:
- Header satırları atlanır (ilk 8 satır)
- TC Kimlik No ile personel eşleştirilir
- Gün kolonları (Pt, Sa, Ça ... Ça.4) parse edilir
- Durum kodları direkt sisteme aktarılır

### Format Karşılaştırma

| Luca Excel | Sistemimiz |
|-----------|-----------|
| TC No | tckn (personnel ile JOIN) |
| Pt, Sa, Ça (31 gün) | gun_1 .. gun_31 |
| Çalışılan Gün | calisilan_gun_sayisi |
| SSK Gün | ssk_gun_sayisi |
| İzin Gün | izin_gun_sayisi |
| Toplam | toplam_gun_sayisi |

## 📦 Kurulum

### 1. Database Migration
```bash
cd backend
python run_puantaj_grid_migration.py
```

### 2. Backend Model
Model dosyası: `app/models/personnel_puantaj_grid.py`

### 3. API Endpoints
Endpoint dosyası: `app/api/v1/endpoints/daily_attendance.py`
- `/grid` endpoint'i eklenmiştir
- `/grid/save` endpoint'i eklenmiştir

### 4. Frontend Route
```tsx
// App.tsx
import PuantajGridPage from './pages/PuantajGridPage';
<Route path="puantaj-grid" element={<PuantajGridPage />} />
```

### 5. Menü Eklendi
```tsx
// AppLayout.tsx
{
  key: '/puantaj-grid',
  icon: <TableOutlined />,
  label: 'Puantaj Girişi (Excel)',
}
```

## 🎯 Avantajlar

1. **Hızlı Veri Girişi**: Excel benzeri arayüz sayesinde toplu giriş
2. **Görsel Geri Bildirim**: Renkli durum kodları, değişiklik işaretleme
3. **Otomatik Hesaplama**: Özet alanlar trigger ile otomatik
4. **Luca Uyumlu**: Durum kodları birebir uyumlu
5. **Performanslı**: Her personel-dönem tek satır (index'li)
6. **Validation**: ENUM ile yanlış veri girişi engellenir

## ⚠️ Notlar

- Her personel-dönem kombinasyonu için tek kayıt (UNIQUE constraint)
- Trigger'lar otomatik özet hesaplama yapar
- Frontend'de yapılan değişiklikler sarı renkle işaretlenir
- Kaydet butonuna basmadan değişiklikler kaybolur
- 31 günden az olan aylarda (28, 29, 30 günlük) son kolonlar boş kalır

## 🚀 Gelecek Geliştirmeler

1. **Excel Import**: Luca puantaj Excel'ini direkt import
2. **Excel Export**: Grid verisini Excel olarak export
3. **Toplu İşlemler**: Tüm personele aynı günde aynı durum atama
4. **Şablon Uygula**: Önceki ay verilerini kopyalama
5. **Hücre Renklendirme**: Hafta sonu/tatil günlerini otomatik işaretle
6. **Yorum/Not**: Her hücreye açıklama ekleme
7. **Değişiklik Geçmişi**: Kimin ne zaman değiştirdiğini takip

## 📊 Performans

- **Index'ler**: personnel_id, donem, yil-ay
- **UNIQUE Constraint**: Duplicate önleme
- **Trigger Optimizasyonu**: BEFORE INSERT/UPDATE
- **Frontend**: Virtual scrolling (büyük liste için)
- **API**: Tek sorgu ile tüm personel
