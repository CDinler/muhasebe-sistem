#!/bin/bash

# SSL Certificate Setup Script using Let's Encrypt
# This script helps you obtain free SSL certificates

DOMAIN="yourdomain.com"
EMAIL="your-email@example.com"

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
