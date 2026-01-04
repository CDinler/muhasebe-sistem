# Son upload loglarını göster
$terminalId = "270ceca3-779f-4538-86f4-c30679302f51"

# Terminal çıktısını al ve DEBUG satırlarını filtrele
Write-Host "=== DEBUG LOGS ===" -ForegroundColor Green
Write-Host ""
Write-Host "Excel'i upload ettikten sonra terminalden son 100 satırı göster:" -ForegroundColor Yellow
Write-Host "Get-Content (Get-PSReadLineOption).HistoryFilePath -Tail 200 | Select-String 'DEBUG|POST.*upload|imported'" -ForegroundColor Cyan
