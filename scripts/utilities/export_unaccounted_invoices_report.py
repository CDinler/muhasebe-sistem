"""
Muhasebeleştirilmemiş E-Faturalar Raporu (Excel)
- Her fatura için: Fatura No, Tarih, Cari, Tutar, Önerilen Hesap, Önerilen Maliyet Merkezi, Eski Kayıt Açıklaması
"""
import pandas as pd
from sqlalchemy import create_engine, text
from app.core.config import settings

# Bağlantı
engine = create_engine(settings.DATABASE_URL)

SQL = '''
SELECT
  e.id AS einvoice_id,
  e.invoice_number,
  e.issue_date,
  c.name AS contact_name,
  c.tax_number,
  e.payable_amount,
  t.id AS last_transaction_id,
  t.transaction_date AS last_transaction_date,
  t.cost_center_id,
  cc.name AS cost_center_name,
  tl.account_id,
  a.code AS account_code,
  a.name AS account_name,
  t.description AS transaction_description
FROM einvoices e
LEFT JOIN contacts c ON e.contact_id = c.id
LEFT JOIN transaction_lines tl ON tl.contact_id = e.contact_id
LEFT JOIN transactions t ON t.id = tl.transaction_id
LEFT JOIN cost_centers cc ON t.cost_center_id = cc.id
LEFT JOIN accounts a ON tl.account_id = a.id
WHERE e.processing_status IN ('IMPORTED', 'MATCHED', 'ERROR')
ORDER BY e.id, t.transaction_date DESC
'''

def main():
    with engine.connect() as conn:
        df = pd.read_sql(SQL, conn)
    # Her fatura için en güncel eski kaydı seç
    df = df.sort_values(['einvoice_id', 'last_transaction_date'], ascending=[True, False])
    df = df.groupby('einvoice_id').first().reset_index()
    # Excel'e aktar
    df.rename(columns={
        'einvoice_id': 'Fatura ID',
        'invoice_number': 'Fatura No',
        'issue_date': 'Fatura Tarihi',
        'contact_name': 'Cari',
        'tax_number': 'VKN/TCKN',
        'payable_amount': 'Tutar',
        'account_code': 'Önerilen Hesap Kodu',
        'account_name': 'Önerilen Hesap Adı',
        'cost_center_name': 'Önerilen Maliyet Merkezi',
        'transaction_description': 'Eski Kayıt Açıklaması',
    }, inplace=True)
    df.to_excel('unaccounted_invoices_report.xlsx', index=False)
    print('Rapor oluşturuldu: unaccounted_invoices_report.xlsx')

if __name__ == '__main__':
    main()
