# 🚀 Deployment Hazırlık Özeti

## ✅ Oluşturulan Dosyalar

Aşağıdaki dosyalar projenize eklendi ve sistem internete yüklenmeye hazır:

### Docker Dosyaları
- ✅ `Dockerfile.backend` - Backend container yapılandırması
- ✅ `Dockerfile.frontend` - Frontend container yapılandırması  
- ✅ `docker-compose.yml` - Tüm servislerin orchestration'ı
- ✅ `.dockerignore` - Docker build optimizasyonu

### Nginx Konfigürasyonu
- ✅ `nginx.conf` - Basit HTTP konfigürasyonu
- ✅ `nginx-ssl.conf` - SSL ve reverse proxy konfigürasyonu

### Environment ve Güvenlik
- ✅ `.env.production` - Production environment şablonu
- ✅ `setup-ssl.sh` - SSL sertifikası kurulum scripti
- ✅ `backup.sh` - Otomatik database backup scripti

### Kurulum ve CI/CD
- ✅ `install.sh` - Tek komutla otomatik kurulum
- ✅ `.github/workflows/deploy.yml` - GitHub Actions CI/CD pipeline

### Dokümantasyon
- ✅ `docs/deployment/DEPLOYMENT_GUIDE.md` - Detaylı deployment kılavuzu
- ✅ `docs/deployment/QUICK_START.md` - Hızlı başlangıç (5 dakika)

---

## 📋 Hızlı Başlangıç Adımları

### 1. Domain ve Hosting Hazırlığı

**Gereksinimler:**
- [ ] Domain name alındı (örn: GoDaddy, Namecheap)
- [ ] Sunucu kiralandı (DigitalOcean, Hetzner, AWS)
  - Minimum: 4GB RAM, 2 CPU, 50GB Disk
  - İşletim Sistemi: Ubuntu 22.04 LTS

**Tahmini Maliyet:**
- Domain: ~$10-15/yıl
- Sunucu: ~$20-25/ay

### 2. DNS Ayarları

Domain sağlayıcınızda DNS kayıtlarını ayarlayın:

```
A Record: @   -> sunucu-ip-adresiniz
A Record: www -> sunucu-ip-adresiniz
```

⏱️ DNS yayılması 24 saate kadar sürebilir.

### 3. Sunucuya Kurulum

**Seçenek A: Otomatik Kurulum (Önerilen - 5 dakika)**

```bash
# Sunucuya SSH ile bağlanın
ssh root@sunucu-ip-adresiniz

# Otomatik kurulum scriptini çalıştırın
curl -fsSL https://raw.githubusercontent.com/your-repo/install.sh | bash
```

Script sizden soracak:
- Domain adı
- Email adresi
- Database şifresi

**Seçenek B: Manuel Kurulum**

Detaylı adımlar için: [DEPLOYMENT_GUIDE.md](docs/deployment/DEPLOYMENT_GUIDE.md)

### 4. SSL Sertifikası (HTTPS)

```bash
cd /opt/muhasebe-sistem

# setup-ssl.sh dosyasını düzenle
nano setup-ssl.sh
# DOMAIN ve EMAIL değerlerini güncelle

# SSL kurulumunu çalıştır
chmod +x setup-ssl.sh
./setup-ssl.sh

# SSL ile servisleri yeniden başlat
docker-compose --profile ssl up -d
```

### 5. Admin Kullanıcısı Oluştur

```bash
docker exec -it muhasebe-backend python create_admin_hash.py
```

Kullanıcı adı ve şifre girin.

### 6. Test Et

Tarayıcınızda açın:
- `https://yourdomain.com` - Ana sayfa
- `https://yourdomain.com/api/health` - API health check
- `https://yourdomain.com/docs` - API documentation

---

## 🔧 Yönetim Komutları

### Servis Yönetimi

```bash
# Servislerin durumunu gör
docker-compose ps

# Log'ları izle
docker-compose logs -f

# Yeniden başlat
docker-compose restart

# Durdur
docker-compose down

# Başlat
docker-compose up -d
```

### Güncelleme

```bash
cd /opt/muhasebe-sistem
git pull
docker-compose build
docker-compose up -d
```

### Backup

```bash
# Manuel backup
./backup.sh

# Otomatik backup (her gün saat 2'de)
crontab -e
# Ekle: 0 2 * * * /opt/muhasebe-sistem/backup.sh
```

---

## ⚙️ Environment Ayarları

`.env` dosyasında **MUTLAKA** değiştirmeniz gerekenler:

