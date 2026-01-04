# Scripts Dizini

Proje yönetimi ve bakım scriptleri

## 📂 Dizin Yapısı

### `/tests` - Test Scriptleri
Backend test scriptleri, unit testler ve integration testler
- `test_*.py` - Çeşitli modül testleri
- `quick_test.py` - Hızlı test scriptleri

### `/analysis` - Analiz Scriptleri
Veri analizi, kontrol ve raporlama scriptleri
- `analyze_*.py` - Veri analiz scriptleri
- `check_*.py` - Veri doğrulama ve kontrol scriptleri

### `/migrations` - Migration Scriptleri
Veritabanı migration ve data migration scriptleri
- `run_*.py` - Migration çalıştırıcıları
- `add_*.py` - Yeni özellik ekleyiciler
- `drop_*.py` - Kolon/tablo silme scriptleri
- `migrate_*.py` - Data migration scriptleri
- `*.sql` - SQL migration dosyaları
- `full_reset.py` - Sistem sıfırlama

### `/utilities` - Utility Scriptleri
Genel amaçlı yardımcı scriptler
- `create_*.py` - Kayıt oluşturma scriptleri
- `update_*.py` - Toplu güncelleme scriptleri
- `fix_*.py` - Veri düzeltme scriptleri
- `normalize_*.py` - Veri normalizasyon scriptleri
- `export_*.py` - Veri export scriptleri
- `import_*.py` - Veri import scriptleri
- `debug_*.py` - Debug yardımcıları
- `get_last_logs.ps1` - Log görüntüleyici

## 🚀 Kullanım

Backend dizininden çalıştırın:
```bash
cd backend
python ../scripts/tests/test_*.py
python ../scripts/migrations/run_*.py
python ../scripts/utilities/fix_*.py
```

## ⚠️ Dikkat

Migration scriptlerini production'da çalıştırmadan önce mutlaka backup alın!
