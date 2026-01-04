# PostgreSQL Kurulum Kontrol Scripti
# PowerShell 5.1+

Write-Host "=== MUHASEBE SİSTEMİ DATABASE KONTROL ===" -ForegroundColor Green

Write-Host "`n[1/3] PostgreSQL kontrol ediliyor..." -ForegroundColor Yellow

# PostgreSQL kontrolü
try {
    $psqlVersion = psql --version
    Write-Host "PostgreSQL versiyonu: $psqlVersion" -ForegroundColor Cyan
} catch {
    Write-Host "UYARI: psql komut satırı bulunamadı." -ForegroundColor Yellow
    Write-Host "PostgreSQL kurulu değilse indirin:" -ForegroundColor Yellow
    Write-Host "  https://www.postgresql.org/download/windows/" -ForegroundColor White
    Write-Host "`nveya pgAdmin kullanarak database oluşturun." -ForegroundColor Cyan
}

Write-Host "`n[2/3] Database oluşturma adımları:" -ForegroundColor Yellow
Write-Host "  1. pgAdmin veya psql'i açın" -ForegroundColor White
Write-Host "  2. Yeni database oluşturun: muhasebe_db" -ForegroundColor White
Write-Host "  3. Owner: postgres (veya istediğiniz kullanıcı)" -ForegroundColor White

Write-Host "`n[3/3] Schema yükleme:" -ForegroundColor Yellow
Write-Host "  Manuel yükleme için:" -ForegroundColor Cyan
Write-Host "  psql -U postgres -f database/schema.sql" -ForegroundColor White
Write-Host "  psql -U postgres -d muhasebe_db -f database/seeds/01_accounts.sql" -ForegroundColor White
Write-Host "  psql -U postgres -d muhasebe_db -f database/seeds/02_cost_centers.sql" -ForegroundColor White

Write-Host "`nveya pgAdmin kullanarak:" -ForegroundColor Cyan
Write-Host "  1. pgAdmin'i aç" -ForegroundColor White
Write-Host "  2. Servers > PostgreSQL > Databases sağ tık > Create > Database" -ForegroundColor White
Write-Host "  3. Name: muhasebe_db, Owner: postgres" -ForegroundColor White
Write-Host "  4. Query Tool'da schema.sql dosyasını çalıştır" -ForegroundColor White

Write-Host "`n✅ Database kontrol tamamlandı!" -ForegroundColor Green
Write-Host "`nSONRAKİ ADIM: PostgreSQL'de muhasebe_db oluşturun, schema.sql'i çalıştırın" -ForegroundColor Cyan
