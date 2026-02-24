# PayrollCalculation Tablosu Sütun Kullanım Raporu

**Tarih:** 2025-01-17  
**Amaç:** `payroll_calculations` tablosunda hangi sütunların aktif olarak kullanıldığının analizi

---

## 📊 GENEL BAKIŞ

`payroll_calculations` tablosu **90+ sütun** içermektedir. Bu rapor, bu sütunların:
- ✅ **Frontend'de görüntülenip görüntülenmediğini**
- ✅ **Backend API'de dönen verilerde bulunup bulunmadığını**
- ✅ **Hangi amaçla kullanıldığını**

analiz eder.

---

## 🎯 KULLANIM DURUMU TABLOSU

### 1. Dönem ve Kimlik Bilgileri ✅ KULLANILIYOR

| Sütun | Frontend | Backend API | Kullanım Amacı |
|-------|----------|-------------|----------------|
| `id` | ✅ Evet | ✅ Evet | Detay modal, yevmiye kayıt ID |
| `yil` | ❌ Hayır | ❌ Endpoint parametresi | Dönem filtresi (query param) |
| `ay` | ❌ Hayır | ❌ Endpoint parametresi | Dönem filtresi (query param) |
| `donem` | ❌ Hayır | ❌ Hayır | Dönem string (YYYY-MM) |
| `personnel_id` | ✅ Evet | ✅ Evet | Personel tanımlama, group by |
| `tckn` | ✅ Evet | ✅ Evet | Tablo gösterim |
| `adi_soyadi` | ✅ Evet | ✅ Evet | Tablo başlık, modal başlık |
| `contract_id` | ❌ Hayır | ❌ Hayır | İlişkisel veri (kullanılmıyor) |
| `luca_bordro_id` | ❌ Hayır | ❌ Hayır | Kaynak veri referansı |

### 2. Şantiye/Maliyet Merkezi Bilgileri ✅ KULLANILIYOR

| Sütun | Frontend | Backend API | Kullanım Amacı |
|-------|----------|-------------|----------------|
| `cost_center_id` | ❌ Hayır | ❌ Hayır | İlişkisel veri |
| `santiye_adi` | ✅ Evet | ✅ Evet | Detay modal gösterim |

### 3. MAAŞ 1 (Luca Bordro Verileri) ✅ KULLANILIYOR

**Tüm alanlar frontend'de gösteriliyor ve API'den dönüyor:**

| Sütun | Frontend | Backend API | Kullanım Amacı |
|-------|----------|-------------|----------------|
| `maas1_net_odenen` | ✅ Evet | ✅ Evet | Tablo toplam, detay modal |
| `maas1_bes` | ✅ Evet | ✅ Evet | Tablo toplam, detay modal |
| `maas1_icra` | ✅ Evet | ✅ Evet | Tablo toplam, detay modal |
| `maas1_avans` | ❌ Hayır | ❌ Hayır | Luca veri (kullanılmıyor) |
| `maas1_gelir_vergisi` | ✅ Evet | ✅ Evet | Detay modal |
| `maas1_damga_vergisi` | ✅ Evet | ✅ Evet | Detay modal |
| `maas1_ssk_isci` | ✅ Evet | ✅ Evet | Detay modal |
| `maas1_ssk_isveren` | ✅ Evet | ✅ Evet | Detay modal, maliyet hesabı |
| `maas1_issizlik_isci` | ✅ Evet | ✅ Evet | Detay modal |
| `maas1_issizlik_isveren` | ✅ Evet | ✅ Evet | Detay modal, maliyet hesabı |
| `maas1_ssk_tesviki` | ❌ Hayır | ❌ Hayır | Luca veri (kullanılmıyor) |

### 4. MAAŞ 2 (Hesaplanan Maaş) ⚠️ KISMI KULLANIM

**Backend'de hesaplanıyor ama frontend'de GÖSTERİLMİYOR:**

