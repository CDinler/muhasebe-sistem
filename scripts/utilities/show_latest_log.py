"""
En son sicil upload log dosyasını oku
"""
import os
from pathlib import Path
from datetime import datetime

log_dir = Path(__file__).parent / 'logs'

if not log_dir.exists():
    print("❌ Logs klasörü bulunamadı")
    exit(1)

log_files = list(log_dir.glob('sicil_upload_warnings_*.txt'))

if not log_files:
    print("❌ Hiç log dosyası bulunamadı")
    exit(1)

# En son dosyayı al
latest_log = max(log_files, key=lambda f: f.stat().st_mtime)

print("=" * 80)
print(f"EN SON SICIL UPLOAD LOG")
print("=" * 80)
print(f"Dosya: {latest_log.name}")
print(f"Tarih: {datetime.fromtimestamp(latest_log.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
print()

with open(latest_log, 'r', encoding='utf-8') as f:
    print(f.read())
