# 🎯 Optimizasyon TODO Listesi
**Tarih:** 1 Şubat 2026  
**Tahmini Süre:** 4-6 saat  
**Durum:** Planlandı - Henüz başlanmadı

---

## 📊 Mevcut Durum Analizi

### Büyük Dosyalar
- `puantaj_grid/service.py`: **1,232 satır** (7 metod)
- `yevmiye_service_bordro.py`: **1,346 satır** (15 metod)
- `bordro_calculation/router.py`: **760 satır** (8 endpoint)
- `bordro_calculation/service.py`: **666 satır** (7 metod)

### Sorunlar
1. Excel işlemleri service içinde (739 satır)
2. get_grid_data() metodunda kod tekrarı (287 satır)
3. Wage calculation 6 farklı yerde
4. Unit test yok

---

## ✅ Seçenek A: Hızlı İyileştirme (2 saat)

### 1. Excel Handler Ayırma (1 saat)

**Yeni Dosya Oluştur:**
```
backend/app/domains/personnel/puantaj_grid/excel_handler.py
```

**İçerik:**
- `create_template_excel()` → service.py'den kopyala
- `parse_excel_without_saving()` → service.py'den kopyala
- `upload_from_excel()` → service.py'den kopyala

**service.py Güncelleme:**
```python
from .excel_handler import PuantajExcelHandler

class PuantajGridService:
    def __init__(self, db: Session):
        self.excel_handler = PuantajExcelHandler(db)
    
    # Wrapper metodlar (backward compatible)
    def create_template_excel(self, ...):
        return self.excel_handler.create_template_excel(...)
```

**Sonuç:**
- `service.py`: 1232 → ~450 satır ✨
- `excel_handler.py`: ~750 satır (yeni)
- Mevcut API değişmiyor

**Test Checklist:**
- [ ] Excel template oluşturma çalışıyor
- [ ] Excel import çalışıyor
- [ ] Excel parse çalışıyor

---

### 2. Helper Metodlar Ekleme (1 saat)

**service.py'e Eklenecek Helper'lar:**

```python
def _build_personnel_row(
    self, 
    person: Personnel,
    contract: Optional[PersonnelContract],
    draft: Optional[PersonnelDraftContract],
    grid: Optional[PersonnelPuantajGrid] = None
) -> dict:
    """Personel satırını oluştur (DRY principle)"""
    return {
        'id': person.id,
        'adi_soyadi': f"{person.ad} {person.soyad}",
        'tc_kimlik_no': person.tc_kimlik_no or '',
        'cost_center_id': contract.cost_center_id if contract else None,
        # ... diğer ortak alanlar
    }

def _apply_daily_defaults(
    self,
    row: dict,
    year: int,
    month: int,
    holidays: set,
    calisma_takvimi: Optional[str],
    ise_giris: Optional[date],
    isten_cikis: Optional[date]
) -> dict:
    """Günlük default değerleri uygula (T, H, -, vb.)"""
    son_gun = calendar.monthrange(year, month)[1]
    
    for i in range(1, 32):
        gun_col = f'gun_{i}'
        
        if i > son_gun:
            row[gun_col] = None
            continue
        
        current_date = date(year, month, i)
        
        # Sigortasının olmadığı günler
        is_not_insured = False
        if ise_giris and current_date < ise_giris:
            is_not_insured = True
        elif isten_cikis and current_date > isten_cikis:
            is_not_insured = True
        
        if is_not_insured:
            row[gun_col] = '-'
        elif i in holidays:
            row[gun_col] = 'T'
        elif current_date.weekday() == 6 and calisma_takvimi == 'atipi':
            row[gun_col] = 'H'
        else:
            row[gun_col] = row.get(gun_col)  # Mevcut değeri koru
    
    return row

def _should_include_personnel(
    self,
    draft: Optional[PersonnelDraftContract],
    cost_center_id: Optional[int]
) -> bool:
    """Personelin listeye dahil edilip edilmeyeceğini kontrol et"""
    if not draft:
        return False
    
    if cost_center_id and draft.cost_center_id != cost_center_id:
        return False
    
    return True
```

**Refactor get_grid_data():**
- Satır 48-175: `_build_personnel_row()` ve `_apply_daily_defaults()` kullan
- Satır 176-287: `_build_personnel_row()` ve `_apply_daily_defaults()` kullan
- Tekrar eden kod kaldır

**Sonuç:**
- `get_grid_data()`: 287 → ~120 satır
- Kod okunabilirliği arttı
- DRY principle uygulandı

**Test Checklist:**
- [ ] Puantaj grid sayfası açılıyor
- [ ] Cost center filtresi çalışıyor
- [ ] Tatil günleri T olarak işaretli
- [ ] Pazar günleri (atipi için) H olarak işaretli
- [ ] İşe giriş/çıkış tarihleri doğru hesaplanıyor

---

## 🚀 Seçenek B: WageCalculator Ekleme (+3 saat)