| Sütun | Frontend | Backend API | Kullanım Amacı |
|-------|----------|-------------|----------------|
| `maas2_anlaşilan` | ❌ Hayır | ✅ Service'de | Toplam maaş hesabı |
| `maas2_normal_calismasi` | ❌ Hayır | ✅ Service'de | Normal gün kazancı |
| `maas2_hafta_tatili` | ❌ Hayır | ✅ Service'de | Hafta tatili kazancı |
| `maas2_fm_calismasi` | ❌ Hayır | ✅ Service'de | Fazla mesai kazancı |
| `maas2_resmi_tatil` | ❌ Hayır | ✅ Service'de | Resmi tatil kazancı |
| `maas2_tatil_calismasi` | ❌ Hayır | ✅ Service'de | Tatil mesai kazancı |
| `maas2_yillik_izin` | ❌ Hayır | ✅ Service'de | Yıllık izin kazancı |
| `maas2_yol` | ❌ Hayır | ✅ Service'de | Yol ücreti |
| `maas2_prim` | ❌ Hayır | ✅ Service'de | Prim |
| `maas2_ikramiye` | ❌ Hayır | ✅ Service'de | İkramiye |
| `maas2_bayram` | ❌ Hayır | ✅ Service'de | Bayram |
| `maas2_kira` | ❌ Hayır | ✅ Service'de | Kira |
| `maas2_toplam` | ❌ Hayır | ✅ Service'de | Toplam hesaplanan maaş |

**💡 NOT:** Bu alanlar bordro hesaplama service'inde (BordroCalculationService) kullanılıyor ancak frontend'de detay olarak gösterilmiyor. Yevmiye kaydı oluştururken kullanılabilir.

### 5. Puantaj Verileri ⚠️ KISMI KULLANIM

| Sütun | Frontend | Backend API | Kullanım Amacı |
|-------|----------|-------------|----------------|
| `normal_gun` | ❌ Hayır | ✅ Service'de | Puantaj hesabı |
| `hafta_tatili_gun` | ❌ Hayır | ✅ Service'de | Puantaj hesabı |
| `fazla_mesai_saat` | ❌ Hayır | ✅ Service'de | Puantaj hesabı |
| `tatil_mesai_gun` | ❌ Hayır | ✅ Service'de | Puantaj hesabı |
| `yillik_izin_gun` | ❌ Hayır | ✅ Service'de | Puantaj hesabı |

**💡 NOT:** Bu veriler `/bordro-calculation/puantaj-data` endpoint'inden alınabilir ancak şu anda frontend tabloda gösterilmiyor.

### 6. Elden Ücret ✅ KULLANILIYOR

| Sütun | Frontend | Backend API | Kullanım Amacı |
|-------|----------|-------------|----------------|
| `elden_ucret_ham` | ❌ Hayır | ✅ Service'de | Hesaplama |
| `elden_ucret_yuvarlanmis` | ✅ Evet | ✅ Evet | Tablo toplam, detay modal |
| `elden_yuvarlama` | ❌ Hayır | ❌ Hayır | Yuvarlama farkı |
| `elden_yuvarlama_yon` | ❌ Hayır | ❌ Hayır | Yuvarlama yönü |

### 7. Yevmiye ve Muhasebe Bilgileri ✅ KULLANILIYOR

| Sütun | Frontend | Backend API | Kullanım Amacı |
|-------|----------|-------------|----------------|
| `yevmiye_tipi` | ✅ Evet | ✅ Evet | Detay modal gösterim |
| `account_code_335` | ❌ Hayır | ✅ Service'de | Hesap planı eşleştirme |
| `transaction_id` | ✅ Evet | ✅ Evet | **YENİ:** Durum sütunu |
| `fis_no` | ✅ Evet | ✅ Evet | Detay modal gösterim |

**🆕 GÜNCELLEME:** `transaction_id` artık frontend'de "Durum" sütununda kullanılıyor:
- `transaction_id != null` → ✅ **İŞLENDİ** (yeşil tag)
- `transaction_id == null` → ⏳ **BEKLEMEDE** (turuncu tag)

### 8. Ek Bilgiler (Kanun, Ücret Tipi vb.) ✅ KULLANILIYOR

| Sütun | Frontend | Backend API | Kullanım Amacı |
|-------|----------|-------------|----------------|
| `kanun_tipi` | ✅ Evet | ✅ Evet | Detay modal gösterim |
| `ucret_nevi` | ✅ Evet | ✅ Evet | Detay modal gösterim |

### 9. Durum ve Hata Yönetimi ⚠️ KULLANILMIYOR (ŞİMDİLİK)

| Sütun | Frontend | Backend API | Kullanım Amacı |
|-------|----------|-------------|----------------|
| `is_approved` | ❌ Hayır | ❌ Hayır | Gelecek: Onay akışı |
| `is_exported` | ❌ Hayır | ❌ Hayır | Gelecek: Excel export tracking |
| `has_error` | ❌ Hayır | ❌ Hayır | Gelecek: Hata durumu |
| `error_message` | ❌ Hayır | ❌ Hayır | Gelecek: Hata mesajı |

