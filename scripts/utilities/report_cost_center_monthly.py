from app.core.database import SessionLocal
from sqlalchemy import text
from datetime import date

# Kullanıcıdan yıl ve ay alınabilir, örnek: 2025-01
SELECTED_YEAR = 2025
SELECTED_MONTH = 1

# Cost center bazında aylık hizmet üretim maliyetleri raporu
# Her cost center için toplam gider, personel maliyeti, hizmet maliyeti, gelir

db = SessionLocal()

print(f"HİZMET ÜRETİM MALİYETLERİ RAPORU - {SELECTED_YEAR}-{SELECTED_MONTH:02d}")
print("="*60)

# SQL: Cost center, hesap tipi, toplam tutar (transactions.cost_center_id)
rows = db.execute(text(f"""
        SELECT 
                cc.id as cost_center_id,
                cc.name as cost_center_name,
                a.account_type,
                SUM(tl.debit) as total_debit,
                SUM(tl.credit) as total_credit
        FROM transaction_lines tl
        JOIN accounts a ON tl.account_id = a.id
        JOIN transactions t ON tl.transaction_id = t.id
        JOIN cost_centers cc ON t.cost_center_id = cc.id
        WHERE YEAR(t.transaction_date) = :year
            AND MONTH(t.transaction_date) = :month
        GROUP BY cc.id, cc.name, a.account_type
        ORDER BY cc.name, a.account_type
"""), {'year': SELECTED_YEAR, 'month': SELECTED_MONTH}).fetchall()

# Raporu cost center bazında grupla
from collections import defaultdict
report = defaultdict(list)
for r in rows:
    report[r.cost_center_name].append({
        'account_type': r.account_type,
        'total_debit': float(r.total_debit or 0),
        'total_credit': float(r.total_credit or 0)
    })


# Excel çıktısı oluştur
import pandas as pd
import os

excel_data = []
for cc_name, items in report.items():
    for item in items:
        excel_data.append({
            'Cost Center': cc_name,
            'Account Type': item['account_type'],
            'Total Debit (Gider)': item['total_debit'],
            'Total Credit (Gelir)': item['total_credit']
        })

df = pd.DataFrame(excel_data)
excel_dir = os.path.join(os.path.dirname(__file__), '../reports')
os.makedirs(excel_dir, exist_ok=True)
excel_path = os.path.join(excel_dir, f"cost_center_report_{SELECTED_YEAR}_{SELECTED_MONTH:02d}.xlsx")
df.to_excel(excel_path, index=False)
print(f"\nExcel çıktısı oluşturuldu: {excel_path}")

for cc_name, items in report.items():
    print(f"\nCost Center: {cc_name}")
    print("----------------------------------------")
    for item in items:
        print(f"  {item['account_type']}: Gider={item['total_debit']:.2f}₺ | Gelir={item['total_credit']:.2f}₺")

print("\nRapor tamamlandı.")
db.close()
