# Muhasebe Sistem - Hızlı Deployment (5 Dakika)

Bu kılavuz, sistemin en hızlı şekilde deploy edilmesi içindir.

## 🚀 Hızlı Başlangıç

### 1. Sunucuya Bağlan

```bash
ssh root@your-server-ip
```

### 2. Tek Komutla Kurulum

```bash
# Otomatik kurulum scriptini çalıştır
curl -fsSL https://raw.githubusercontent.com/your-repo/muhasebe-sistem/main/install.sh | bash
```

### Veya Manuel:

```bash
# Docker kur
curl -fsSL https://get.docker.com | sh

# Projeyi klonla
cd /opt
git clone your-repo-url muhasebe-sistem
cd muhasebe-sistem

# Environment ayarla
cp .env.production .env
nano .env  # DB_PASSWORD ve SECRET_KEY değiştir!

# Başlat
docker-compose up -d
```

### 3. SSL Kur (Let's Encrypt)

```bash
# Domain ayarını yap
nano setup-ssl.sh  # DOMAIN ve EMAIL değiştir

# SSL setup
chmod +x setup-ssl.sh
./setup-ssl.sh

# SSL ile yeniden başlat
docker-compose --profile ssl up -d
```

### 4. Admin Oluştur

```bash
docker exec -it muhasebe-backend python create_admin_hash.py
```

## ✅ Test Et

```bash
# Health check
curl https://yourdomain.com/api/health

# Tarayıcıda aç
open https://yourdomain.com
```

## 📝 Önemli Notlar

1. **Mutlaka değiştir:**
   - `.env` içindeki `DB_PASSWORD`
   - `.env` içindeki `SECRET_KEY`
   - Domain adlarını

2. **DNS Ayarları:**
   ```
   A Record: @ -> your-server-ip
   A Record: www -> your-server-ip
   ```

3. **Firewall:**
   ```bash
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw enable
   ```

## 🐛 Sorun mu var?

```bash
# Log'lara bak
docker-compose logs -f

# Yeniden başlat
docker-compose restart
```

Detaylı kılavuz için: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
