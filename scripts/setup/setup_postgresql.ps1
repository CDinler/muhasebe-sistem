# PostgreSQL Database Hızlı Kurulum
# PowerShell 5.1+

Write-Host "=== POSTGRESQL DATABASE KURULUM ===" -ForegroundColor Green

$dbName = "muhasebe_db"
$dbUser = "postgres"
$dbPassword = Read-Host "PostgreSQL postgres kullanıcı şifresi" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPassword)
$dbPasswordPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

Write-Host "`n[1/4] PostgreSQL bağlantı kontrolü..." -ForegroundColor Yellow

try {
    $env:PGPASSWORD = $dbPasswordPlain
    $result = psql -U $dbUser -c "SELECT version();" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ PostgreSQL bağlantısı başarılı" -ForegroundColor Green
    } else {
        Write-Host "✗ PostgreSQL'e bağlanılamadı" -ForegroundColor Red
        Write-Host "pgAdmin kullanarak manuel kurulum yapın." -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "✗ psql komutu bulunamadı" -ForegroundColor Red
    Write-Host "pgAdmin kullanarak manuel kurulum yapın." -ForegroundColor Yellow
    exit 1
}

Write-Host "`n[2/4] Database oluşturuluyor..." -ForegroundColor Yellow
psql -U $dbUser -c "DROP DATABASE IF EXISTS $dbName;" 2>$null
psql -U $dbUser -c "CREATE DATABASE $dbName WITH ENCODING='UTF8';"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Database oluşturuldu: $dbName" -ForegroundColor Green
} else {
    Write-Host "✗ Database oluşturulamadı" -ForegroundColor Red
    exit 1
}

Write-Host "`n[3/4] Schema yükleniyor..." -ForegroundColor Yellow
$schemaFile = "C:\Projects\muhasebe-sistem\database\schema.sql"
psql -U $dbUser -d $dbName -f $schemaFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Schema yüklendi" -ForegroundColor Green
} else {
    Write-Host "✗ Schema yüklenemedi" -ForegroundColor Red
}

Write-Host "`n[4/4] Seed data yükleniyor..." -ForegroundColor Yellow
psql -U $dbUser -d $dbName -f "C:\Projects\muhasebe-sistem\database\seeds\01_accounts.sql"
psql -U $dbUser -d $dbName -f "C:\Projects\muhasebe-sistem\database\seeds\02_cost_centers.sql"

Remove-Item Env:\PGPASSWORD

Write-Host "`n✅ Database kurulumu tamamlandı!" -ForegroundColor Green
Write-Host "`nBağlantı bilgileri:" -ForegroundColor Cyan
Write-Host "  Host: localhost" -ForegroundColor White
Write-Host "  Port: 5432" -ForegroundColor White
Write-Host "  Database: $dbName" -ForegroundColor White
Write-Host "  User: $dbUser" -ForegroundColor White
Write-Host "`nConnection String:" -ForegroundColor Cyan
Write-Host "  postgresql://${dbUser}:ŞİFRENİZ@localhost:5432/$dbName" -ForegroundColor White

Write-Host "`nSONRAKİ ADIM: Backend .env dosyasını güncelleyin" -ForegroundColor Yellow
