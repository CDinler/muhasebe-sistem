@echo off
echo ========================================
echo MUHASEBE SISTEMI BASLATILIYOR
echo ========================================
echo.

REM Eski process'leri temizle
echo [0/2] Eski servisler durduruluyor...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Backend*" >nul 2>&1
taskkill /F /IM node.exe /FI "WINDOWTITLE eq Frontend*" >nul 2>&1
timeout /t 2 /nobreak >nul

echo [1/2] BACKEND baslatiliyor (Port 8000)...
start "Backend (Port 8000)" /D "C:\Projects\muhasebe-sistem\backend" cmd /k "C:\Projects\muhasebe-sistem\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo Bekle 5 saniye...
timeout /t 5 /nobreak >nul

echo [2/2] FRONTEND baslatiliyor (Port 5173)...
start "Frontend (Port 5173)" /D "C:\Projects\muhasebe-sistem\frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo HAZIR!
echo ========================================
echo.
echo 2 CMD penceresi acildi - KAPATMAYIN!
echo.
echo 10 saniye bekleyin, sonra tarayicida:
echo http://localhost:5173/einvoices
echo.
echo Bu pencereyi kapatabilirsiniz.
echo.
pause
