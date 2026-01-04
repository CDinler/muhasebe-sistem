"""
process_unaccounted_einvoices.py

İşlenmemiş e-faturaları otomatik olarak muhasebeleştirir.
- Her fatura için eski kayıtlara bakarak önerilen hesap ve maliyet merkezi ile yevmiye fişi oluşturur.
- Fiş numarası transaction_counter tablosundan atomik olarak alınır.
- Fatura işlendikten sonra processing_status güncellenir.

Kullanım:
python backend/process_unaccounted_einvoices.py

Not: Script üzerinde birlikte çalışmak için bolca açıklama ve TODO bırakılmıştır.
"""
import pandas as pd
from sqlalchemy import create_engine, text
from app.core.config import settings

# TODO: Gerekirse ORM ile model importları eklenebilir

engine = create_engine(settings.DATABASE_URL)

# 1. İşlenmemiş faturaları bul
SQL_UNACCOUNTED = '''
SELECT e.id, e.invoice_number, e.issue_date, e.contact_id, e.payable_amount
FROM einvoices e
WHERE e.processing_status IN ('IMPORTED', 'MATCHED', 'ERROR')
  AND e.contact_id IS NOT NULL
'''

# 2. Her fatura için eski yevmiye kaydını bul
SQL_LAST_TX = '''
SELECT t.id, t.cost_center_id, cc.name as cost_center_name, tl.account_id, a.code as account_code, a.name as account_name
FROM transactions t
JOIN transaction_lines tl ON tl.transaction_id = t.id
JOIN accounts a ON tl.account_id = a.id
LEFT JOIN cost_centers cc ON t.cost_center_id = cc.id
WHERE tl.contact_id = :contact_id
ORDER BY t.transaction_date DESC
LIMIT 1
'''

# 3. Yeni fiş oluştur (örnek, atomik fiş numarası alma)
SQL_NEXT_FIS_NO = '''
UPDATE transaction_counter SET last_number = last_number + 1 WHERE id = 1;
SELECT last_number FROM transaction_counter WHERE id = 1;
'''

# 4. Fiş ve satır ekleme, fatura güncelleme için TODO bırakıldı

def main():
    with engine.connect() as conn:
        # 1. İşlenmemiş faturaları çek
        df = pd.read_sql(SQL_UNACCOUNTED, conn)
        print(f"Toplam işlenmemiş fatura: {len(df)}")
        for idx, row in df.iterrows():
            # === Cari kontrolü ===
            contact_id = row['contact_id']
            invoice_id = row['id']
            invoice_number = row['invoice_number']
            amount = row['payable_amount']
            vkn = None
            # VKN/TCKN faturadan alınabiliyorsa ekle (örnek: tax_number alanı varsa)
            if 'tax_number' in row and row['tax_number']:
                vkn = row['tax_number']

            if not contact_id:
                if vkn:
                    cari = conn.execute(text("SELECT id FROM contacts WHERE tax_number = :vkn"), {"vkn": vkn}).fetchone()
                    if cari:
                        contact_id = cari.id
                        print(f"Fatura {invoice_number}: VKN {vkn} ile cari bulundu (id={contact_id})")
                    else:
                        print(f"Fatura {invoice_number}: VKN {vkn} ile cari bulunamadı, yeni cari açılmalı! (Manuel kontrol gerek)")
                        # TODO: Burada yeni cari açma kodu eklenebilir
                        continue
                else:
                    print(f"Fatura {invoice_number}: VKN/TCKN yok, manuel eşleştirme gerekli!")
                    # TODO: Manuel eşleştirme için log/işaretleme eklenebilir
                    continue
            # === Eski yevmiye kaydını bul ===
            tx = conn.execute(text(SQL_LAST_TX), {'contact_id': contact_id}).fetchone()
            if not tx:
                print(f"Fatura {invoice_number}: Eski kayıt yok, manuel işlem gerek!")
                continue
            # === Yeni fiş numarası al ===
            fis_no_result = conn.execute(text(SQL_NEXT_FIS_NO)).fetchall()
            fis_no = fis_no_result[-1][0] if fis_no_result else None
            fis_code = f"F{fis_no:08d}" if fis_no else "F00000000"
            print(f"Fatura {invoice_number}: Yeni fiş no {fis_code}, Cost Center: {tx.cost_center_name}, Hesap: {tx.account_code}")
            # TODO: Burada transaction ve transaction_line ekleme kodu yazılacak
            # TODO: Fatura processing_status 'TRANSACTION_CREATED' olarak güncellenecek
            # TODO: Hatalar ve loglama eklenecek

if __name__ == '__main__':
    main()
