#!/bin/bash

# Muhasebe Sistem - Sunucu Güncelleme Scripti
# Kullanım: ./update.sh
# Bu script en son kodu çeker ve servisleri yeniden başlatır.

set -e

echo "╔════════════════════════════════════════╗"
echo "║    Muhasebe Sistem - Güncelleme        ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Proje dizinine git
cd /opt/muhasebe-sistem

# Mevcut commit'i göster
BEFORE=$(git rev-parse --short HEAD)
echo "▶  Mevcut versiyon: $BEFORE"

# Kodu çek
echo ""
echo "📥 Yeni kod indiriliyor (git pull)..."
git pull origin main
AFTER=$(git rev-parse --short HEAD)

# Değişiklik var mı kontrol et
if [ "$BEFORE" = "$AFTER" ]; then
    echo ""
    echo "✅ Zaten güncel. Güncelleme yapılmadı."
    exit 0
fi

echo ""
echo "📝 Değişiklikler ($BEFORE → $AFTER):"
git log --oneline $BEFORE..$AFTER

# Değişen dosyaları kontrol et - hangi servisin rebuild edilmesi gerektiğini anla
BACKEND_CHANGED=$(git diff --name-only $BEFORE $AFTER | grep "^backend/" | wc -l)
FRONTEND_CHANGED=$(git diff --name-only $BEFORE $AFTER | grep "^frontend/" | wc -l)

echo ""

if [ "$BACKEND_CHANGED" -gt 0 ] && [ "$FRONTEND_CHANGED" -gt 0 ]; then
    echo "🔄 Backend + Frontend değişti, ikisi de rebuild ediliyor..."
    docker-compose build backend frontend
    docker-compose up -d --no-deps backend frontend

elif [ "$BACKEND_CHANGED" -gt 0 ]; then
    echo "🔄 Backend değişti, rebuild ediliyor..."
    docker-compose build backend
    docker-compose up -d --no-deps backend

elif [ "$FRONTEND_CHANGED" -gt 0 ]; then
    echo "🔄 Frontend değişti, rebuild ediliyor..."
    docker-compose build frontend
    docker-compose up -d --no-deps frontend
fi

# Servislerin ayağa kalkmasını bekle
echo ""
echo "⏳ Servisler başlatılıyor (20 saniye)..."
sleep 20

# Health check
echo ""
echo "🔍 Sağlık kontrolü yapılıyor..."
if curl -sf http://localhost:8000/health > /dev/null; then
    echo "✅ Backend çalışıyor!"
else
    echo "⚠️  Backend health check başarısız. Logları kontrol edin:"
    echo "   docker-compose logs backend"
fi

# Eski image'ları temizle
docker image prune -f > /dev/null 2>&1

echo ""
echo "╔════════════════════════════════════════╗"
echo "║    ✅ GÜNCELLEME TAMAMLANDI!           ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Versiyon: $BEFORE → $AFTER"
echo "Log için: docker-compose logs -f"
