from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date
import pandas as pd
from app.models.transaction import Transaction
from app.models.transaction_line import TransactionLine
from app.models.account import Account
from app.models.cost_center import CostCenter

def get_cost_center_monthly_excel(
    db: Session,
    year: int,
    month: int
) -> bytes:
    """
    Cost center bazında aylık hizmet üretim maliyetleri raporu (Excel)
    """
    from io import BytesIO

    sql = text("""
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
    """)
    rows = db.execute(sql, {'year': year, 'month': month}).fetchall()

    data = [
        {
            'Cost Center ID': r.cost_center_id,
            'Cost Center': r.cost_center_name,
            'Hesap Tipi': r.account_type,
            'Toplam Gider (Borç)': float(r.total_debit or 0),
            'Toplam Gelir (Alacak)': float(r.total_credit or 0)
        }
        for r in rows
    ]
    df = pd.DataFrame(data)

    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    return excel_buffer.getvalue()
