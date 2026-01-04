import pandas as pd
from app.core.database import SessionLocal
from sqlalchemy import text

csv_file = r"C:\Users\CAGATAY\OneDrive\Desktop\MUHASEBE_ANALIZ_v2\muhasebe kayıtları PERSONEL HESAPNOLAR GUCEL.csv"

print("=" * 80)
print("10 HANELİ TCKN ÖRNEKLERİ (CSV vs DB)")
print("=" * 80)

# CSV oku
df = pd.read_csv(csv_file, sep=';', encoding='utf-8-sig')

# 10 haneli TCKN'leri bul
tckn_10_digit = {}
for idx, row in df.iterrows():
    account = str(row['account_id']).strip()
    if account.startswith('335.'):
        tckn = account.replace('335.', '')
        if len(tckn) == 10:
            if account not in tckn_10_digit:
                tckn_10_digit[account] = {
                    'rows': [],
                    'transactions': []
                }
            tckn_10_digit[account]['rows'].append(idx + 2)  # Excel satır no
            
            # Transaction bilgisi
            tx_info = {
                'fis': row.get('transaction_numbe', ''),
                'tarih': row.get('transaction_date', ''),
                'aciklama': row.get('line_description', ''),
                'borc': row.get('debit', 0),
                'alacak': row.get('credit', 0)
            }
            tckn_10_digit[account]['transactions'].append(tx_info)

# Database ile karşılaştır
db = SessionLocal()

print(f"\n📊 CSV'de 10 haneli TCKN: {len(tckn_10_digit)} farklı hesap")
print("\nİLK 30 ÖRNEK:")
print("=" * 80)

for i, (csv_account, info) in enumerate(sorted(tckn_10_digit.items())[:30], 1):
    tckn_10 = csv_account.replace('335.', '')
    
    # DB'de bu TCKN'nin 11 haneli versiyonu var mı?
    db_account_11 = f"335.{tckn_10}0"
    
    # DB'den hesap bilgisi al
    db_result = db.execute(text("""
        SELECT a.code, a.name, COUNT(tl.id) as tx_count
        FROM accounts a
        LEFT JOIN transaction_lines tl ON tl.account_id = a.id
        WHERE a.code = :code
        GROUP BY a.code, a.name
    """), {'code': db_account_11}).first()
    
    print(f"\n{i}. TCKN: {tckn_10}")
    print(f"   CSV: {csv_account}")
    print(f"   CSV satırlar: {info['rows'][:5]}")  # İlk 5 satır
    print(f"   CSV tx sayısı: {len(info['transactions'])}")
    
    if db_result:
        print(f"   DB:  {db_result.code} - {db_result.name}")
        print(f"   DB tx sayısı: {db_result.tx_count}")
        
        if db_result.tx_count > 0:
            print(f"   ⚠️ DB'de transaction VAR ama CSV'de 10 haneli!")
    else:
        print(f"   DB:  Hesap bulunamadı (335.{tckn_10}0)")
    
    # İlk transaction örneği
    if len(info['transactions']) > 0:
        tx = info['transactions'][0]
        print(f"   Örnek TX: {tx['fis']} - {tx['tarih']} - {tx['aciklama'][:40]}")

db.close()

print("\n" + "=" * 80)
print("NOT: Bu TCKN'leri personel kayıtlarından kontrol edin!")
print("Eğer gerçek TCKN 10 haneli ise, DB'deki 11 haneli hesaplar YANLIŞ!")
print("=" * 80)
