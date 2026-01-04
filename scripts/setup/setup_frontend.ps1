# Frontend Kurulum Scripti
# PowerShell 5.1+

Write-Host "=== MUHASEBE SİSTEMİ FRONTEND KURULUM ===" -ForegroundColor Green

# 1. Node.js kontrolü
Write-Host "`n[1/4] Node.js kontrol ediliyor..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "Node.js versiyonu: $nodeVersion" -ForegroundColor Cyan
} catch {
    Write-Host "HATA: Node.js bulunamadı. Lütfen Node.js kurun." -ForegroundColor Red
    Write-Host "İndirme: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# 2. Dependencies kurulumu
Write-Host "[2/4] Dependencies kuruluyor (npm install)..." -ForegroundColor Yellow
npm install

# 3. .env.local dosyası oluştur
Write-Host "[3/4] .env.local dosyası oluşturuluyor..." -ForegroundColor Yellow
if (-Not (Test-Path .env.local)) {
    Copy-Item .env.example .env.local
    Write-Host ".env.local dosyası oluşturuldu." -ForegroundColor Cyan
}

# 4. Build kontrolü
Write-Host "[4/4] TypeScript kontrolü..." -ForegroundColor Yellow
npm run build

Write-Host "`n✅ Frontend kurulumu tamamlandı!" -ForegroundColor Green
Write-Host "`nGeliştirme modunda çalıştırmak için:" -ForegroundColor Cyan
Write-Host "  npm run dev" -ForegroundColor White
Write-Host "`nProduction build için:" -ForegroundColor Cyan
Write-Host "  npm run build" -ForegroundColor White
