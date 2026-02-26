#!/bin/bash
# =============================================================
# Muhasebe Sistem - SSL Kurulum Scripti
# Kullanim: bash /opt/muhasebe-sistem/setup-ssl.sh
# Not: server-setup.sh tamamlandiktan sonra calistir
# =============================================================

set -e

DOMAIN="yimak.isletmeyazilim.com"
EMAIL="cagataydinler@gmail.com"
APP_DIR="/opt/muhasebe-sistem"

echo "============================================"
echo "  SSL Kurulumu: $DOMAIN"
echo "============================================"

# ---- 1. Certbot Kur ----
echo "[1/5] Certbot kuruluyor..."
apt-get install -y certbot

# ---- 2. Frontend container'i durdur (80 portu serbest kalsin) ----
echo "[2/5] Nginx durduruluyor (port 80 serbest birakiliyor)..."
cd $APP_DIR
docker compose stop frontend

# ---- 3. SSL Sertifikasi Al ----
echo "[3/5] SSL sertifikasi aliniyor..."
certbot certonly \
    --standalone \
    -d $DOMAIN \
    --non-interactive \
    --agree-tos \
    -m $EMAIL \
    --no-eff-email

echo "Sertifika alindi: /etc/letsencrypt/live/$DOMAIN/"

# ---- 4. Nginx SSL Config Guncelle ----
echo "[4/5] Nginx SSL konfigurasyonu guncelleniyor..."
cat > $APP_DIR/frontend/nginx.conf << 'NGINXEOF'
server {
    listen 80;
    server_name yimak.isletmeyazilim.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yimak.isletmeyazilim.com;

    ssl_certificate /etc/letsencrypt/live/yimak.isletmeyazilim.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yimak.isletmeyazilim.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINXEOF

# ---- 5. .env Guncelle (HTTPS URL) ----
echo "[5/5] .env HTTPS URL'e guncelleniyor..."
sed -i 's|VITE_API_URL=.*|VITE_API_URL=https://yimak.isletmeyazilim.com|' $APP_DIR/.env
sed -i 's|ALLOWED_ORIGINS=.*|ALLOWED_ORIGINS=http://185.92.2.82,https://yimak.isletmeyazilim.com|' $APP_DIR/.env

# ---- docker-compose override: SSL port + sertifika mount ----
echo "Docker compose SSL icin guncelleniyor..."
cat > $APP_DIR/docker-compose.override.yml << 'DCEOF'
services:
  frontend:
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - ./frontend/nginx.conf:/etc/nginx/conf.d/default.conf:ro
DCEOF

# ---- Rebuild & Baslat ----
echo "Frontend rebuild ediliyor (HTTPS URL ile)..."
cd $APP_DIR
docker compose build --no-cache frontend
docker compose up -d

echo ""
echo "============================================"
echo "  SSL KURULUMU TAMAMLANDI!"
echo "  Site: https://$DOMAIN"
echo "  Giris: admin / admin123"
echo "============================================"

# UYARI: Bu script icindeki gereksiz eski kod asagida - silinmistir
exit 0

echo "SSL Certificate Setup for Muhasebe System"
echo "=========================================="
echo ""
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# Check if domain is still placeholder
if [ "$DOMAIN" = "yourdomain.com" ]; then
    echo "ERROR: Please edit this script and replace 'yourdomain.com' with your actual domain!"
    exit 1
fi

# Create directory for certificates
mkdir -p ./ssl
mkdir -p ./certbot/www

# Create docker-compose override for certbot
cat > docker-compose.certbot.yml <<EOF
version: '3.8'

services:
  certbot:
    image: certbot/certbot
    container_name: certbot
    volumes:
      - ./ssl:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    command: certonly --webroot -w /var/www/certbot --email $EMAIL --agree-tos --no-eff-email -d $DOMAIN -d www.$DOMAIN
EOF

echo "Step 1: Starting temporary nginx for certificate challenge..."

# Temporary nginx config for certbot challenge
cat > nginx-certbot-temp.conf <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 200 'OK';
        add_header Content-Type text/plain;
    }
}
EOF

# Start nginx temporarily
docker run -d --name nginx-temp \
    -p 80:80 \
    -v $(pwd)/nginx-certbot-temp.conf:/etc/nginx/conf.d/default.conf \
    -v $(pwd)/certbot/www:/var/www/certbot \
    nginx:alpine

echo "Step 2: Obtaining SSL certificate..."
docker-compose -f docker-compose.certbot.yml run --rm certbot

if [ $? -eq 0 ]; then
    echo "✓ SSL certificate obtained successfully!"
    
    # Copy certificates to ssl directory
    cp ./ssl/live/$DOMAIN/fullchain.pem ./ssl/
    cp ./ssl/live/$DOMAIN/privkey.pem ./ssl/
    
    echo "✓ Certificates copied to ./ssl/ directory"
else
    echo "✗ Failed to obtain SSL certificate"
    docker stop nginx-temp
    docker rm nginx-temp
    exit 1
fi

# Stop temporary nginx
echo "Step 3: Cleaning up..."
docker stop nginx-temp
docker rm nginx-temp

echo ""
echo "=========================================="
echo "SSL Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update nginx-ssl.conf with your domain name"
echo "2. Update .env.production with your domain"
echo "3. Start services with: docker-compose --profile ssl up -d"
echo ""
echo "Certificate renewal:"
echo "Certificates expire in 90 days. Set up auto-renewal with cron:"
echo "0 0 1 * * cd /path/to/muhasebe-sistem && docker-compose -f docker-compose.certbot.yml run --rm certbot renew && docker-compose restart nginx"
