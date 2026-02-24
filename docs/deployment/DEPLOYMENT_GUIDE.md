# Muhasebe Sistem - Production Deployment Kılavuzu

Bu kılavuz, Muhasebe Sistemini internete (production ortamına) yüklemek için gereken tüm adımları detaylı olarak açıklar.

## 📋 İçindekiler

1. [Gereksinimler](#gereksinimler)
2. [Hosting Seçimi](#hosting-seçimi)
3. [Sunucu Hazırlığı](#sunucu-hazırlığı)
4. [Deployment Yöntemleri](#deployment-yöntemleri)
5. [SSL Sertifikası Kurulumu](#ssl-sertifikası-kurulumu)
6. [Bakım ve Monitoring](#bakım-ve-monitoring)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Gereksinimler

### 1. Domain Name (Alan Adı)
- Bir domain name sağlayıcısından domain alın (örn: yourdomain.com)
  - Önerilen: GoDaddy, Namecheap, Cloudflare Registrar
  - Yıllık maliyet: ~$10-$15

### 2. Server (Sunucu)
Minimum gereksinimler:
- **CPU**: 2 core
- **RAM**: 4 GB
- **Disk**: 50 GB SSD
- **OS**: Ubuntu 20.04/22.04 LTS veya Debian 11+

Önerilen sunucu sağlayıcıları:
- **DigitalOcean** - Droplet ($24/ay) - Kolay, iyi dokümantasyon
- **Hetzner** - Cloud Server (€20/ay) - Uygun fiyat
- **AWS** - EC2 Lightsail ($20/ay) - Enterprise
- **Azure** - VM ($25/ay)
- **Türk Telekom** - Bulut Sunucu

### 3. Gerekli Yazılımlar (Sunucuya kurulacak)
- Docker & Docker Compose
- Git
- Nginx (opsiyonel - Docker içinde de çalışabilir)

---

## 🏢 Hosting Seçimi

### Seçenek 1: DigitalOcean (Önerilen - Başlangıç İçin)

**장점:**
- 1-click Docker image mevcut
- İyi dokümantasyon
- Kolay yönetim paneli
- Automatic backups

**Adımlar:**
```bash
1. DigitalOcean hesabı oluştur
2. Create Droplet
3. Ubuntu 22.04 LTS + Docker seç
4. $24/ay plan (4GB RAM, 2 CPU)
5. SSH key ekle
6. Create!
```

### Seçenek 2: Hetzner (Maliyet Odaklı)

**장점:**
- Daha ucuz (~€20/ay)
- Güçlü donanım
- Avrupa datacenter

**Adımlar:**
```bash
1. Hetzner Cloud hesabı oluştur
2. CX31 plan seç (4GB RAM, 2 vCPU)
3. Ubuntu 22.04 image seç
4. SSH key ekle
```

### Seçenek 3: AWS Lightsail (Büyük Şirketler İçin)

**장점:**
- AWS ekosistemi
- Yüksek güvenilirlik
- Global datacenter

---

## 🔧 Sunucu Hazırlığı

### Adım 1: Sunucuya Bağlan

```bash
# SSH ile bağlan (IP adresinizi kullanın)
ssh root@your-server-ip
```

### Adım 2: Sistemi Güncelle

```bash
# Sistem güncellemesi
apt update && apt upgrade -y

# Gerekli paketleri kur
apt install -y git curl wget nano ufw
```

### Adım 3: Docker Kurulumu

```bash
# Docker kurulum scripti
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose kurulum
apt install -y docker-compose

# Docker servisini başlat
systemctl start docker
systemctl enable docker

# Kurulumu test et
docker --version
docker-compose --version
```

### Adım 4: Firewall Ayarları

```bash
# UFW firewall'ı aktive et
ufw allow OpenSSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable

# Durumu kontrol et
ufw status
```

### Adım 5: Swap Bellek (Opsiyonel ama Önerilen)

```bash
# 2GB swap oluştur
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Kalıcı yap
echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab
```

---

## 🚀 Deployment Yöntemleri

### Yöntem 1: Docker ile Deployment (ÖNERİLEN)

#### Adım 1: Projeyi Klonla

```bash
# Ana dizine git
cd /opt

# Projeyi klonla
git clone <your-git-repo-url> muhasebe-sistem
cd muhasebe-sistem

# Veya dosyaları SCP ile yükle:
# scp -r ./muhasebe-sistem root@your-server-ip:/opt/
```

#### Adım 2: Environment Ayarları

```bash
# Production env dosyasını kopyala
cp .env.production .env

# Düzenle
nano .env
```

**.env dosyasında MUTLAKA değiştir:**
```env
# Güçlü şifre oluştur
DB_PASSWORD=YourStrongPassword123!@#

# SECRET_KEY oluştur (terminal'de çalıştır: openssl rand -hex 32)
SECRET_KEY=your-64-character-random-string-here

# Domain adını ekle
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
VITE_API_URL=https://yourdomain.com/api/v1
```

#### Adım 3: Frontend Environment

```bash
# Frontend env dosyası oluştur
cd frontend
echo "VITE_API_URL=https://yourdomain.com/api/v1" > .env.production
cd ..
```

#### Adım 4: Build ve Deploy

```bash
# Docker container'ları başlat
docker-compose up -d

# Log'ları izle
docker-compose logs -f

# Servis durumunu kontrol et
docker-compose ps
```

#### Adım 5: Database Migration

```bash
# Database container'a bağlan
docker exec -it muhasebe-db psql -U muhasebe_user -d muhasebe_db

# Migration dosyalarını çalıştır
# (Eğer auto migration yoksa manuel çalıştır)
```

#### Adım 6: İlk Admin Kullanıcısı Oluştur

```bash
# Backend container'a gir
docker exec -it muhasebe-backend bash

# Admin oluşturma scriptini çalıştır
python create_admin_hash.py

# Container'dan çık
exit
```

---

### Yöntem 2: Manuel Deployment (İleri Seviye)

<details>
<summary>Tıklayarak detayları göster</summary>

#### Backend Kurulumu

```bash
# Python 3.11 kur
apt install -y python3.11 python3.11-venv python3-pip

# Backend dizinine git
cd /opt/muhasebe-sistem/backend

# Virtual environment oluştur
python3.11 -m venv venv
source venv/bin/activate

# Bağımlılıkları kur
pip install -r requirements.txt

# Systemd service oluştur
cat > /etc/systemd/system/muhasebe-backend.service <<EOF
[Unit]
Description=Muhasebe Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/muhasebe-sistem/backend
Environment="PATH=/opt/muhasebe-sistem/backend/venv/bin"
ExecStart=/opt/muhasebe-sistem/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Servisi başlat
systemctl daemon-reload
systemctl start muhasebe-backend
systemctl enable muhasebe-backend
```

#### Frontend Kurulumu

```bash
# Node.js 18 kur
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Frontend dizinine git
cd /opt/muhasebe-sistem/frontend

# Bağımlılıkları kur
npm ci

# Build
npm run build

# Build dosyalarını nginx dizinine kopyala
mkdir -p /var/www/muhasebe
cp -r dist/* /var/www/muhasebe/
```

#### Nginx Kurulumu

```bash
# Nginx kur
apt install -y nginx

# Config dosyasını kopyala
cp /opt/muhasebe-sistem/nginx-ssl.conf /etc/nginx/sites-available/muhasebe

# Symlink oluştur
ln -s /etc/nginx/sites-available/muhasebe /etc/nginx/sites-enabled/

# Default config'i kaldır
rm /etc/nginx/sites-enabled/default

# Nginx'i test et
nginx -t

# Nginx'i başlat
systemctl restart nginx
systemctl enable nginx
```

</details>

---

## 🔒 SSL Sertifikası Kurulumu

### Let's Encrypt ile Ücretsiz SSL

#### Yöntem 1: Certbot ile (Docker Dışı)

```bash
# Certbot kur
apt install -y certbot python3-certbot-nginx

# SSL sertifikası al
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# E-posta ve domain onayı yap
# Certbot otomatik olarak nginx'i yapılandırır

# Otomatik yenileme testi
certbot renew --dry-run
```

#### Yöntem 2: Docker ile

```bash
# Proje dizininde
cd /opt/muhasebe-sistem

# SSL setup scriptini düzenle
nano setup-ssl.sh
# DOMAIN ve EMAIL değerlerini güncelle

# Script'i çalıştırılabilir yap
chmod +x setup-ssl.sh

# SSL setup'ı çalıştır
./setup-ssl.sh

# SSL ile servisleri başlat
docker-compose --profile ssl up -d
```

### Cloudflare SSL (Alternatif - Basit)

Eğer Cloudflare kullanıyorsanız:
```bash
1. Domain'i Cloudflare'e ekle
2. Nameserver'ları güncelle
3. SSL/TLS -> Full (strict) seç
4. Cloudflare otomatik SSL sağlar!
```

---

## 🔍 Bakım ve Monitoring

### Günlük İzleme

```bash
# Tüm container'ları izle
docker-compose logs -f

# Sadece backend
docker-compose logs -f backend

# Sadece database
docker-compose logs -f db

# Nginx access log
docker-compose logs -f nginx
```

### Sistem Durumu

```bash
# Container durumu
docker-compose ps

# Sistem kaynakları
docker stats

# Disk kullanımı
df -h

# RAM kullanımı
free -h
```

### Database Backup

```bash
# Backup scriptini çalıştırılabilir yap
chmod +x backup.sh

# Manuel backup
./backup.sh

# Cron ile otomatik backup (her gün saat 2'de)
crontab -e
# Şunu ekle:
0 2 * * * /opt/muhasebe-sistem/backup.sh
```

### Güncelleme

```bash
# Kod güncellemesi
cd /opt/muhasebe-sistem
git pull

# Container'ları yeniden build et
docker-compose build

# Restart
docker-compose down
docker-compose up -d

# Veya rolling update
docker-compose up -d --no-deps --build backend
docker-compose up -d --no-deps --build frontend
```

---

## 📊 Monitoring Araçları (Opsiyonel)

### 1. Portainer (Docker GUI)

```bash
docker volume create portainer_data
docker run -d -p 9000:9000 \
    --name=portainer --restart=always \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v portainer_data:/data \
    portainer/portainer-ce

# Tarayıcıda aç: http://your-server-ip:9000
```

### 2. Uptime Kuma (Uptime Monitoring)

```bash
docker run -d --restart=always \
    -p 3001:3001 \
    -v uptime-kuma:/app/data \
    --name uptime-kuma \
    louislam/uptime-kuma:1

# Tarayıcıда aç: http://your-server-ip:3001
```

---

## 🐛 Troubleshooting

### Container Başlamıyor

```bash
# Log'ları kontrol et
docker-compose logs backend

# Container'ı yeniden başlat
docker-compose restart backend

# Fresh start
docker-compose down
docker-compose up -d
```

### Database Bağlantı Hatası

```bash
# Database container'ının çalıştığını kontrol et
docker-compose ps db

# Database log'larını kontrol et
docker-compose logs db

# Database'e manuel bağlan
docker exec -it muhasebe-db psql -U muhasebe_user -d muhasebe_db
```

### Frontend API'ye Bağlanamıyor

1. `.env` dosyasında `VITE_API_URL` doğru mu?
2. CORS ayarları doğru mu? (ALLOWED_ORIGINS)
3. Nginx proxy ayarları doğru mu?

```bash
# Backend health check
curl http://localhost:8000/health

# Nginx config test
docker-compose exec nginx nginx -t
```

### SSL Sorunu

```bash
# Sertifika yolları doğru mu kontrol et
ls -la /etc/nginx/ssl/

# Nginx SSL config test
docker-compose logs nginx

# Sertifikayı yenile
certbot renew
docker-compose restart nginx
```

### Disk Doldu

```bash
# Docker temizlik
docker system prune -a

# Log dosyalarını temizle
docker-compose logs --tail=1000 > /tmp/logs.txt
# Log rotation ayarla

# Eski backup'ları sil
find /var/backups/muhasebe-sistem -name "*.sql.gz" -mtime +30 -delete
```

---

## 📝 Deployment Checklist

Deployment öncesi kontrol listesi:

- [ ] Domain name alındı ve DNS ayarlandı
- [ ] Sunucu kiralandı ve hazırlandı
- [ ] Docker kuruldu
- [ ] `.env` dosyası düzenlendi
  - [ ] DB_PASSWORD değiştirildi
  - [ ] SECRET_KEY değiştirildi
  - [ ] Domain eklenди
- [ ] SSL sertifikası alındı
- [ ] Firewall ayarlandı
- [ ] Database migration yapıldı
- [ ] Admin kullanıcısı oluşturuldu
- [ ] Backup script kuruldu
- [ ] Monitoring setup yapıldı
- [ ] Test edildi (tarayıcıdan erişim)

---

## 🚨 Güvenlik Önerileri

1. **SSH Güvenliği**
```bash
# SSH port değiştir
nano /etc/ssh/sshd_config
# Port 22 -> Port 2222

# Root login kapat
PermitRootLogin no

# SSH restart
systemctl restart sshd
```

2. **Database Güvenliği**
- Güçlü şifre kullan (min 16 karakter)
- Database portunu dışarıya açma
- Regular backup yap

3. **Application Güvenliği**
- SECRET_KEY'i asla paylaşma
- CORS ayarlarını daralt (sadece kendi domain'in)
- DEBUG=False olduğundan emin ol

4. **Fail2Ban** (Brute force koruması)
```bash
apt install -y fail2ban
systemctl enable fail2ban
```

---

## 📞 Yardım ve Destek

Sorun yaşarsanız:
1. Log dosyalarını kontrol edin
2. Troubleshooting bölümüne bakın
3. Domain ve SSL ayarlarını tekrar kontrol edin

---

## 🎉 Deployment Tamamlandı!

Tebrikler! Sisteminiz artık online.

**Test için:**
- `https://yourdomain.com` - Frontend
- `https://yourdomain.com/api/health` - Backend health
- `https://yourdomain.com/docs` - API documentation

**Sonraki adımlar:**
1. Monitoring kurulumu
2. Backup stratejisi
3. Email bildirimleri
4. Performance tuning

---

## 📚 Ek Kaynaklar

- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Son Güncelleme:** 2026-02-24
**Versiyon:** 1.0.0
