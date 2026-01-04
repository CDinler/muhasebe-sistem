import pandas as pd

csv_file = r"C:\Users\CAGATAY\OneDrive\Desktop\MUHASEBE_ANALIZ_v2\muhasebe kayıtları PERSONEL HESAPNOLAR GUCEL.csv"

# DTYPE KULLANMADAN oku (Float olarak okur)
df = pd.read_csv(csv_file, sep=';', encoding='utf-8-sig')

# 335 ile başlayanları filtrele
df_335 = df[df['account_id'].astype(str).str.startswith('335.', na=False)]

print("İlk 20 örnek account_id (Float okuma):")
for i, acc in enumerate(df_335['account_id'].head(20)):
    acc_str = str(acc)
    if acc_str.startswith('335.'):
        tckn = acc_str.replace('335.', '')
        print(f"{i+1}. {acc_str} → TCKN uzunluğu: {len(tckn)}")

# Uzunluk dağılımı
print("\n" + "="*60)
print("TCKN uzunluk dağılımı (Float okuma):")
length_counts = {}
for acc in df_335['account_id']:
    acc_str = str(acc)
    if acc_str.startswith('335.'):
        tckn = acc_str.replace('335.', '')
        length = len(tckn)
        length_counts[length] = length_counts.get(length, 0) + 1

for length in sorted(length_counts.keys()):
    print(f"{length} haneli: {length_counts[length]:,} satır")