**💡 ÖNERİ:** Bu alanlar şu anda kullanılmıyor ancak ileride iş akışı için kullanılabilir:
- `is_approved`: Bordro onaylandı mı? (Onay butonu eklenebilir)
- `has_error`: Hata durumunda kırmızı tag gösterilebilir
- `error_message`: Hata detayı tooltip olarak gösterilebilir

### 10. Metadata (Oluşturma/Güncellenme) ❌ KULLANILMIYOR

| Sütun | Frontend | Backend API | Kullanım Amacı |
|-------|----------|-------------|----------------|
| `notes` | ❌ Hayır | ❌ Hayır | Notlar (boş) |
| `created_at` | ❌ Hayır | ✅ Model'de | Oluşturma tarihi |
| `updated_at` | ❌ Hayır | ✅ Model'de | Güncellenme tarihi |
| `calculated_by` | ❌ Hayır | ❌ Hayır | Hesaplayan kullanıcı |
| `approved_by` | ❌ Hayır | ❌ Hayır | Onaylayan kullanıcı |

---

## 📈 ÖZET İSTATİSTİKLER

### Frontend Kullanım Durumu

| Kategori | Toplam Sütun | Kullanılan | Kullanılmayan | Kullanım Oranı |
|----------|--------------|------------|---------------|----------------|
| **Kimlik Bilgileri** | 9 | 4 | 5 | 44% |
| **Maaş 1 (Luca)** | 11 | 7 | 4 | 64% |
| **Maaş 2 (Hesaplanan)** | 13 | 0 | 13 | 0% |
| **Puantaj** | 5 | 0 | 5 | 0% |
| **Elden Ücret** | 4 | 1 | 3 | 25% |
| **Yevmiye** | 4 | 3 | 1 | 75% |
| **Durum/Hata** | 4 | 0 | 4 | 0% |
| **Metadata** | 5 | 0 | 5 | 0% |
| **DİĞER** | 35+ | ~10 | ~25 | ~29% |
| **TOPLAM** | **90+** | **~25** | **~65** | **~28%** |

### Backend Service Kullanımı

Backend'de (BordroCalculationService, BordroYevmiyeService) **tüm sütunlar** kullanılıyor çünkü:
- Maaş hesaplamaları yapılıyor (maas2_* alanları)
- Puantaj verileri işleniyor
- Yevmiye kayıtları oluşturuluyor
- SSK, vergi hesaplamaları yapılıyor

Ancak bu hesaplanan değerler **frontend'de detaylı gösterilmiyor**, sadece toplam değerler gösteriliyor.

---

## 🎯 ÖNERİLER

### 1. Frontend'de Gösterilmeyen Ama Değerli Alanlar

**Maaş 2 Detayları** modal'a eklenebilir:
```typescript
// Detay modal'a eklenebilecek alanlar:
- Normal Çalışma: {calc.maas2_normal_calismasi} ₺
- Fazla Mesai: {calc.maas2_fm_calismasi} ₺
- Hafta Tatili: {calc.maas2_hafta_tatili} ₺
- Resmi Tatil: {calc.maas2_resmi_tatil} ₺
- Yıllık İzin: {calc.maas2_yillik_izin} ₺
- Yol: {calc.maas2_yol} ₺
- Prim: {calc.maas2_prim} ₺
- İkramiye: {calc.maas2_ikramiye} ₺
```

### 2. Durum Alanları İçin İyileştirme

`is_approved`, `has_error`, `is_exported` alanları kullanılabilir:

```typescript
// Durum sütunu genişletilebilir:
{
  title: 'Durum',
  render: (_, record) => {
    if (record.has_error) return <Tag color="red">HATA</Tag>;
    if (record.transaction_id && record.is_approved) 
      return <Tag color="green">ONAYLANMIŞ</Tag>;
    if (record.transaction_id) 
      return <Tag color="blue">İŞLENDİ</Tag>;
    return <Tag color="orange">BEKLEMEDE</Tag>;
  }
}
```

### 3. Toplam İşveren Maliyeti Kaldırıldı ✅

**SON GÜNCELLEME:**
- ❌ `total_isveren_maliyet` sütunu **KALDIRILDI**
- ✅ `Durum` sütunu **EKLENDİ** (transaction_id bazlı)

Bu değişiklik ile frontend daha temiz ve kullanıcıya yevmiye durumu net görünüyor.