### 3. WageCalculator Oluşturma (2 saat)

**Dizin Yapısı:**
```
backend/app/domains/personnel/payroll/
├── __init__.py
├── calculations/
│   ├── __init__.py
│   └── wage_calculator.py
```

**wage_calculator.py İçeriği:**

```python
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from dataclasses import dataclass, asdict
from datetime import date

@dataclass
class PuantajInput:
    """Puantaj giriş verileri"""
    normal_calismasi: Decimal
    fazla_calismasi: Decimal
    eksik_calismasi: Decimal
    gece_calismasi: Decimal
    tatil_calismasi: Decimal
    yillik_izin_gun: int
    izin_gun_sayisi: int
    yol: Decimal = Decimal('0')
    prim: Decimal = Decimal('0')
    ikramiye: Decimal = Decimal('0')

@dataclass
class ContractInput:
    """Sözleşme bilgileri"""
    net_ucret: Decimal
    ucret_nevi: str  # 'aylik', 'gunluk', 'saatlik'
    fm_orani: Decimal
    tatil_orani: Decimal

@dataclass
class WageCalculationOutput:
    """Maaş hesaplama çıktısı"""
    gunluk_ucret: Decimal
    normal_kazanc: Decimal
    mesai_kazanc: Decimal
    eksik_mesai_kazanc: Decimal
    tatil_kazanc: Decimal
    tatil_mesai_kazanc: Decimal
    yillik_izin_kazanc: Decimal
    izin_kazanc: Decimal
    ek_odemeler_toplam: Decimal
    brut_kazanc: Decimal
    toplam_kazanc: Decimal

class WageCalculator:
    """Merkezi maaş hesaplama sınıfı"""
    
    @staticmethod
    def calculate_gunluk_ucret(contract: ContractInput) -> Decimal:
        """Günlük ücret hesapla"""
        if contract.ucret_nevi == 'aylik':
            return (contract.net_ucret / Decimal('30')).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        elif contract.ucret_nevi == 'gunluk':
            return contract.net_ucret
        elif contract.ucret_nevi == 'saatlik':
            return contract.net_ucret * Decimal('8')
        else:
            raise ValueError(f"Geçersiz ücret nevi: {contract.ucret_nevi}")
    
    @staticmethod
    def calculate_wages(
        puantaj: PuantajInput,
        contract: ContractInput
    ) -> WageCalculationOutput:
        """
        Maaş hesapla - TÜM hesaplamaların tek kaynağı
        """
        # Günlük ücret
        gunluk_ucret = WageCalculator.calculate_gunluk_ucret(contract)
        
        # İzin günü sınırlaması (max 30)
        izin_gun_sinirli = min(puantaj.izin_gun_sayisi, 30)
        
        # Normal kazanç
        normal_kazanc = puantaj.normal_calismasi * gunluk_ucret
        
        # İzin kazancı (ayrı satır)
        izin_kazanc = izin_gun_sinirli * gunluk_ucret
        
        # Fazla mesai kazancı
        mesai_kazanc = (
            puantaj.fazla_calismasi * (gunluk_ucret / Decimal('8')) * contract.fm_orani
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Eksik mesai kazancı (negatif)
        eksik_mesai_kazanc = (
            puantaj.eksik_calismasi * (gunluk_ucret / Decimal('8'))
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Tatil çalışması kazancı
        tatil_kazanc = puantaj.tatil_calismasi * gunluk_ucret
        
        # Tatil fazla mesai
        tatil_mesai_kazanc = Decimal('0')  # Şimdilik basit
        
        # Yıllık izin
        yillik_izin_kazanc = puantaj.yillik_izin_gun * gunluk_ucret
        
        # Ek ödemeler
        ek_odemeler_toplam = puantaj.yol + puantaj.prim + puantaj.ikramiye
        
        # Brüt kazanç (ek ödemeler hariç)
        brut_kazanc = (
            normal_kazanc + 
            izin_kazanc +
            mesai_kazanc - 
            eksik_mesai_kazanc + 
            tatil_kazanc + 
            tatil_mesai_kazanc + 
            yillik_izin_kazanc
        )
        
        # Toplam kazanç
        toplam_kazanc = brut_kazanc + ek_odemeler_toplam
        
        return WageCalculationOutput(
            gunluk_ucret=gunluk_ucret,
            normal_kazanc=normal_kazanc,
            mesai_kazanc=mesai_kazanc,
            eksik_mesai_kazanc=eksik_mesai_kazanc,
            tatil_kazanc=tatil_kazanc,
            tatil_mesai_kazanc=tatil_mesai_kazanc,
            yillik_izin_kazanc=yillik_izin_kazanc,
            izin_kazanc=izin_kazanc,
            ek_odemeler_toplam=ek_odemeler_toplam,
            brut_kazanc=brut_kazanc,
            toplam_kazanc=toplam_kazanc
        )
```