```bash
# Güçlü database şifresi
DB_PASSWORD=YourStrongPassword123!@#

# Secret key oluştur: openssl rand -hex 32
SECRET_KEY=your-random-64-character-string

# Domain adınızı ekleyin
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
VITE_API_URL=https://yourdomain.com/api/v1
```

---

## 🔒 Güvenlik Kontrol Listesi

- [ ] `.env` dosyasında güçlü şifreler kullanıldı
- [ ] `SECRET_KEY` rastgele oluşturuldu (64 karakter)
- [ ] `DEBUG=False` olarak ayarlandı
- [ ] SSL sertifikası kuruldu (HTTPS)
- [ ] Firewall aktif (UFW)
  ```bash
  ufw allow 80/tcp
  ufw allow 443/tcp
  ufw enable
  ```
- [ ] SSH güvenliği sağlandı (key-based auth önerilir)
- [ ] Database portı (5432) dışarıya kapalı
- [ ] Otomatik backup kuruldu
- [ ] CORS ayarları daraltıldı (sadece kendi domain)

---

## 📊 Monitoring (Opsiyonel)

### Portainer (Docker GUI)

```bash
docker run -d -p 9000:9000 \
    --name=portainer --restart=always \
    -v /var/run/docker.sock:/var/run/docker.sock \
    portainer/portainer-ce
```

Erişim: `http://sunucu-ip:9000`

### Sistem Monitoring

```bash
# Container durumu
docker stats

# Disk kullanımı
df -h

# RAM kullanımı
free -h

# Log boyutları
du -sh /var/lib/docker/containers/*
```

---

## 🐛 Sorun Giderme

### Container başlamıyor?

```bash
# Log'ları kontrol et
docker-compose logs backend
docker-compose logs db

# Yeniden başlat
docker-compose restart
```

### Database bağlantı hatası?

```bash
# Database çalışıyor mu?
docker-compose ps db

# Database'e manuel bağlan
docker exec -it muhasebe-db psql -U muhasebe_user -d muhasebe_db
```

### Frontend API'ye bağlanamıyor?

1. `.env` dosyasında `VITE_API_URL` doğru mu?
2. `ALLOWED_ORIGINS` ayarında domain var mı?
3. Nginx log'larını kontrol et: `docker-compose logs nginx`

### Disk doldu?

```bash
# Docker temizliği
docker system prune -a

# Eski backup'ları sil (30 günden eski)
find /var/backups/muhasebe-sistem -mtime +30 -delete
```

---

## 📚 Detaylı Dokümantasyon

Daha fazla bilgi için:

- **Detaylı Kılavuz**: [docs/deployment/DEPLOYMENT_GUIDE.md](docs/deployment/DEPLOYMENT_GUIDE.md)
- **Hızlı Başlangıç**: [docs/deployment/QUICK_START.md](docs/deployment/QUICK_START.md)

---

## 🎯 Deployment Checklist

Deployment öncesi son kontrol:

### Hazırlık
- [ ] Domain alındı
- [ ] DNS kayıtları ayarlandı
- [ ] Sunucu kiralandı ve erişilebilir

### Kurulum
- [ ] Docker kuruldu
- [ ] Proje dosyaları yüklendi
- [ ] `.env` dosyası düzenlendi
- [ ] Environment değerleri güncellendi

### Güvenlik
- [ ] Database şifresi değiştirildi
- [ ] SECRET_KEY oluşturuldu
- [ ] Firewall ayarlandı
- [ ] SSL sertifikası kuruldu

### Test
- [ ] Servisler çalışıyor (`docker-compose ps`)
- [ ] Health check başarılı (`/api/health`)
- [ ] Frontend erişilebilir
- [ ] Admin girişi yapılabiliyor

### Bakım
- [ ] Backup script kuruldu
- [ ] Cron job ayarlandı
- [ ] Monitoring kuruldu (opsiyonel)
- [ ] Log rotation yapılandırıldı

---

## 🚀 Başarılı Deployment!

Tebrikler! Sisteminiz artık online. 

**Sonraki Adımlar:**
1. İlk kullanıcıları oluşturun
2. Sistem ayarlarını yapılandırın
3. Email bildirimleri kurun (opsiyonel)
4. Database backup'ları düzenli kontrol edin
5. SSL sertifikası yenileme tarihini not edin (90 gün)

---

**Son Güncelleme:** 2026-02-24  
**Versiyon:** 1.0.0

İyi kullanımlar! 🎉