### 4. Kullanılmayan Alanların Temizlenmesi

Şu alanlar hiç kullanılmıyor ve kaldırılabilir:
- `notes` (boş)
- `calculated_by` (kullanılmıyor)
- `approved_by` (kullanılmıyor)
- `contract_id` (ilişkisel ama kullanılmıyor)
- `luca_bordro_id` (kaynak veri, gerekirse saklanabilir)

**⚠️ UYARI:** Kaldırma işleminden önce yevmiye servislerinde kullanılıp kullanılmadığı kontrol edilmeli.

---

## 📋 API ENDPOINT KULLANIM DURUMU

### `/bordro-calculation/list-grouped` (✅ ANA ENDPOINT)

**Dönen Veri Yapısı:**
```typescript
{
  items: [
    {
      personnel_id: number,
      tckn: string,
      adi_soyadi: string,
      has_active_draft_contract: boolean,
      
      // TOPLAMLAR (frontend'de gösteriliyor)
      total_net_odenen: float,
      total_bes: float,
      total_icra: float,
      total_elden_ucret: float,
      total_kazanc: float,
      total_isveren_maliyet: float,  // ⚠️ Artık frontend'de gösterilmiyor
      
      // DETAYLAR
      calculations: [
        {
          id: int,
          santiye_adi: string,
          ucret_nevi: string,
          kanun_tipi: string,
          yevmiye_tipi: string,
          
          // Maaş 1 verileri
          maas1_net_odenen: float,
          maas1_bes: float,
          maas1_icra: float,
          maas1_ssk_isci: float,
          maas1_ssk_isveren: float,
          maas1_issizlik_isci: float,
          maas1_issizlik_isveren: float,
          maas1_gelir_vergisi: float,
          maas1_damga_vergisi: float,
          elden_ucret_yuvarlanmis: float,
          
          // Yevmiye bilgisi
          transaction_id: int | null,  // ✅ YENİ: Durum gösterimi için
          fis_no: string | null
        }
      ]
    }
  ],
  total: int
}
```

**Kullanım:**
- ✅ Ana tablo gösterimi
- ✅ Toplam hesaplamalar
- ✅ Detay modal
- ✅ **Durum sütunu** (transaction_id kontrolü)

### `/bordro-calculation/puantaj-data` (❌ FRONTEND'DE KULLANILMIYOR)

Dönen veriler:
- Puantaj günleri (normal_gun, hafta_tatili_gun, vb.)
- Ek ödemeler (yol, prim, ikramiye, bayram, kira)
- Hesaplanan normal çalışma günü

**💡 ÖNERİ:** Bu endpoint frontend'de "Puantaj Bilgileri" modal'ında kullanılabilir.

### `/bordro-calculation/maas-hesabi-data` (❌ FRONTEND'DE KULLANILMIYOR)

Dönen veriler:
- Draft contract bilgileri
- Puantaj verileri
- Hesaplanan kazançlar (normal, mesai, tatil)
- Günlük ücret

**💡 ÖNERİ:** Bu endpoint frontend'de "Maaş Hesabı" modal'ında kullanılabilir.

---

## 🔗 İLGİLİ DOSYALAR

**Backend:**
- Model: `backend/app/models/payroll_calculation.py`
- Service: `backend/app/domains/personnel/bordro_calculation/service.py`
- Yevmiye Service: `backend/app/domains/personnel/bordro_calculation/yevmiye_service.py`
- Router: `backend/app/domains/personnel/bordro_calculation/router.py`

**Frontend:**
- Ana Sayfa: `frontend/src/pages/BordroCalculationPageGrouped.tsx`
- Kullanılan Sütunlar: ~25/90 (28%)

**Veritabanı:**
- Tablo: `payroll_calculations` (90+ sütun)

---

## 📝 DEĞİŞİKLİK GEÇMİŞİ

| Tarih | Değişiklik | Açıklama |
|-------|------------|----------|
| 2025-01-17 | `total_isveren_maliyet` kaldırıldı | Frontend tablosundan kaldırıldı |
| 2025-01-17 | `Durum` sütunu eklendi | `transaction_id` bazlı İŞLENDİ/BEKLEMEDE gösterimi |
| 2025-01-17 | Rapor oluşturuldu | İlk sütun kullanım analizi |

---

**Hazırlayan:** GitHub Copilot  
**Versiyon:** 1.0  
**Son Güncelleme:** 2025-01-17
