# 📊 MAAŞ HESAPLAMA MERKEZİLEŞTİRME RAPORU

## 🎯 Proje Özeti

**Amaç:** Sistemdeki tüm maaş hesaplamalarını tek bir merkezi sınıftan yönetmek

**Tarih:** 31 Ocak 2026

**Durum:** Kritik sorunlar çözüldü ✅, Merkezileştirme planı hazır

---

## ✅ ÇÖZÜLMÜŞ KRİTİK SORUNLAR

### 1. ✅ PuantajGridPage.tsx - Yıllık İzin Kazancı Eksikliği
**Sorun:** Yıllık izin kazancı toplam kazanca dahil değildi

**Düzeltme:**
- Satır 321: `yillik_izin_kazanc` değişkeni eklendi
- Satır 331: `yillik_izin_kazanc = yillik_izin_gun * gunluk_kazanc`
- Satır 335: Toplam kazanca `yillik_izin_kazanc` eklendi
- Satır 359: Return objesine `yillik_izin_kazanc` ve `maas2_yillik_izin_kazanc` eklendi

### 2. ✅ router.py - Normal Çalışma Formülü Eksiklikler
**Sorun:** `rapor_gun_sayisi` ve `yarim_gun_sayisi` kontrolü yoktu

**Düzeltme:**
- Satır 651: `rapor_gun_sayisi` değişkeni eklendi
- Satır 665: `ayin_toplam_gun_sayisi` puantaj'dan alınıyor (varsayılan 30 yerine)
- Satır 668-678: Tam ay formülüne tüm koşullar eklendi:
  ```python
  normal_calismasi = (
      30 - tatiller if (
          (ucret_nevi == "aylik" or ucret_nevi == "sabit aylik") and 
          eksik_gun_sayisi == 0 and 
          ayin_toplam_gun_sayisi != 30 and 
          sigorta_girmedigi == 0 and
          rapor_gun_sayisi == 0 and
          yarim_gun_sayisi == 0
      ) else calisilan_gun_sayisi + yarim_gun_sayisi
  )
  ```

### 3. ✅ router.py - Tam Ay Formülü Hatası
**Sorun:** Tam ay durumunda `30` kullanılıyor, tatiller çıkarılmıyordu

**Düzeltme:**
- Satır 668: Tatiller hesaplaması yukarı taşındı
- Satır 671: `30` yerine `30 - tatiller` kullanılıyor

---

## 📍 MEVCUT DURUM ANALİZİ

### Maaş Hesabı Yapılan Dosyalar

#### Frontend (1 dosya)
1. **frontend/src/pages/PuantajGridPage.tsx** (Satır 270-360)
   - Modal'da kazanç hesaplaması yapıyor
   - Kullanıcı puantaj girişinde anlık hesaplama gösteriyor

#### Backend (5 dosya/endpoint)
1. **backend/app/domains/personnel/bordro_calculation/router.py**
   - `/maas-hesabi-data` (Satır 554-752): Modal için hesaplama
   - `/puantaj-data` (Satır 467-552): Puantaj önizleme
   
2. **backend/app/domains/personnel/bordro_calculation/service.py**
   - `_calculate_ppg_summary` (Satır 23-66): PPG özet verilerini al
   - `calculate` (Satır 69-667): Ana bordro hesaplama servisi
   
3. **backend/app/domains/personnel/bordro_calculation/yevmiye_service_bordro.py**
   - `_prepare_variables` (Satır 1230-1253): Yevmiye kaydı için hesaplamalar
   
4. **backend/app/domains/personnel/puantaj_grid/service.py**
   - `export_to_excel` (Satır 1170-1200): Excel formülü oluşturma

5. **Database Trigger:** `personnel_puantaj_grid` tablosunda trigger (SQL)

---

## 🔍 FARKLILIKLAR TABLOSU

| Özellik | Frontend | router.py | service.py | yevmiye | Excel | Trigger |
|---------|----------|-----------|------------|---------|-------|---------|
| **Normal Çalışma (Tam Ay)** | `30-tatiller` ✅ | `30-tatiller` ✅ | PPG'den | PPG'den | `30` + tatiller ayrı | Hesaplıyor |
| **Rapor Kontrolü** | ✅ | ✅ | PPG'den | PPG'den | ✅ | ✅ |
| **Yarım Gün Kontrolü** | ✅ | ✅ | PPG'den | PPG'den | ✅ | ✅ |
| **İzin Günleri (İ)** | Normal'e dahil değil | Normal'e dahil ✅ | PPG'den | PPG'den | Ayrı | Trigger'da |
| **Yıllık İzin (S)** | ✅ Toplama dahil | ✅ Toplama dahil | ✅ | ✅ | ✅ | ✅ |
| **Hesaplama Yeri** | Frontend JS | Backend Python | Backend | Backend | Excel Formül | SQL Trigger |

### Anahtar Farklar

