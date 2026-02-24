# Backend Başlatma Scripti
# Sadece app/ klasörünü izler, backend klasöründe script çalıştırınca restart atmaz

# Hata durumunda devam et
$ErrorActionPreference = "Continue"

# Backend klasörüne git
Set-Location C:\Projects\muhasebe-sistem\backend

# PYTHONPATH ayarla
$env:PYTHONPATH = "C:\Projects\muhasebe-sistem\backend"

Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   🚀 BACKEND SUNUCUSU BAŞLATILIYOR" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📂 Klasör: C:\Projects\muhasebe-sistem\backend" -ForegroundColor Gray
Write-Host "📂 İzlenen klasör: app/" -ForegroundColor Gray
Write-Host "🔄 Auto-reload: Aktif (sadece app/ için)" -ForegroundColor Gray
Write-Host "🌐 Adres: http://0.0.0.0:8000" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  Backend klasöründe script çalıştırınca" -ForegroundColor Yellow
Write-Host "   RESTART ATMAYACAK!" -ForegroundColor Yellow
Write-Host ""
Write-Host "⏹️  Durdurmak için: CTRL+C" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════`n" -ForegroundColor Cyan

# Python ve uvicorn kontrolü
Write-Host "🔍 Python kontrolü..." -ForegroundColor Gray
$pythonPath = "..\\.venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    Write-Host "❌ HATA: Virtual environment bulunamadı!" -ForegroundColor Red
    Write-Host "   .venv klasörü eksik. Proje root klasöründe olmalı." -ForegroundColor Yellow
    pause
    exit 1
}
$pythonVersion = & $pythonPath --version 2>&1
Write-Host "✅ $pythonVersion" -ForegroundColor Green

Write-Host "🔍 uvicorn kontrolü..." -ForegroundColor Gray
& $pythonPath -c "import uvicorn" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ HATA: uvicorn modülü bulunamadı!" -ForegroundColor Red
    Write-Host "   Yüklemek için: .\.venv\Scripts\pip install uvicorn" -ForegroundColor Yellow
    pause
    exit 1
}
Write-Host "✅ uvicorn yüklü" -ForegroundColor Green

Write-Host "`n▶️  Backend başlatılıyor...`n" -ForegroundColor Cyan

# Backend'i başlat
try {
    & $pythonPath -m uvicorn app.main:app --reload --reload-dir app --host 0.0.0.0 --port 8000
} catch {
    Write-Host "`n❌ HATA: Backend başlatılamadı!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    pause
    exit 1
}

# Eğer normal kapanırsa (CTRL+C ile)
Write-Host "`n✅ Backend durduruldu." -ForegroundColor Green
pause