### 4. Bir Endpoint'e Entegre Et (1 saat)

**bordro_calculation/router.py → /maas-hesabi-data endpoint:**

```python
from app.domains.personnel.payroll.calculations.wage_calculator import (
    WageCalculator, 
    PuantajInput, 
    ContractInput
)

@router.get("/maas-hesabi-data")
async def get_maas_hesabi_data(...):
    # ... mevcut kod ...
    
    # WageCalculator kullan
    puantaj_input = PuantajInput(
        normal_calismasi=Decimal(str(normal_calismasi)),
        fazla_calismasi=Decimal(str(fazla_calismasi)),
        eksik_calismasi=Decimal(str(eksik_calismasi)),
        # ... diğer alanlar
    )
    
    contract_input = ContractInput(
        net_ucret=Decimal(str(net_ucret)),
        ucret_nevi=ucret_nevi,
        fm_orani=Decimal(str(fm_orani)),
        tatil_orani=Decimal(str(tatil_orani))
    )
    
    result = WageCalculator.calculate_wages(puantaj_input, contract_input)
    
    return {
        "gunluk_kazanc": float(result.gunluk_ucret),
        "normal_kazanc": float(result.normal_kazanc),
        # ... tüm alanlar
    }
```

**Test Checklist:**
- [ ] Maaş hesabı modalı açılıyor
- [ ] Hesaplamalar doğru (eski sonuçlarla karşılaştır)
- [ ] İzin günü 30 ile sınırlı
- [ ] Normal kazanç + izin kazancı ayrı görünüyor

---

## 📋 İmplementasyon Adımları

### Commit Stratejisi
```bash
# Başlangıç
git checkout -b optimization/code-cleanup
git tag pre-optimization-backup

# Her adımda commit
git add .
git commit -m "refactor: Excel handler'ı ayır"

git add .
git commit -m "refactor: Helper metodlar ekle"

git add .
git commit -m "feat: WageCalculator sınıfı ekle"

git add .
git commit -m "refactor: maas-hesabi-data endpoint WageCalculator kullanıyor"

# Test sonrası merge
git checkout main
git merge optimization/code-cleanup
```

---

## 🧪 Test Stratejisi

### Manuel Test Listesi
**Excel Handler:**
- [ ] Puantaj Grid sayfasını aç
- [ ] "Excel Template İndir" butonuna bas
- [ ] Excel dosyası indirildi mi?
- [ ] Excel'i doldur ve import et
- [ ] Veriler doğru yüklendi mi?

**Helper Metodlar:**
- [ ] Puantaj Grid sayfasını aç
- [ ] Farklı maliyet merkezleri seç
- [ ] Personeller doğru filtreleniyor mu?
- [ ] T, H, - işaretleri doğru mu?

**WageCalculator:**
- [ ] Bir personel için maaş hesabı modalını aç
- [ ] Rakamları eski sistemle karşılaştır
- [ ] Tüm kazanç kalemleri aynı mı?
- [ ] İzin günü 30 ile sınırlı mı?

---

## 🎯 Beklenen Sonuçlar

### Kod Metrikleri
| Dosya | Önce | Sonra | İyileşme |
|-------|------|-------|----------|
| puantaj_grid/service.py | 1232 satır | ~450 satır | -782 satır |
| (yeni) excel_handler.py | - | ~750 satır | +750 satır |
| (yeni) wage_calculator.py | - | ~200 satır | +200 satır |
| **NET** | 1232 satır | 1400 satır | +168 satır ama modüler! |

### Kalite İyileştirmeleri
- ✅ Separation of concerns
- ✅ DRY principle
- ✅ Daha kolay test edilebilir
- ✅ Wage calculation merkezileştirildi
- ✅ Kod okunabilirliği arttı

---

## 📅 Takvim

**Seçenek A (2 saat):**
- Excel Handler: 1 saat
- Helper Metodlar: 1 saat

**Seçenek B (5 saat):**
- Excel Handler: 1 saat
- Helper Metodlar: 1 saat
- WageCalculator: 2 saat
- Test: 1 saat

---

## 🚨 Rollback Planı

Eğer bir şey ters giderse:

```bash
# Son commit'e geri dön
git revert HEAD

# Veya backup tag'ine dön
git reset --hard pre-optimization-backup

# Veya sadece merge'i iptal et
git merge --abort
```

---

## 📌 Notlar

- [ ] Excel handler ayrıldığında, eski API değişmemeli (backward compatible)
- [ ] Helper metodlar eklendiğinde, önce test et sonra refactor et
- [ ] WageCalculator'ı önce TEK bir yerde kullan, sonra diğer yerlere yay
- [ ] Her değişiklikten sonra manuel test yap
- [ ] Çalışan bir sistemi bozmadan optimize et

---

**Son Güncelleme:** 1 Şubat 2026  
**Durum:** 📝 Planlandı - Henüz başlanmadı
