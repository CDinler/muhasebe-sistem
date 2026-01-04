# PostgreSQL Portable Kurulum (Onaysız)
# Bu script PostgreSQL'i tamamen otomatik kurar

$ErrorActionPreference = "Stop"
$ProgressPreference = 'SilentlyContinue'

Write-Host "=== PostgreSQL Portable Kurulum Basliyor ===" -ForegroundColor Cyan

# Kurulum dizinleri
$pgDir = "C:\PostgreSQL\15"
$pgDataDir = "$pgDir\data"
$pgPassword = "postgres123"

# Zaten kurulu mu kontrol et
if (Test-Path "$pgDir\bin\postgres.exe") {
    Write-Host "PostgreSQL zaten kurulu: $pgDir" -ForegroundColor Yellow
    
    # PATH'e ekle
    $env:Path = "$pgDir\bin;$env:Path"
    [System.Environment]::SetEnvironmentVariable("Path", "$pgDir\bin;" + [System.Environment]::GetEnvironmentVariable("Path", "Machine"), "Machine")
    
    Write-Host "PostgreSQL servisi baslatiiliyor..." -ForegroundColor Green
    Start-Service postgresql-x64-15 -ErrorAction SilentlyContinue
    
    Write-Host "`nPostgreSQL hazir!" -ForegroundColor Green
    Write-Host "Host: localhost" -ForegroundColor White
    Write-Host "Port: 5432" -ForegroundColor White
    Write-Host "User: postgres" -ForegroundColor White
    Write-Host "Password: $pgPassword" -ForegroundColor White
    exit 0
}

Write-Host "[1/5] Kurulum dizini olusturuluyor..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $pgDir -Force | Out-Null

Write-Host "[2/5] PostgreSQL indiriliyor (344 MB)..." -ForegroundColor Yellow
Write-Host "      Alternatif kaynak kullaniliyor..." -ForegroundColor Gray

# PostgreSQL Binaries (zip) indir
$zipUrl = "https://sbp.enterprisedb.com/getfile.jsp?fileid=1258893"
$zipFile = "$env:TEMP\postgresql-15-windows-x64-binaries.zip"

try {
    # Wget ile indir
    Invoke-WebRequest -Uri "https://www.enterprisedb.com/download-postgresql-binaries" -OutFile "$env:TEMP\pg_page.html" -ErrorAction SilentlyContinue
    
    Write-Host "      Direkt binary dosyalari indiriliyor..." -ForegroundColor Gray
    
    # Manuel link (EDB binaries)
    $directUrl = "https://sbp.enterprisedb.com/getfile.jsp?fileid=1258910"
    Invoke-WebRequest -Uri $directUrl -OutFile $zipFile -UseBasicParsing
    
} catch {
    Write-Host "      Ana sunucu calismiyor, yedek kaynak kullaniliyor..." -ForegroundColor Yellow
    
    # PostgreSQL.org mirror
    $mirrorUrl = "https://ftp.postgresql.org/pub/binary/v15.10/win32/postgresql-15.10-1-windows-x64-binaries.zip"
    try {
        Invoke-WebRequest -Uri $mirrorUrl -OutFile $zipFile -UseBasicParsing
    } catch {
        Write-Host "      HATA: PostgreSQL indirilemedi. Manuel kurulum gerekli." -ForegroundColor Red
        Write-Host "`nManuel Kurulum:" -ForegroundColor Cyan
        Write-Host "1. Git: https://www.postgresql.org/download/windows/" -ForegroundColor White
        Write-Host "2. PostgreSQL 15'i indir ve kur" -ForegroundColor White
        Write-Host "3. Sifre: postgres123" -ForegroundColor White
        Write-Host "4. Kurulum bittikten sonra: .\setup_postgresql.ps1" -ForegroundColor White
        exit 1
    }
}

Write-Host "[3/5] Arsiv aciliyor..." -ForegroundColor Yellow
Expand-Archive -Path $zipFile -DestinationPath "C:\PostgreSQL" -Force

Write-Host "[4/5] PostgreSQL yapilandiriliyor..." -ForegroundColor Yellow

# initdb calistir
& "$pgDir\bin\initdb.exe" -D $pgDataDir -U postgres --pwfile=<(echo $pgPassword) --encoding=UTF8 --locale=C

# postgresql.conf ayarlari
@"
listen_addresses = 'localhost'
port = 5432
max_connections = 100
shared_buffers = 128MB
"@ | Out-File -FilePath "$pgDataDir\postgresql.conf" -Append -Encoding UTF8

Write-Host "[5/5] Servis olusturuluyor..." -ForegroundColor Yellow

# Windows Service olustur
& "$pgDir\bin\pg_ctl.exe" register -N postgresql-x64-15 -D $pgDataDir -U postgres

# Servisi baslat
Start-Service postgresql-x64-15

# PATH'e ekle
[System.Environment]::SetEnvironmentVariable("Path", "$pgDir\bin;" + [System.Environment]::GetEnvironmentVariable("Path", "Machine"), "Machine")
$env:Path = "$pgDir\bin;$env:Path"

Write-Host "`n=== PostgreSQL Basariyla Kuruldu ===" -ForegroundColor Green
Write-Host "Konum: $pgDir" -ForegroundColor White
Write-Host "Host: localhost" -ForegroundColor White
Write-Host "Port: 5432" -ForegroundColor White
Write-Host "User: postgres" -ForegroundColor White
Write-Host "Password: $pgPassword" -ForegroundColor Yellow
Write-Host "`nDatabase olusturmak icin: .\setup_postgresql.ps1" -ForegroundColor Cyan
