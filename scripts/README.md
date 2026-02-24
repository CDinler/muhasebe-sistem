# Scripts Dizini

Bu dizin artık temizlenmiştir. Tüm geçici geliştirme scriptleri silinmiştir.

## 📋 Proje Yönetimi

**Database Migrations:** 
- `database/migrations/` klasöründe SQL migration dosyaları
- `backend/alembic/` klasöründe Alembic Python migration'ları

**Test Scriptleri:**
- Backend test'leri için: `backend/tests/` klasörünü kullanın
- Frontend test'leri için: `frontend/src/__tests__/` klasörünü kullanın

**Bakım Scriptleri:**
- İhtiyaç duyulan özel scriptler için bu klasörde yeni dosyalar oluşturabilirsiniz
- Geliştirme sırasında kullanılan geçici scriptler buraya konulmamalıdır

## 🧹 Temizlik Notları

**Silinen klasörler:**
- `/analysis` - 114 geçici analiz scripti
- `/tests` - 47 geçici test scripti
- `/migrations` - 25 eski migration scripti
- `/utilities` - 114 geçici utility scripti
- `/setup` - 5 PostgreSQL kurulum scripti
- `/backup` - Boş klasör
- `/deploy` - Boş klasör

**Toplam:** ~305 geçici dosya temizlendi
