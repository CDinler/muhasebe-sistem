import pandas as pd
import os

csv_file = r"C:\Users\CAGATAY\OneDrive\Desktop\MUHASEBE_ANALIZ_v2\muhasebe kayıtları PERSONEL HESAPNOLAR GUCEL.csv"
output_file = r"C:\Users\CAGATAY\OneDrive\Desktop\MUHASEBE_ANALIZ_v2\muhasebe kayıtları PERSONEL HESAPNOLAR DUZELTILMIS.csv"

print("=" * 80)
print("CSV TCKN DÜZELTİCİ")
print("=" * 80)

# CSV oku - DTYPE KULLANMADAN (Float olarak okuyacak, sondaki 0'lar kaybolacak)
print(f"\n📂 Dosya okunuyor: {os.path.basename(csv_file)}")
df = pd.read_csv(csv_file, sep=';', encoding='utf-8-sig')
print(f"✅ {len(df):,} satır okundu")

# İstatistikler
print("\n📊 Düzeltme öncesi durum:")
print("-" * 80)

account_lengths = {}
for idx, row in df.iterrows():
    account = str(row['account_id']).strip()
    if account.startswith('335.'):
        tckn = account.replace('335.', '')
        length = len(tckn)
        if length not in account_lengths:
            account_lengths[length] = 0
        account_lengths[length] += 1

for length in sorted(account_lengths.keys()):
    print(f"{length} haneli TCKN: {account_lengths[length]} satır")

# Düzeltme yap
print("\n🔧 Düzeltme yapılıyor...")
fixed_count = 0

# Yeni account_id listesi oluştur
new_account_ids = []

for idx, row in df.iterrows():
    account = str(row['account_id']).strip()
    
    if account.startswith('335.'):
        tckn = account.replace('335.', '')
        
        # Excel noktalı sayıları float'a çevirip sondaki 0'ları siliyor
        # Örn: 335.10103603060 → 335.1010360306 (float olarak)
        # Bunu düzeltmek için TCKN'i 11 haneli yapalım
        if len(tckn) < 11:
            # SONA 0 ekle (Excel sondaki 0'ı siliyor)
            fixed_tckn = tckn + '0' * (11 - len(tckn))
            fixed_account = f"335.{fixed_tckn}"
            new_account_ids.append(fixed_account)
            fixed_count += 1
            
            if fixed_count <= 10:  # İlk 10 örnek
                print(f"  {account} → {fixed_account}")
        else:
            new_account_ids.append(account)
    else:
        new_account_ids.append(account)

# Tüm account_id kolonunu güncelle
df['account_id'] = new_account_ids

print(f"\n✅ {fixed_count:,} satır düzeltildi")

# Düzeltme sonrası durum
print("\n📊 Düzeltme sonrası durum:")
print("-" * 80)

account_lengths_after = {}
for idx, row in df.iterrows():
    account = str(row['account_id']).strip()
    if account.startswith('335.'):
        tckn = account.replace('335.', '')
        length = len(tckn)
        if length not in account_lengths_after:
            account_lengths_after[length] = 0
        account_lengths_after[length] += 1

for length in sorted(account_lengths_after.keys()):
    print(f"{length} haneli TCKN: {account_lengths_after[length]} satır")

# Yeni dosyaya kaydet
print(f"\n💾 Düzeltilmiş dosya kaydediliyor...")
df.to_csv(output_file, sep=';', index=False, encoding='utf-8-sig')
print(f"✅ Kaydedildi: {os.path.basename(output_file)}")

print("\n" + "=" * 80)
print("TAMAMLANDI!")
print("=" * 80)
print(f"📁 Yeni dosya: {output_file}")
print(f"✅ Toplam düzeltilen satır: {fixed_count:,}")
