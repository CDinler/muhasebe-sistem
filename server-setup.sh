#!/bin/bash
# =============================================================
# Muhasebe Sistem - Sunucu Kurulum Scripti
# Kullanim: bash server-setup.sh
# =============================================================

set -e  # Hata olursa dur

echo "============================================"
echo "  Muhasebe Sistem - Sunucu Kurulumu"
echo "============================================"

# ---- 0. SSH Güvenli Erişim Ayarı ----
echo "[0/6] SSH konfigürasyonu yapılıyor..."
# Root ile SSH girişine izin ver (kapanmasın)
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
systemctl restart sshd
echo "SSH ayarları güncellendi: Root girişi = AKTIF"

# ---- 1. Sistem Güncellemesi ----
echo "[1/6] Sistem güncelleniyor..."
apt-get update -y
apt-get upgrade -y

# ---- 2. Docker Kurulumu ----
echo "[2/6] Docker kuruluyor..."
apt-get install -y ca-certificates curl gnupg git

# Docker GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Docker repo ekle
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
| tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# ---- 3. DNS Düzelt ----
echo "[3/6] DNS ayarlanıyor..."
rm -f /etc/resolv.conf
echo "nameserver 8.8.8.8" > /etc/resolv.conf
echo "nameserver 1.1.1.1" >> /etc/resolv.conf

# ---- 4. Projeyi İndir ----
echo "[4/6] Proje indiriliyor..."
mkdir -p /opt/muhasebe-sistem
cd /opt/muhasebe-sistem

# GitHub'dan clone (PAT token ile)
if [ ! -d ".git" ]; then
    git clone https://github.com/CDinler/muhasebe-sistem.git .
else
    git pull origin main
fi

# ---- 5. .env Dosyası Oluştur ----
echo "[5/6] .env dosyası oluşturuluyor..."
cat > /opt/muhasebe-sistem/.env << 'ENVEOF'
DB_USER=muhasebe_user
DB_PASSWORD=86a427b417583194faee99deab0dc364
DB_NAME=muhasebe_db
DB_HOST=db
DB_PORT=5432
SECRET_KEY=65bc3e6ecfe544ec838ad01fe7cff2b99b02789d03e461c81ab8e7c39069faca
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALLOWED_ORIGINS=http://185.92.2.82,http://185.92.2.82:80,https://yimak.isletmeyazilim.com
VITE_API_URL=http://185.92.2.82:8000
ENVIRONMENT=production
DEBUG=False
ENVEOF

# ---- 6. Docker Build & Başlat ----
echo "[6/6] Docker build ediliyor ve başlatılıyor..."
cd /opt/muhasebe-sistem
docker compose build --no-cache
docker compose up -d

echo ""
echo "============================================"
echo "  Kurulum tamamlandı!"
echo "  Containerlar başlatılıyor, 30 saniye bekle..."
echo "============================================"
sleep 30

# ---- Veritabanı Tablolarını Oluştur ----
echo "Veritabanı tabloları oluşturuluyor..."
docker exec muhasebe-backend python -c "
from app.core.database import Base, engine
# Tüm modeller import edilmeli (FK bağımlılıkları için)
from app.domains.users.models import User
from app.domains.settings.document_types.models import DocumentType
from app.domains.settings.config.models import SystemConfig, TaxBracket
from app.domains.settings.tax_codes.models import TaxCode
from app.domains.partners.contacts.models import Contact
from app.domains.partners.cost_centers.models import CostCenter
from app.domains.accounting.accounts.models import Account
from app.domains.accounting.transactions.models import Transaction, TransactionLine
from app.domains.personnel.draft_contracts.models import PersonnelDraftContract
from app.domains.personnel.models import Personnel, PersonnelContract
from app.domains.personnel.payroll.models import Payroll
from app.domains.invoicing.einvoices.models import EInvoice
Base.metadata.create_all(bind=engine)
print('Tablolar olusturuldu')
"

# ---- Admin Kullanıcısı Oluştur ----
echo "Admin kullanıcısı oluşturuluyor..."
docker exec muhasebe-backend python -c "
from app.core.database import SessionLocal
from app.domains.users.models import User
from argon2 import PasswordHasher
ph = PasswordHasher()
db = SessionLocal()
existing = db.query(User).filter(User.username == 'admin').first()
if not existing:
    user = User(
        username='admin',
        email='admin@example.com',
        full_name='Admin',
        hashed_password=ph.hash('admin123'),
        role='admin',
        is_active=True
    )
    db.add(user)
    db.commit()
    print('Admin kullanicisi olusturuldu')
else:
    print('Admin zaten mevcut')
db.close()
"

echo ""
echo "============================================"
echo "  KURULUM TAMAMLANDI"
echo "  Site: http://185.92.2.82"
echo "  Giriş: admin / admin123"
echo "============================================"
docker compose ps
