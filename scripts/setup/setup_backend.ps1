# Backend Kurulum Scripti
# PowerShell 5.1+

Write-Host "=== MUHASEBE SİSTEMİ BACKEND KURULUM ===" -ForegroundColor Green

# 1. Virtual environment oluştur
Write-Host "`n[1/5] Virtual environment oluşturuluyor..." -ForegroundColor Yellow
python -m venv .venv

# 2. Virtual environment aktifleştir
Write-Host "[2/5] Virtual environment aktifleştiriliyor..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1

# 3. Pip güncellemesi
Write-Host "[3/5] Pip güncelleniyor..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# 4. Dependencies kurulumu
Write-Host "[4/5] Dependencies kuruluyor..." -ForegroundColor Yellow
pip install -r requirements.txt

# 5. .env dosyası oluştur
Write-Host "[5/5] .env dosyası oluşturuluyor..." -ForegroundColor Yellow
if (-Not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host ".env dosyası oluşturuldu. Lütfen düzenleyin." -ForegroundColor Cyan
}

Write-Host "`n✅ Backend kurulumu tamamlandı!" -ForegroundColor Green
Write-Host "`nÇalıştırmak için:" -ForegroundColor Cyan
Write-Host "  uvicorn app.main:app --reload" -ForegroundColor White
