import pandas as pd

csv_file = r"C:\Users\CAGATAY\OneDrive\Desktop\MUHASEBE_ANALIZ_v2\muhasebe kayıtları PERSONEL HESAPNOLAR GUCEL.csv"

# String olarak oku
df = pd.read_csv(csv_file, sep=';', encoding='utf-8-sig', dtype={'account_id': str})

# 335 ile başlayan hesapları filtrele
df_335 = df[df['account_id'].str.startswith('335.', na=False)]

print("İlk 20 örnek account_id:")
for i, acc in enumerate(df_335['account_id'].head(20)):
    tckn = acc.replace('335.', '')
    print(f"{i+1}. {acc} → TCKN uzunluğu: {len(tckn)}")

# Uzunluk dağılımı
print("\n" + "="*60)
print("TCKN uzunluk dağılımı:")
length_counts = {}
for acc in df_335['account_id']:
    tckn = acc.replace('335.', '')
    length = len(tckn)
    length_counts[length] = length_counts.get(length, 0) + 1

for length in sorted(length_counts.keys()):
    print(f"{length} haneli: {length_counts[length]:,} satır")
