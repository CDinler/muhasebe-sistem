#!/bin/bash

# Muhasebe Sistem - Otomatik Kurulum Scripti
# Bu script sunucunuza otomatik olarak sistemi kurar

set -e  # Hata durumunda dur

echo "╔════════════════════════════════════════╗"
echo "║  Muhasebe Sistem - Otomatik Kurulum  ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Root kontrolü
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Bu scripti root olarak çalıştırmalısınız!"
    echo "Lütfen 'sudo' kullanın veya root olarak giriş yapın."
    exit 1
fi

# Input al
read -p "Domain adınızı girin (örn: muhasebe.com): " DOMAIN
read -p "Email adresinizi girin: " EMAIL
read -sp "Database şifresi girin: " DB_PASSWORD
echo ""
read -sp "Database şifresini tekrar girin: " DB_PASSWORD_CONFIRM
echo ""

# Şifre kontrolü
if [ "$DB_PASSWORD" != "$DB_PASSWORD_CONFIRM" ]; then
    echo "❌ Şifreler eşleşmiyor!"
    exit 1
fi

# Secret key oluştur
SECRET_KEY=$(openssl rand -hex 32)

echo ""
echo "📦 Adım 1/7: Sistem güncellemesi..."
apt update && apt upgrade -y

echo ""
echo "🐳 Adım 2/7: Docker kurulumu..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl start docker
    systemctl enable docker
    echo "✓ Docker kuruldu"
else
    echo "✓ Docker zaten kurulu"
fi

echo ""
echo "🐳 Adım 3/7: Docker Compose kurulumu..."
if ! command -v docker-compose &> /dev/null; then
    apt install -y docker-compose
    echo "✓ Docker Compose kuruldu"
else
    echo "✓ Docker Compose zaten kurulu"
fi

echo ""
echo "🔥 Adım 4/7: Firewall ayarları..."
apt install -y ufw
ufw --force enable
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
echo "✓ Firewall yapılandırıldı"

echo ""
echo "📂 Adım 5/7: Proje dizini oluşturuluyor..."
mkdir -p /opt/muhasebe-sistem
cd /opt/muhasebe-sistem

echo ""
echo "Projeyi nasıl yüklemek istersiniz?"
echo "1) Git clone (önerilen)"
echo "2) Manuel dosya yükleme (daha sonra scp ile)"
read -p "Seçiminiz (1 veya 2): " CHOICE

if [ "$CHOICE" == "1" ]; then
    read -p "Git repository URL'sini girin: " GIT_URL
    git clone "$GIT_URL" .
elif [ "$CHOICE" == "2" ]; then
    echo ""
    echo "📋 Manuel yükleme seçildi."
    echo "Şimdi yerel bilgisayarınızdan bu komutu çalıştırın:"
    echo ""
    echo "scp -r ./muhasebe-sistem/* root@$(hostname -I | awk '{print $1}'):/opt/muhasebe-sistem/"
    echo ""
    read -p "Dosyaları yükledikten sonra Enter'a basın..."
fi

echo ""
echo "⚙️  Adım 6/7: Environment ayarları..."

cat > .env <<EOF
# Database Configuration
DB_USER=muhasebe_user
DB_PASSWORD=$DB_PASSWORD
DB_NAME=muhasebe_db
DB_HOST=db
DB_PORT=5432

# Application Security
SECRET_KEY=$SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN

# API Configuration
VITE_API_URL=https://$DOMAIN/api/v1

# Environment
ENVIRONMENT=production
DEBUG=False

# Backup Configuration
BACKUP_PATH=/var/backups/muhasebe-sistem
EOF

echo "✓ Environment dosyası oluşturuldu"

echo ""
echo "🚀 Adım 7/7: Docker container'ları başlatılıyor..."
docker-compose up -d

echo ""
echo "⏳ Servislerin başlaması bekleniyor (30 saniye)..."
sleep 30

echo ""
echo "╔════════════════════════════════════════╗"
echo "║        KURULUM TAMAMLANDI! 🎉          ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "📋 Önemli Bilgiler:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo "Secret Key: $SECRET_KEY"
echo "Database User: muhasebe_user"
echo "Database Password: [GİZLİ]"
echo ""
echo "📂 Proje Dizini:"
echo "/opt/muhasebe-sistem"
echo ""
echo "🔍 Komutlar:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Log göster:    docker-compose logs -f"
echo "Restart:       docker-compose restart"
echo "Stop:          docker-compose down"
echo "Start:         docker-compose up -d"
echo "Status:        docker-compose ps"
echo ""
echo "📝 Sonraki Adımlar:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣  DNS Ayarları (Domain sağlayıcınızda):"
echo "   A Record: @ -> $(hostname -I | awk '{print $1}')"
echo "   A Record: www -> $(hostname -I | awk '{print $1}')"
echo ""
echo "2️⃣  SSL Sertifikası Kur:"
echo "   cd /opt/muhasebe-sistem"
echo "   nano setup-ssl.sh  # DOMAIN ve EMAIL değerlerini kontrol et"
echo "   chmod +x setup-ssl.sh"
echo "   ./setup-ssl.sh"
echo ""
echo "3️⃣  Admin Kullanıcısı Oluştur:"
echo "   docker exec -it muhasebe-backend python create_admin_hash.py"
echo ""
echo "4️⃣  Test Et:"
echo "   http://$(hostname -I | awk '{print $1}')  (şu an erişilebilir)"
echo "   https://$DOMAIN  (DNS ve SSL sonrası)"
echo ""
echo "📚 Detaylı dokümantasyon:"
echo "/opt/muhasebe-sistem/docs/deployment/DEPLOYMENT_GUIDE.md"
echo ""
echo "╔════════════════════════════════════════╗"
echo "║     İyi kullanımlar! 🚀                 ║"
echo "╚════════════════════════════════════════╝"