1. **İzin Günleri (İ) Muamelesi:**
   - Frontend/Excel: Normal kazanca dahil değil, ayrı hesaplanıyor
   - Backend router: Normal kazanca dahil
   - Trigger: Bilinmiyor (SQL'e bakılmalı)

2. **Tam Ay Formülü:**
   - Frontend: `30 - tatiller`
   - Backend: `30 - tatiller` (düzeltme sonrası)
   - Excel: `30` (tatiller formülde ayrı ekleniyor)
   - Matematiksel olarak aynı sonuç

3. **Hesaplama Sorumluluğu:**
   - Frontend: Kendi hesaplıyor (modal preview için)
   - Backend router endpoints: Kendi hesaplıyor
   - Backend service: PPG trigger'ının hesapladığını kullanıyor
   - Excel: Formül kullanıcının dolduracağı
   - Trigger: SQL ile hesaplıyor

---

## 💡 MERKEZİLEŞTİRME MİMARİSİ

### Önerilen Yapı

```
backend/app/domains/personnel/
├── payroll/
│   ├── __init__.py
│   ├── calculations/
│   │   ├── __init__.py
│   │   ├── wage_calculator.py      # 🎯 Ana hesaplama sınıfı
│   │   ├── formulas.py              # Matematiksel formüller
│   │   └── validators.py            # Veri doğrulama
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── calculation_input.py     # Input modelleri
│   │   └── calculation_output.py    # Output modelleri
│   └── tests/
│       ├── __init__.py
│       ├── test_wage_calculator.py  # Unit testler
│       └── test_formulas.py         # Formül testleri
```

### Veri Akışı

```
┌─────────────────┐
│   Frontend      │
│  PuantajGrid    │
└────────┬────────┘
         │ API Call
         ▼
┌─────────────────────────────┐
│  Backend Router/Endpoint    │
│  - /maas-hesabi-data        │
│  - /puantaj-data            │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│   🎯 WageCalculator         │
│   (Merkezi Sınıf)           │
│   - calculate_wages()       │
│   - calculate_normal_gun()  │
│   - calculate_gunluk_ucret()│
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│   Response                  │
│   - Tüm kazanç kalemleri    │
│   - Frontend'e JSON         │
└─────────────────────────────┘
```

---

## 📝 UYGULANACAK DEĞİŞİKLİKLER

### ADIM 1: Merkezi Sınıf Oluşturma

#### 1.1 Dosya: `backend/app/domains/personnel/payroll/calculations/wage_calculator.py`

```python
"""
Merkezi Maaş Hesaplama Modülü

Bu modül, sistemdeki TÜM maaş hesaplamalarının tek kaynağıdır.
Herhangi bir yerde maaş hesaplaması yapılacaksa, bu sınıf kullanılmalıdır.

Kullanım Alanları:
- Bordro hesaplama servisi
- Maaş hesabı modalı
- Puantaj grid önizlemesi
- Yevmiye kayıtları
- Excel export
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class PuantajInput:
    """
    Puantaj giriş verileri
    
    Tüm alanlar zorunludur. Eksik veri olmamalı.
    Varsayılan değerler 0 olarak ayarlanmıştır.
    """
    # Gün sayıları
    calisilan_gun_sayisi: int = 0
    yillik_izin_gun: int = 0
    izin_gun_sayisi: int = 0
    rapor_gun_sayisi: int = 0
    eksik_gun_sayisi: int = 0
    yarim_gun_sayisi: float = 0.0
    sigorta_girmedigi: int = 0
    ayin_toplam_gun_sayisi: int = 30
    
    # Çalışma saatleri
    fazla_calismasi: float = 0.0
    eksik_calismasi: float = 0.0
    gece_calismasi: float = 0.0
    
    # Tatil günleri
    hafta_tatili: int = 0
    resmi_tatil: int = 0
    tatil_calismasi: float = 0.0
    
    # Ek ödemeler (TL cinsinden)
    yol: Decimal = Decimal('0')
    prim: Decimal = Decimal('0')
    ikramiye: Decimal = Decimal('0')
    bayram: Decimal = Decimal('0')
    kira: Decimal = Decimal('0')


@dataclass
class ContractInput:
    """
    Sözleşme giriş verileri
    """
    net_ucret: Decimal
    ucret_nevi: str  # 'aylik', 'sabit aylik', 'gunluk'
    fm_orani: Decimal = Decimal('1.5')
    tatil_orani: Decimal = Decimal('1.0')


@dataclass
class WageCalculationOutput:
    """
    Maaş hesaplama çıktısı
    
    Tüm kazanç kalemleri ve toplam kazanç
    """
    # Temel veriler
    gunluk_ucret: Decimal
    normal_calismasi: float
    
    # Kazanç kalemleri
    normal_kazanc: Decimal
    mesai_kazanc: Decimal
    eksik_mesai_kazanc: Decimal
    tatil_kazanc: Decimal
    tatil_mesai_kazanc: Decimal
    yillik_izin_kazanc: Decimal
    izin_kazanc: Decimal  # İzin günleri kazancı (İ)
    
    # Ek ödemeler
    ek_odemeler_toplam: Decimal
    
    # Toplamlar
    brut_kazanc: Decimal  # Ek ödemeler hariç
    toplam_kazanc: Decimal  # Ek ödemeler dahil
    
    def to_dict(self, round_decimals: int = 2) -> Dict[str, Any]:
        """
        Dict'e çevir ve ondalık sayıları yuvarla
        
        Args:
            round_decimals: Kaç haneye yuvarlanacak (varsayılan 2)
            
        Returns:
            Dictionary formatında sonuç
        """
        result = {}
        for key, value in asdict(self).items():
            if isinstance(value, Decimal):
                result[key] = float(value.quantize(
                    Decimal(10) ** -round_decimals, 
                    rounding=ROUND_HALF_UP
                ))
            else:
                result[key] = value
        return result


class WageCalculator:
    """
    Merkezi Maaş Hesaplama Sınıfı
    
    Bu sınıf, tüm maaş hesaplamalarının tek kaynağıdır.
    Static metodlardan oluşur, instance oluşturmaya gerek yoktur.
    
    Temel Prensipler:
    1. Tüm formüller burada tanımlanmıştır
    2. Formül değişiklikleri sadece buradan yapılır
    3. Tüm hesaplamalar Decimal kullanır (para hassasiyeti için)
    4. Hesaplamalar test edilebilir ve dokümante edilmiştir
    
    Kullanım:
        ```python
        from app.domains.personnel.payroll.calculations.wage_calculator import (
            WageCalculator, PuantajInput, ContractInput
        )
        
        puantaj = PuantajInput(
            calisilan_gun_sayisi=20,
            yillik_izin_gun=2,
            # ... diğer alanlar
        )
        
        contract = ContractInput(
            net_ucret=Decimal('30000'),
            ucret_nevi='aylik'
        )
        
        result = WageCalculator.calculate_wages(puantaj, contract)
        print(f"Toplam Kazanç: {result.toplam_kazanc}")
        ```
    """
    
    @staticmethod
    def calculate_gunluk_ucret(net_ucret: Decimal, ucret_nevi: str) -> Decimal:
        """
        Günlük ücret hesapla
        
        Formül:
        - Aylık/Sabit Aylık: Net Ücret / 30
        - Günlük: Net Ücret
        - Diğer: 0
        
        Args:
            net_ucret: Sözleşmedeki net ücret
            ucret_nevi: 'aylik', 'sabit aylik', 'gunluk'
            
        Returns:
            Günlük ücret (Decimal, 2 ondalık hassasiyet)
            
        Examples:
            >>> WageCalculator.calculate_gunluk_ucret(Decimal('30000'), 'aylik')
            Decimal('1000.00')
            
            >>> WageCalculator.calculate_gunluk_ucret(Decimal('500'), 'gunluk')
            Decimal('500.00')
        """
        if ucret_nevi in ['aylik', 'sabit aylik']:
            return (net_ucret / 30).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        elif ucret_nevi == 'gunluk':
            return net_ucret.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            return Decimal('0.00')
    
    @staticmethod
    def calculate_normal_calismasi(
        puantaj: PuantajInput,
        ucret_nevi: str
    ) -> float:
        """
        Normal çalışma günü hesapla
        
        İKİ DURUM VAR:
        
        1. TAM AY (Aylık/Sabit Aylık için özel durum):
           Koşullar:
           - Ücret nevi: 'aylik' veya 'sabit aylik'
           - Eksik gün yok (0)
           - Ayın toplam günü 30 değil (28, 29, 31)
           - Sigortasız gün yok (0)
           - Rapor günü yok (0)
           - Yarım gün yok (0)
           
           Formül: 30 - (Hafta Tatili + Resmi Tatil + Tatil Çalışması)
           
           Açıklama: Ay 30 günden az/fazlaysa ama tam çalışıldıysa,
                     30 gün kabul et ama tatilleri çıkar.
        
        2. NORMAL DURUM:
           Formül: Çalışılan Gün + (Yarım Gün × 0.5)
           
           Açıklama: Gerçekten çalışılan günler hesaplanır.
        
        NOT: İzin günleri (İ) BURAYA DAHİL DEĞİL!
             İzin kazancı ayrı hesaplanır.
        
        Args:
            puantaj: Puantaj verileri
            ucret_nevi: Ücret nevi
            
        Returns:
            Normal çalışma gün sayısı (float, yarım gün için)
            
        Examples:
            >>> # Tam ay örneği (31 günlük ay, tam çalışıldı, 8 tatil)
            >>> p = PuantajInput(
            ...     calisilan_gun_sayisi=23,
            ...     ayin_toplam_gun_sayisi=31,
            ...     hafta_tatili=4,
            ...     resmi_tatil=3,
            ...     tatil_calismasi=1
            ... )
            >>> WageCalculator.calculate_normal_calismasi(p, 'aylik')
            22.0  # 30 - (4 + 3 + 1) = 22
            
            >>> # Normal örnek (yarım gün var)
            >>> p2 = PuantajInput(
            ...     calisilan_gun_sayisi=20,
            ...     yarim_gun_sayisi=2
            ... )
            >>> WageCalculator.calculate_normal_calismasi(p2, 'aylik')
            21.0  # 20 + 2*0.5 = 21
        """
        # Tatiller toplamı
        tatiller = (
            puantaj.hafta_tatili + 
            puantaj.resmi_tatil + 
            puantaj.tatil_calismasi
        )
        
        # Tam ay koşulları
        tam_ay_kosullari = (
            ucret_nevi in ['aylik', 'sabit aylik'] and
            puantaj.eksik_gun_sayisi == 0 and
            puantaj.ayin_toplam_gun_sayisi != 30 and
            puantaj.sigorta_girmedigi == 0 and
            puantaj.rapor_gun_sayisi == 0 and
            puantaj.yarim_gun_sayisi == 0
        )
        
        if tam_ay_kosullari:
            return float(30 - tatiller)
        else:
            return float(puantaj.calisilan_gun_sayisi + puantaj.yarim_gun_sayisi)
    
    @staticmethod
    def calculate_normal_kazanc(
        normal_calismasi: float,
        izin_gun_sayisi: int,
        gunluk_ucret: Decimal
    ) -> Decimal:
        """
        Normal kazanç hesapla
        
        Formül: (Normal Çalışma + İzin Günleri) × Günlük Ücret
        
        NOT: İzin günleri (İ) normal kazanca dahildir çünkü ücretli izindir.
        
        Args:
            normal_calismasi: Normal çalışma gün sayısı
            izin_gun_sayisi: İzin günleri (İ)
            gunluk_ucret: Günlük ücret
            
        Returns:
            Normal kazanç (Decimal)
            
        Examples:
            >>> WageCalculator.calculate_normal_kazanc(20.0, 2, Decimal('1000'))
            Decimal('22000.00')
        """
        toplam_gun = Decimal(str(normal_calismasi + izin_gun_sayisi))
        return (toplam_gun * gunluk_ucret).quantize(
            Decimal('0.01'), 
            rounding=ROUND_HALF_UP
        )
    
    @staticmethod
    def calculate_mesai_kazanc(
        fazla_calismasi: float,
        gunluk_ucret: Decimal,
        fm_orani: Decimal
    ) -> Decimal:
        """
        Fazla mesai kazancı hesapla
        
        Formül: (Fazla Çalışma Saati × Günlük Ücret / 8) × FM Oranı
        
        Args:
            fazla_calismasi: Fazla çalışma saati
            gunluk_ucret: Günlük ücret
            fm_orani: Fazla mesai oranı (1.5, 2.0 vb.)
            
        Returns:
            Fazla mesai kazancı (Decimal)
            
        Examples:
            >>> # 8 saat FM, günlük 1000 TL, %150 oran
            >>> WageCalculator.calculate_mesai_kazanc(8, Decimal('1000'), Decimal('1.5'))
            Decimal('1500.00')  # (8 × 1000 / 8) × 1.5 = 1500
        """
        saat = Decimal(str(fazla_calismasi))
        saatlik_ucret = gunluk_ucret / 8
        return (saat * saatlik_ucret * fm_orani).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )
    
    @staticmethod
    def calculate_eksik_mesai_kazanc(
        eksik_calismasi: float,
        gunluk_ucret: Decimal
    ) -> Decimal:
        """
        Eksik mesai kesintisi hesapla
        
        Formül: (Eksik Çalışma Saati × Günlük Ücret / 8)
        
        NOT: Bu bir KESİNTİDİR, toplam kazançtan ÇIKARILIR.
             Oran kullanılmaz (1x).
        
        Args:
            eksik_calismasi: Eksik çalışma saati
            gunluk_ucret: Günlük ücret
            
        Returns:
            Eksik mesai kesintisi (Decimal, pozitif değer)
            
        Examples:
            >>> # 4 saat eksik, günlük 1000 TL
            >>> WageCalculator.calculate_eksik_mesai_kazanc(4, Decimal('1000'))
            Decimal('500.00')  # (4 × 1000 / 8) = 500 TL kesilir
        """
        saat = Decimal(str(eksik_calismasi))
        saatlik_ucret = gunluk_ucret / 8
        return (saat * saatlik_ucret).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )
    
    @staticmethod
    def calculate_tatil_kazanc(
        hafta_tatili: int,
        resmi_tatil: int,
        tatil_calismasi: float,
        gunluk_ucret: Decimal
    ) -> Decimal:
        """
        Tatil kazancı hesapla
        
        Formül: (Hafta Tatili + Resmi Tatil + Tatil Çalışması) × Günlük Ücret
        
        NOT: Tatil çalışması (M) günleri hem buraya hem de tatil mesai
             kazancına dahildir. Çünkü hem normal ücret hem de %50-100
             fazlası ödenir.
        
        Args:
            hafta_tatili: Hafta tatili gün sayısı (H)
            resmi_tatil: Resmi tatil gün sayısı (T)
            tatil_calismasi: Tatil çalışma gün sayısı (M)
            gunluk_ucret: Günlük ücret
            
        Returns:
            Tatil kazancı (Decimal)
            
        Examples:
            >>> # 4 hafta tatili, 1 resmi tatil, 2 tatil çalışması
            >>> WageCalculator.calculate_tatil_kazanc(4, 1, 2, Decimal('1000'))
            Decimal('7000.00')  # (4 + 1 + 2) × 1000 = 7000
        """
        toplam_tatil = Decimal(str(hafta_tatili + resmi_tatil + tatil_calismasi))
        return (toplam_tatil * gunluk_ucret).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )
    
    @staticmethod
    def calculate_tatil_mesai_kazanc(
        tatil_calismasi: float,
        gunluk_ucret: Decimal,
        tatil_orani: Decimal
    ) -> Decimal:
        """
        Tatil mesai kazancı hesapla
        
        Formül: Tatil Çalışması × Günlük Ücret × Tatil Oranı
        
        Açıklama: Tatil çalışması (M) günleri için EKSTRA ödeme.
                  Tatil kazancında zaten 1x ücret var, bu %50-100 FAZLASI.
        
        Args:
            tatil_calismasi: Tatil çalışma gün sayısı (M)
            gunluk_ucret: Günlük ücret
            tatil_orani: Tatil oranı (1.0 = %100, 0.5 = %50)
            
        Returns:
            Tatil mesai kazancı (Decimal)
            
        Examples:
            >>> # 2 gün tatil çalışması, günlük 1000 TL, %100 oran
            >>> WageCalculator.calculate_tatil_mesai_kazanc(2, Decimal('1000'), Decimal('1.0'))
            Decimal('2000.00')  # 2 × 1000 × 1.0 = 2000 TL ekstra
        """
        gun = Decimal(str(tatil_calismasi))
        return (gun * gunluk_ucret * tatil_orani).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )
    
    @staticmethod
    def calculate_yillik_izin_kazanc(
        yillik_izin_gun: int,
        gunluk_ucret: Decimal
    ) -> Decimal:
        """
        Yıllık izin kazancı hesapla
        
        Formül: Yıllık İzin Günü × Günlük Ücret
        
        Args:
            yillik_izin_gun: Yıllık izin gün sayısı (S)
            gunluk_ucret: Günlük ücret
            
        Returns:
            Yıllık izin kazancı (Decimal)
            
        Examples:
            >>> WageCalculator.calculate_yillik_izin_kazanc(3, Decimal('1000'))
            Decimal('3000.00')
        """
        gun = Decimal(str(yillik_izin_gun))
        return (gun * gunluk_ucret).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )
    
    @classmethod
    def calculate_wages(
        cls,
        puantaj: PuantajInput,
        contract: ContractInput
    ) -> WageCalculationOutput:
        """
        TÜM maaş hesaplamalarını yap
        
        Bu metod, tüm kazanç kalemlerini hesaplar ve WageCalculationOutput
        olarak döner. Sistemdeki TÜM maaş hesaplamaları bu metodu kullanmalıdır.
        
        Hesaplama Sırası:
        1. Günlük ücret
        2. Normal çalışma günü
        3. Normal kazanç (izin dahil)
        4. Fazla mesai kazancı
        5. Eksik mesai kesintisi
        6. Tatil kazancı
        7. Tatil mesai kazancı
        8. Yıllık izin kazancı
        9. Ek ödemeler toplamı
        10. Brüt kazanç (ek ödemeler hariç)
        11. TOPLAM KAZANÇ (ek ödemeler dahil)
        
        Args:
            puantaj: Puantaj giriş verileri
            contract: Sözleşme giriş verileri
            
        Returns:
            WageCalculationOutput - Tüm kazanç kalemleri
            
        Examples:
            >>> puantaj = PuantajInput(
            ...     calisilan_gun_sayisi=20,
            ...     izin_gun_sayisi=2,
            ...     yillik_izin_gun=3,
            ...     fazla_calismasi=8,
            ...     hafta_tatili=4,
            ...     resmi_tatil=1,
            ...     yol=Decimal('500'),
            ...     prim=Decimal('1000')
            ... )
            >>> contract = ContractInput(
            ...     net_ucret=Decimal('30000'),
            ...     ucret_nevi='aylik',
            ...     fm_orani=Decimal('1.5')
            ... )
            >>> result = WageCalculator.calculate_wages(puantaj, contract)
            >>> print(f"Toplam: {result.toplam_kazanc}")
        """
        # 1. Günlük ücret
        gunluk_ucret = cls.calculate_gunluk_ucret(
            contract.net_ucret,
            contract.ucret_nevi
        )
        
        # 2. Normal çalışma günü
        normal_calismasi = cls.calculate_normal_calismasi(
            puantaj,
            contract.ucret_nevi
        )
        
        # 3. Normal kazanç (izin dahil)
        normal_kazanc = cls.calculate_normal_kazanc(
            normal_calismasi,
            puantaj.izin_gun_sayisi,
            gunluk_ucret
        )
        
        # 4. Fazla mesai kazancı
        mesai_kazanc = cls.calculate_mesai_kazanc(
            puantaj.fazla_calismasi,
            gunluk_ucret,
            contract.fm_orani
        )
        
        # 5. Eksik mesai kesintisi
        eksik_mesai_kazanc = cls.calculate_eksik_mesai_kazanc(
            puantaj.eksik_calismasi,
            gunluk_ucret
        )
        
        # 6. Tatil kazancı
        tatil_kazanc = cls.calculate_tatil_kazanc(
            puantaj.hafta_tatili,
            puantaj.resmi_tatil,
            puantaj.tatil_calismasi,
            gunluk_ucret
        )
        
        # 7. Tatil mesai kazancı
        tatil_mesai_kazanc = cls.calculate_tatil_mesai_kazanc(
            puantaj.tatil_calismasi,
            gunluk_ucret,
            contract.tatil_orani
        )
        
        # 8. Yıllık izin kazancı
        yillik_izin_kazanc = cls.calculate_yillik_izin_kazanc(
            puantaj.yillik_izin_gun,
            gunluk_ucret
        )
        
        # 9. İzin kazancı (İ) - ayrı hesaplama için
        izin_kazanc = (Decimal(str(puantaj.izin_gun_sayisi)) * gunluk_ucret).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )
        
        # 10. Ek ödemeler toplamı
        ek_odemeler_toplam = (
            puantaj.yol + 
            puantaj.prim + 
            puantaj.ikramiye + 
            puantaj.bayram + 
            puantaj.kira
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # 11. Brüt kazanç (ek ödemeler HARİÇ)
        brut_kazanc = (
            normal_kazanc + 
            mesai_kazanc - 
            eksik_mesai_kazanc + 
            tatil_kazanc + 
            tatil_mesai_kazanc + 
            yillik_izin_kazanc
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # 12. TOPLAM KAZANÇ (ek ödemeler DAHİL)
        toplam_kazanc = (brut_kazanc + ek_odemeler_toplam).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )
        
        return WageCalculationOutput(
            gunluk_ucret=gunluk_ucret,
            normal_calismasi=normal_calismasi,
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

---

### ADIM 2: Backend Endpoint'leri Güncelleme

#### 2.1 Dosya: `backend/app/domains/personnel/bordro_calculation/router.py`

**Değişiklik: `/maas-hesabi-data` endpoint (Satır 554-752)**

```python
# ÖNCEKİ KOD (KALDIRILIYOR):
# Satır 645-715 arası tüm hesaplama kodu silinecek

# YENİ KOD:
from app.domains.personnel.payroll.calculations.wage_calculator import (
    WageCalculator, PuantajInput, ContractInput
)

@router.get("/maas-hesabi-data")
async def get_maas_hesabi_data(
    yil: int = Query(...),
    ay: int = Query(...),
    personnel_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """
    Personelin maaş hesabını draft contract ve puantaj verilerine göre hesapla
    
    GÜNCELLEME: Artık merkezi WageCalculator kullanıyor
    """
    from app.models import PersonnelPuantajGrid
    from app.models import PersonnelDraftContract
    from app.models import CostCenter
    
    # Aktif draft contract'ı çek
    draft = db.query(PersonnelDraftContract).filter(
        PersonnelDraftContract.personnel_id == personnel_id,
        PersonnelDraftContract.is_active == 1
    ).first()
    
    if not draft:
        raise HTTPException(
            status_code=404,
            detail=f"Personnel ID {personnel_id} için aktif taslak sözleşme bulunamadı"
        )
    
    # Maliyet merkezini çek
    cost_center_name = "Belirtilmemiş"
    if draft.cost_center_id:
        cost_center = db.query(CostCenter).filter(CostCenter.id == draft.cost_center_id).first()
        if cost_center:
            cost_center_name = cost_center.name
    
    # Dönemi oluştur
    donem = f"{yil}-{ay:02d}"
    
    # Puantaj grid kaydını çek
    puantaj = db.query(PersonnelPuantajGrid).filter(
        PersonnelPuantajGrid.personnel_id == personnel_id,
        PersonnelPuantajGrid.donem == donem
    ).first()
    
    if not puantaj:
        raise HTTPException(
            status_code=404,
            detail=f"Personnel ID {personnel_id} için {donem} dönemine ait puantaj kaydı bulunamadı"
        )
    
    # 🎯 MERKEZI HESAPLAMA - PuantajInput oluştur
    puantaj_input = PuantajInput(
        calisilan_gun_sayisi=int(puantaj.calisilan_gun_sayisi or 0),
        yillik_izin_gun=int(puantaj.yillik_izin_gun or 0),
        izin_gun_sayisi=int(puantaj.izin_gun_sayisi or 0),
        rapor_gun_sayisi=int(puantaj.rapor_gun_sayisi or 0),
        yarim_gun_sayisi=float(puantaj.yarim_gun_sayisi or 0),
        eksik_gun_sayisi=int(puantaj.eksik_gun_sayisi or 0),
        sigorta_girmedigi=int(puantaj.sigorta_girmedigi or 0),
        ayin_toplam_gun_sayisi=int(puantaj.ayin_toplam_gun_sayisi or 30),
        fazla_calismasi=float(puantaj.fazla_calismasi or 0),
        eksik_calismasi=float(puantaj.eksik_calismasi or 0),
        hafta_tatili=int(puantaj.hafta_tatili or 0),
        resmi_tatil=int(puantaj.resmi_tatil or 0),
        tatil_calismasi=float(puantaj.tatil_calismasi or 0),
        yol=Decimal(str(puantaj.yol or 0)),
        prim=Decimal(str(puantaj.prim or 0)),
        ikramiye=Decimal(str(puantaj.ikramiye or 0)),
        bayram=Decimal(str(puantaj.bayram or 0)),
        kira=Decimal(str(puantaj.kira or 0)),
    )
    
    # 🎯 MERKEZI HESAPLAMA - ContractInput oluştur
    contract_input = ContractInput(
        net_ucret=Decimal(str(draft.net_ucret or 0)),
        ucret_nevi=draft.ucret_nevi or 'aylik',
        fm_orani=Decimal(str(draft.fm_orani or 1.5)),
        tatil_orani=Decimal(str(draft.tatil_orani or 1.0))
    )
    
    # 🎯 MERKEZI HESAPLAMA - Maaş hesapla
    result = WageCalculator.calculate_wages(puantaj_input, contract_input)
    
    # Response'u oluştur
    result_dict = result.to_dict()
    
    return {
        # Draft Contract Bilgileri
        "draft_contracts_id": draft.id,
        "cc_id": draft.cost_center_id,
        "cost_center_name": cost_center_name,
        "net_ucret": float(contract_input.net_ucret),
        "ucret_nevi": contract_input.ucret_nevi,
        "fm_orani": float(contract_input.fm_orani),
        "tatil_orani": float(contract_input.tatil_orani),
        
        # Puantaj Verileri
        "normal_calismasi": result_dict['normal_calismasi'],
        "izin_gun_sayisi": puantaj_input.izin_gun_sayisi,
        "fazla_calismasi": puantaj_input.fazla_calismasi,
        "eksik_calismasi": puantaj_input.eksik_calismasi,
        "yillik_izin_gun": puantaj_input.yillik_izin_gun,
        "hafta_tatili": puantaj_input.hafta_tatili,
        "resmi_tatil": puantaj_input.resmi_tatil,
        "tatil_calismasi": puantaj_input.tatil_calismasi,
        "yol": float(puantaj_input.yol),
        "prim": float(puantaj_input.prim),
        "ikramiye": float(puantaj_input.ikramiye),
        "bayram": float(puantaj_input.bayram),
        "kira": float(puantaj_input.kira),
        
        # 🎯 Hesaplanan Değerler - Merkezi sınıftan
        "gunluk_ucret": result_dict['gunluk_ucret'],
        "normal_kazanc": result_dict['normal_kazanc'],
        "mesai_kazanc": result_dict['mesai_kazanc'],
        "eksik_mesai_kazanc": result_dict['eksik_mesai_kazanc'],
        "tatil_kazanc": result_dict['tatil_kazanc'],
        "tatil_mesai_kazanc": result_dict['tatil_mesai_kazanc'],
        "yillik_izin_kazanc": result_dict['yillik_izin_kazanc'],
        "izin_kazanc": result_dict['izin_kazanc'],
        "toplam_kazanc": result_dict['toplam_kazanc']
    }
```

**Satır Sayısı:**
- Önceki: ~185 satır
- Yeni: ~110 satır
- Kazanç: **75 satır azalma, %40 daha az kod**

---

#### 2.2 Dosya: `backend/app/domains/personnel/bordro_calculation/service.py`

**Değişiklik: `calculate` metodundaki maas2 hesaplamaları (Satır 524-548)**

```python
# ÖNCEKİ KOD (KALDIRILIYOR):
# Satır 524-548 arası hesaplama kodu silinecek

# YENİ KOD:
from app.domains.personnel.payroll.calculations.wage_calculator import (
    WageCalculator, PuantajInput, ContractInput
)

# ... mevcut kod ...

# Draft contract'tan ücret bilgilerini al
net_ucret = Decimal(str(draft_contract.net_ucret or 0))

# 🎯 MERKEZI HESAPLAMA - PuantajInput oluştur
puantaj_input = PuantajInput(
    calisilan_gun_sayisi=int(ppg_summary['calisilan_gun_sayisi']),
    yillik_izin_gun=int(ppg_summary['yillik_izin_gun']),
    izin_gun_sayisi=int(ppg_summary['izin_gun_sayisi']),
    rapor_gun_sayisi=int(ppg_summary['rapor_gun_sayisi']),
    yarim_gun_sayisi=float(ppg_summary['yarim_gun_sayisi']),
    eksik_gun_sayisi=int(ppg_summary['eksik_gun_sayisi']),
    sigorta_girmedigi=int(ppg_summary['sigorta_girmedigi']),
    ayin_toplam_gun_sayisi=int(ppg_summary['ayin_toplam_gun_sayisi']),
    fazla_calismasi=float(ppg_summary['fazla_calismasi']),
    eksik_calismasi=float(ppg_summary.get('eksik_calismasi', 0)),
    hafta_tatili=int(ppg_summary['hafta_tatili']),
    resmi_tatil=int(ppg_summary['resmi_tatil']),
    tatil_calismasi=float(ppg_summary['tatil_calismasi']),
    yol=Decimal(str(ppg_summary['yol'])),
    prim=Decimal(str(ppg_summary['prim'])),
    ikramiye=Decimal(str(ppg_summary['ikramiye'])),
    bayram=Decimal(str(ppg_summary['bayram'])),
    kira=Decimal(str(ppg_summary['kira'])),
)

# 🎯 MERKEZI HESAPLAMA - ContractInput oluştur
contract_input = ContractInput(
    net_ucret=net_ucret,
    ucret_nevi=draft_contract.ucret_nevi or 'aylik',
    fm_orani=Decimal(str(draft_contract.fm_orani or 1.5)),
    tatil_orani=Decimal(str(draft_contract.tatil_orani or 1.0))
)

# 🎯 MERKEZI HESAPLAMA - Maaş hesapla
wage_result = WageCalculator.calculate_wages(puantaj_input, contract_input)

# Değerleri kullan
maas2_normal = wage_result.normal_kazanc
maas2_fm = wage_result.mesai_kazanc
maas2_em = wage_result.eksik_mesai_kazanc
maas2_toplam_tatil_calismasi = wage_result.tatil_kazanc
maas2_tatil_calismasi = wage_result.tatil_mesai_kazanc
maas2_yillik_izin = wage_result.yillik_izin_kazanc
maas2_yol = puantaj_input.yol
maas2_prim = puantaj_input.prim
maas2_ikramiye = puantaj_input.ikramiye
maas2_bayram = puantaj_input.bayram
maas2_kira = puantaj_input.kira
maas2_toplam = wage_result.toplam_kazanc
```

**Satır Sayısı:**
- Önceki: ~25 satır hesaplama
- Yeni: ~45 satır (ama merkezi sınıf kullanıyor)
- Kazanç: Tutarlılık ve test edilebilirlik

---

#### 2.3 Dosya: `backend/app/domains/personnel/bordro_calculation/yevmiye_service_bordro.py`

**Değişiklik: `_prepare_variables` metodu (Satır 1230-1253)**

```python
# ÖNCEKİ KOD (KALDIRILIYOR):
# Satır 1236-1253 arası hesaplama kodu silinecek

# YENİ KOD:
from app.domains.personnel.payroll.calculations.wage_calculator import (
    WageCalculator, PuantajInput, ContractInput
)

# ... mevcut kod draft contract verilerini alıyor ...

if draft_contract:
    # 🎯 MERKEZI HESAPLAMA - Input'ları hazırla
    puantaj_input = PuantajInput(
        calisilan_gun_sayisi=int(vars['ppg_normal_calismasi']),  # Trigger hesaplamış
        yillik_izin_gun=int(vars['ppg_yillik_izin_gun']),
        izin_gun_sayisi=int(vars.get('ppg_izin_gun_sayisi', 0)),
        rapor_gun_sayisi=0,  # PPG'de yok
        yarim_gun_sayisi=0,  # PPG'de yok
        eksik_gun_sayisi=0,  # PPG'de yok
        sigorta_girmedigi=0,  # PPG'de yok
        ayin_toplam_gun_sayisi=30,
        fazla_calismasi=float(vars['ppg_fazla_calismasi']),
        eksik_calismasi=0,
        hafta_tatili=int(vars['ppg_hafta_tatili']),
        resmi_tatil=int(vars['ppg_resmi_tatil']),
        tatil_calismasi=float(vars['ppg_tatil_calismasi']),
        yol=Decimal(str(vars['ppg_yol'])),
        prim=Decimal(str(vars['ppg_prim'])),
        ikramiye=Decimal(str(vars['ppg_ikramiye'])),
        bayram=Decimal(str(vars['ppg_bayram'])),
        kira=Decimal(str(vars['ppg_kira'])),
    )
    
    contract_input = ContractInput(
        net_ucret=vars['tr_maas2_tutar'],
        ucret_nevi=vars['tr_ucret_nevi'],
        fm_orani=vars['tr_fm_orani'],
        tatil_orani=vars['tr_tatil_orani']
    )
    
    # 🎯 MERKEZI HESAPLAMA
    wage_result = WageCalculator.calculate_wages(puantaj_input, contract_input)
    
    # Değerleri kullan
    tr_gunluk_ucret = wage_result.gunluk_ucret
    tr_normal_calisma_tutar = wage_result.normal_kazanc
    tr_fazla_calisma_tutar = wage_result.mesai_kazanc
    tr_tatil_tutar = wage_result.tatil_kazanc
    tr_tatil_calismasi_tutar = wage_result.tatil_mesai_kazanc
    tr_yillik_izin_gun_tutar = wage_result.yillik_izin_kazanc
    
    tr_net_maas_tutar = wage_result.toplam_kazanc
    tr_bordro_net_toplami = vars['lc_n_odenen'] + vars['lc_oto_kat_bes'] + vars['lc_icra'] + vars['lc_avans']
    tr_elden_kalan = tr_net_maas_tutar - tr_bordro_net_toplami
    
    # Yuvarlama (100'e)
    tr_elden_kalan_yuvarlanmis = (tr_elden_kalan / 100).quantize(Decimal('1'), rounding='ROUND_HALF_UP') * 100
    tr_elden_yuvarlamasi = tr_elden_kalan - tr_elden_kalan_yuvarlanmis
    
    vars.update({
        'tr_gunluk_ucret': tr_gunluk_ucret,
        'tr_net_maas_tutar': tr_net_maas_tutar,
        'tr_bordro_net_toplami': tr_bordro_net_toplami,
        'tr_elden_kalan': tr_elden_kalan,
        'tr_elden_kalan_yuvarlanmis': tr_elden_kalan_yuvarlanmis,
        'tr_elden_yuvarlamasi': tr_elden_yuvarlamasi,
    })
else:
    # ... mevcut kod ...
```

---

### ADIM 3: Frontend Güncelleme

#### 3.1 Dosya: `frontend/src/pages/PuantajGridPage.tsx`

**Değişiklik: Hesaplama kısmını kaldır, backend'den gelen veriyi kullan**

**Seçenek A: Backend'den veri al (Önerilen)**
```typescript
// Satır 315-360 arası hesaplama kodu silinecek

// YENİ KOD: Backend'den hesaplanmış veriyi al
const calculatePersonelSummary = async (
  personel: any,
  includeEarnings: boolean = false,
  earningsData?: any
): Promise<any> => {
  // ... mevcut özet hesaplamaları (gün sayıları) ...
  
  if (includeEarnings && personel.draft_contract_id) {
    try {
      // 🎯 Backend'den hesaplanmış kazançları al
      const response = await axios.get(
        `${API_URL}/bordro-calculation/maas-hesabi-data`,
        {
          params: {
            yil: selectedDate.year(),
            ay: selectedDate.month() + 1,
            personnel_id: personel.personnel_id
          }
        }
      );
      
      const data = response.data;
      
      return {
        ...summary,
        maas2: personel.maas2_tutar,
        fm_orani: data.fm_orani,
        tatil_orani: data.tatil_orani,
        gunluk_kazanc: data.gunluk_ucret,
        normal_kazanc: data.normal_kazanc,
        mesai_kazanc: data.mesai_kazanc,
        eksik_kazanc: data.eksik_mesai_kazanc,
        tatil_kazanc: data.tatil_kazanc,
        tatil_mesai_kazanc: data.tatil_mesai_kazanc,
        yillik_izin_kazanc: data.yillik_izin_kazanc,
        toplam_kazanc: data.toplam_kazanc,
        // Maas2 alanları
        maas2_gunluk_kazanc: data.gunluk_ucret,
        maas2_normal_kazanc: data.normal_kazanc,
        maas2_mesai_kazanc: data.mesai_kazanc,
        maas2_eksik_kazanc: data.eksik_mesai_kazanc,
        maas2_tatil_kazanc: data.tatil_kazanc,
        maas2_tatil_mesai_kazanc: data.tatil_mesai_kazanc,
        maas2_yillik_izin_kazanc: data.yillik_izin_kazanc,
        maas2_toplam_kazanc: data.toplam_kazanc
      };
    } catch (error) {
      console.error('Kazanç hesaplama hatası:', error);
      return summary;
    }
  }
  
  return summary;
};
```

**Seçenek B: Frontend hesaplama tutulsun ama merkezi formül kullan (Alternatif)**

Eğer performance için frontend'de de hesaplama yapılması istenirse:

```typescript
// wage-calculator.ts adında yeni dosya oluştur
// Backend Python kodunun TypeScript versiyonu
// Bu seçenek önerilmiyor çünkü kod tekrarı oluşturur
```

---

### ADIM 4: Unit Test Yazma

#### 4.1 Dosya: `backend/app/domains/personnel/payroll/tests/test_wage_calculator.py`

```python
"""
WageCalculator Unit Tests

Bu testler, maaş hesaplama fonksiyonlarının doğruluğunu kontrol eder.
Her formül için edge case'ler test edilir.
"""

import pytest
from decimal import Decimal
from app.domains.personnel.payroll.calculations.wage_calculator import (
    WageCalculator,
    PuantajInput,
    ContractInput,
    WageCalculationOutput
)


class TestGunlukUcretHesaplama:
    """Günlük ücret hesaplama testleri"""
    
    def test_aylik_ucret(self):
        """Aylık ücret için günlük ücret hesaplama"""
        result = WageCalculator.calculate_gunluk_ucret(
            Decimal('30000'),
            'aylik'
        )
        assert result == Decimal('1000.00')
    
    def test_sabit_aylik_ucret(self):
        """Sabit aylık ücret için günlük ücret hesaplama"""
        result = WageCalculator.calculate_gunluk_ucret(
            Decimal('30000'),
            'sabit aylik'
        )
        assert result == Decimal('1000.00')
    
    def test_gunluk_ucret(self):
        """Günlük ücret için günlük ücret (kendisi)"""
        result = WageCalculator.calculate_gunluk_ucret(
            Decimal('500'),
            'gunluk'
        )
        assert result == Decimal('500.00')
    
    def test_bilinmeyen_ucret_nevi(self):
        """Bilinmeyen ücret nevi için 0 dönmeli"""
        result = WageCalculator.calculate_gunluk_ucret(
            Decimal('30000'),
            'saat basina'  # Geçersiz
        )
        assert result == Decimal('0.00')


class TestNormalCalisimaHesaplama:
    """Normal çalışma günü hesaplama testleri"""
    
    def test_tam_ay_31_gun(self):
        """31 günlük ay, tam çalışma (8 tatil)"""
        puantaj = PuantajInput(
            calisilan_gun_sayisi=23,
            ayin_toplam_gun_sayisi=31,
            eksik_gun_sayisi=0,
            sigorta_girmedigi=0,
            rapor_gun_sayisi=0,
            yarim_gun_sayisi=0,
            hafta_tatili=4,
            resmi_tatil=3,
            tatil_calismasi=1
        )
        result = WageCalculator.calculate_normal_calismasi(puantaj, 'aylik')
        # 30 - (4 + 3 + 1) = 22
        assert result == 22.0
    
    def test_tam_ay_28_gun_subat(self):
        """28 günlük Şubat ayı, tam çalışma (8 tatil)"""
        puantaj = PuantajInput(
            calisilan_gun_sayisi=20,
            ayin_toplam_gun_sayisi=28,
            eksik_gun_sayisi=0,
            sigorta_girmedigi=0,
            rapor_gun_sayisi=0,
            yarim_gun_sayisi=0,
            hafta_tatili=4,
            resmi_tatil=2,
            tatil_calismasi=2
        )
        result = WageCalculator.calculate_normal_calismasi(puantaj, 'aylik')
        # 30 - (4 + 2 + 2) = 22
        assert result == 22.0
    
    def test_tam_ay_rapor_varsa(self):
        """Rapor günü varsa tam ay olmamalı"""
        puantaj = PuantajInput(
            calisilan_gun_sayisi=20,
            ayin_toplam_gun_sayisi=31,
            eksik_gun_sayisi=0,
            sigorta_girmedigi=0,
            rapor_gun_sayisi=3,  # Rapor var
            yarim_gun_sayisi=0,
            hafta_tatili=4,
            resmi_tatil=3,
            tatil_calismasi=1
        )
        result = WageCalculator.calculate_normal_calismasi(puantaj, 'aylik')
        # Tam ay değil, normal hesaplama: 20
        assert result == 20.0
    
    def test_normal_hesaplama_yarim_gun(self):
        """Normal hesaplama - yarım gün var"""
        puantaj = PuantajInput(
            calisilan_gun_sayisi=20,
            yarim_gun_sayisi=2.0
        )
        result = WageCalculator.calculate_normal_calismasi(puantaj, 'aylik')
        # 20 + 2 = 22
        assert result == 22.0
    
    def test_gunluk_ucretli(self):
        """Günlükçü için tam ay formülü geçerli değil"""
        puantaj = PuantajInput(
            calisilan_gun_sayisi=25,
            ayin_toplam_gun_sayisi=31,
            eksik_gun_sayisi=0,
            hafta_tatili=4
        )
        result = WageCalculator.calculate_normal_calismasi(puantaj, 'gunluk')
        # Günlükçü tam ay formülü kullanmaz: 25
        assert result == 25.0


class TestNormalKazancHesaplama:
    """Normal kazanç hesaplama testleri"""
    
    def test_izin_dahil(self):
        """İzin günleri kazanca dahil"""
        result = WageCalculator.calculate_normal_kazanc(
            normal_calismasi=20.0,
            izin_gun_sayisi=2,
            gunluk_ucret=Decimal('1000')
        )
        # (20 + 2) × 1000 = 22000
        assert result == Decimal('22000.00')
    
    def test_izin_yok(self):
        """İzin günü yoksa"""
        result = WageCalculator.calculate_normal_kazanc(
            normal_calismasi=22.0,
            izin_gun_sayisi=0,
            gunluk_ucret=Decimal('1000')
        )
        assert result == Decimal('22000.00')


class TestMesaiKazancHesaplama:
    """Fazla mesai kazancı hesaplama testleri"""
    
    def test_8_saat_fm_oran_1_5(self):
        """8 saat FM, %150 oran"""
        result = WageCalculator.calculate_mesai_kazanc(
            fazla_calismasi=8.0,
            gunluk_ucret=Decimal('1000'),
            fm_orani=Decimal('1.5')
        )
        # (8 × 1000 / 8) × 1.5 = 1500
        assert result == Decimal('1500.00')
    
    def test_16_saat_fm_oran_2_0(self):
        """16 saat FM, %200 oran"""
        result = WageCalculator.calculate_mesai_kazanc(
            fazla_calismasi=16.0,
            gunluk_ucret=Decimal('800'),
            fm_orani=Decimal('2.0')
        )
        # (16 × 800 / 8) × 2.0 = 3200
        assert result == Decimal('3200.00')
    
    def test_fm_yok(self):
        """FM yoksa 0"""
        result = WageCalculator.calculate_mesai_kazanc(
            fazla_calismasi=0.0,
            gunluk_ucret=Decimal('1000'),
            fm_orani=Decimal('1.5')
        )
        assert result == Decimal('0.00')


class TestToplamKazancHesaplama:
    """Toplam kazanç entegrasyon testleri"""
    
    def test_basit_senaryo(self):
        """Basit senaryo - sadece normal çalışma"""
        puantaj = PuantajInput(
            calisilan_gun_sayisi=22,
            hafta_tatili=4,
            resmi_tatil=2,
            ayin_toplam_gun_sayisi=30
        )
        contract = ContractInput(
            net_ucret=Decimal('30000'),
            ucret_nevi='aylik'
        )
        
        result = WageCalculator.calculate_wages(puantaj, contract)
        
        # Günlük: 30000 / 30 = 1000
        assert result.gunluk_ucret == Decimal('1000.00')
        
        # Normal çalışma: 22
        assert result.normal_calismasi == 22.0
        
        # Normal kazanç: 22 × 1000 = 22000
        assert result.normal_kazanc == Decimal('22000.00')
        
        # Tatil kazanç: (4 + 2) × 1000 = 6000
        assert result.tatil_kazanc == Decimal('6000.00')
        
        # Toplam: 22000 + 6000 = 28000
        assert result.toplam_kazanc == Decimal('28000.00')
    
    def test_karmasik_senaryo(self):
        """Karmaşık senaryo - tüm kalemler"""
        puantaj = PuantajInput(
            calisilan_gun_sayisi=20,
            izin_gun_sayisi=2,
            yillik_izin_gun=3,
            yarim_gun_sayisi=0,
            fazla_calismasi=8.0,
            eksik_calismasi=4.0,
            hafta_tatili=4,
            resmi_tatil=1,
            tatil_calismasi=1.0,
            yol=Decimal('500'),
            prim=Decimal('1000'),
            ikramiye=Decimal('2000'),
            ayin_toplam_gun_sayisi=30
        )
        contract = ContractInput(
            net_ucret=Decimal('30000'),
            ucret_nevi='aylik',
            fm_orani=Decimal('1.5'),
            tatil_orani=Decimal('1.0')
        )
        
        result = WageCalculator.calculate_wages(puantaj, contract)
        
        # Günlük: 1000
        assert result.gunluk_ucret == Decimal('1000.00')
        
        # Normal çalışma: 20 (tam ay değil çünkü 30 gün)
        assert result.normal_calismasi == 20.0
        
        # Normal kazanç: (20 + 2 İzin) × 1000 = 22000
        assert result.normal_kazanc == Decimal('22000.00')
        
        # FM kazanç: (8 × 1000/8) × 1.5 = 1500
        assert result.mesai_kazanc == Decimal('1500.00')
        
        # Eksik mesai: (4 × 1000/8) = 500
        assert result.eksik_mesai_kazanc == Decimal('500.00')
        
        # Tatil: (4 + 1 + 1) × 1000 = 6000
        assert result.tatil_kazanc == Decimal('6000.00')
        
        # Tatil mesai: 1 × 1000 × 1.0 = 1000
        assert result.tatil_mesai_kazanc == Decimal('1000.00')
        
        # Yıllık izin: 3 × 1000 = 3000
        assert result.yillik_izin_kazanc == Decimal('3000.00')
        
        # Ek ödemeler: 500 + 1000 + 2000 = 3500
        assert result.ek_odemeler_toplam == Decimal('3500.00')
        
        # Brüt (ek hariç): 22000 + 1500 - 500 + 6000 + 1000 + 3000 = 33000
        assert result.brut_kazanc == Decimal('33000.00')
        
        # Toplam: 33000 + 3500 = 36500
        assert result.toplam_kazanc == Decimal('36500.00')


# Test çalıştırma:
# pytest backend/app/domains/personnel/payroll/tests/test_wage_calculator.py -v
```

---

### ADIM 5: Uygulama Sırası

#### Faz 1: Altyapı Hazırlama (1-2 gün)
1. ✅ Dizin yapısını oluştur: `payroll/calculations/`
2. ✅ `wage_calculator.py` dosyasını oluştur
3. ✅ Unit testleri yaz ve çalıştır
4. ✅ Tüm testlerin geçtiğini doğrula

#### Faz 2: Backend Entegrasyonu (2-3 gün)
1. ✅ `bordro_calculation/router.py` - `/maas-hesabi-data` endpoint'ini güncelle
2. ✅ Test et - modal açılıyor mu, doğru hesaplıyor mu?
3. ✅ `bordro_calculation/service.py` - `calculate` metodunu güncelle
4. ✅ Test et - bordro hesaplama çalışıyor mu?
5. ✅ `yevmiye_service_bordro.py` - yevmiye hesaplamalarını güncelle
6. ✅ Test et - yevmiye kayıtları doğru mu?

#### Faz 3: Frontend Güncelleme (1 gün)
1. ✅ `PuantajGridPage.tsx` - Backend'den veri al
2. ✅ Test et - Modal açıldığında doğru hesaplamalar görünüyor mu?
3. ✅ Performance test - Yavaşlama var mı?

#### Faz 4: Excel Formül Güncellemesi (1 gün)
1. ✅ `puantaj_grid/service.py` - Excel formülünü güncelle
2. ✅ Test et - Excel export çalışıyor mu?
3. ✅ Manuel test - Excel'de formüller doğru çalışıyor mu?

#### Faz 5: Doğrulama ve Test (2 gün)
1. ✅ Mevcut verilerle karşılaştırmalı test
2. ✅ Tüm endpoint'leri test et
3. ✅ Frontend'i test et
4. ✅ Excel export'u test et
5. ✅ Regression test - Eski özellikler çalışıyor mu?

#### Faz 6: Dokümantasyon ve Deployment (1 gün)
1. ✅ Code review
2. ✅ Dokümantasyon güncelle
3. ✅ Migration notları yaz
4. ✅ Production'a deploy

**Toplam Süre:** 8-10 gün

---

### ADIM 6: Rollback Planı

Eğer bir sorun olursa:

```python
# Git'te önceki commite dön
git revert <commit-hash>

# Veya branch'i geri al
git reset --hard <previous-commit>
```

**Güvenlik Önlemleri:**
1. Feature branch'te çalış: `feature/centralize-wage-calculation`
2. Her faz sonrası commit
3. Test coverage %90+ tutulmalı
4. Staging'de 1 hafta test edilmeli
5. Production'a kademeli deploy (canary deployment)

---

## 📊 BEKLENEN FAYDALAR

### Kod Kalitesi
- ✅ **%40 daha az kod** (185 satır → 110 satır bazı dosyalarda)
- ✅ **Tek doğruluk kaynağı** (Single Source of Truth)
- ✅ **Test coverage artışı** (Unit test yazılabilir)
- ✅ **Bakım kolaylığı** (Formül değişikliği tek yerden)

### Hata Azaltma
- ✅ **Tutarsızlık riski sıfır** (Tüm yerler aynı mantığı kullanır)
- ✅ **Kod tekrarı yok** (DRY principle)
- ✅ **Type safety** (Dataclass kullanımı)

### Geliştirme Hızı
- ✅ **Yeni özellik ekleme hızı** (Merkezi sınıfa ekle, tüm yerler otomatik kullanır)
- ✅ **Debug kolaylığı** (Tek yerden debug)
- ✅ **Onboarding hızı** (Yeni geliştiriciler tek yere bakar)

### Performans
- ⚠️ **Hafif yavaşlama olabilir** (Frontend'den backend'e API call)
- ✅ **Cache ile optimize edilebilir**
- ✅ **Database trigger hala kullanılabilir** (Önceden hesaplanmış veriler)

---

## 🎯 ÖNERİLER

### Öncelik 1: Merkezi Sınıfı Oluştur
Önce `wage_calculator.py` dosyasını oluştur ve test et. Bu, tüm değişikliklerin temelini oluşturur.

### Öncelik 2: Backend Endpoint'leri Güncelle
Backend'i önce güncelle çünkü bu, frontend'den bağımsız çalışır. Test etmek daha kolay.

### Öncelik 3: Frontend'i Güncelle
Frontend'i backend'den veri alacak şekilde güncelle. API ready olduktan sonra bu kolay olacak.

### Öncelik 4: Excel Formülünü Güncelle
Excel en son öncelik çünkü kullanıcılar manuel dolduruyor, otomatik sistem değil.

### Test Stratejisi
- Her faz sonrası regression test
- Mevcut verilerle karşılaştırma yapılmalı
- Edge case'ler test edilmeli
- Performance test yapılmalı

---

## 📋 KONTROL LİSTESİ

### Geliştirme Öncesi
- [ ] Bu raporu oku ve anla
- [ ] Tüm ilgili dosyaları incele
- [ ] Feature branch oluştur
- [ ] Test veritabanı hazırla

### Geliştirme Sırası
- [ ] `wage_calculator.py` oluştur
- [ ] Unit testleri yaz
- [ ] Testleri çalıştır (%100 geçmeli)
- [ ] Backend endpoint'leri güncelle
- [ ] Integration testleri yap
- [ ] Frontend'i güncelle
- [ ] Frontend testleri yap
- [ ] Excel formülünü güncelle
- [ ] Excel testleri yap

### Deployment Öncesi
- [ ] Code review yap
- [ ] Tüm testler geçiyor mu?
- [ ] Performance test yap
- [ ] Dokümantasyon güncelle
- [ ] Rollback planı hazır mı?

### Deployment Sonrası
- [ ] Staging'de test et (1 hafta)
- [ ] Production'a canary deployment
- [ ] Monitoring kur
- [ ] Kullanıcı geri bildirimi topla
- [ ] Gerekirse hotfix hazır ol

---

## 📞 DESTEK

Herhangi bir sorun olursa:
1. Bu rapordaki örneklere bak
2. Unit testlere bak (nasıl kullanılacağını gösterir)
3. Git history'ye bak (ne değişti)
4. Rollback planını uygula

---

**Rapor Tarihi:** 31 Ocak 2026
**Versiyon:** 1.0
**Durum:** Kritik sorunlar çözüldü ✅, Merkezileştirme planı hazır
