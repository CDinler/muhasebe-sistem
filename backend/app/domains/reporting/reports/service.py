"""
Reports Service
Business logic for financial reports
"""
from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import text


class ReportsService:
    """Raporlama business logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_mizan_report(
        self,
        start_date: date,
        end_date: date,
        cost_center_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Mizan (Trial Balance) raporu"""
        # Opening balances (before start_date)
        opening_query = text("""
            SELECT 
                a.code,
                a.name,
                COALESCE(SUM(tl.debit), 0) as opening_debit,
                COALESCE(SUM(tl.credit), 0) as opening_credit
            FROM accounts a
            LEFT JOIN transaction_lines tl ON a.id = tl.account_id
            LEFT JOIN transactions t ON tl.transaction_id = t.id
            WHERE t.transaction_date < :start_date
            AND t.draft = 0
            GROUP BY a.id, a.code, a.name
        """)
        
        # Period movements
        period_query = text("""
            SELECT 
                a.code,
                a.name,
                COALESCE(SUM(tl.debit), 0) as period_debit,
                COALESCE(SUM(tl.credit), 0) as period_credit
            FROM accounts a
            LEFT JOIN transaction_lines tl ON a.id = tl.account_id
            LEFT JOIN transactions t ON tl.transaction_id = t.id
            WHERE t.transaction_date BETWEEN :start_date AND :end_date
            AND t.draft = 0
            GROUP BY a.id, a.code, a.name
        """)
        
        opening_result = {row.code: row for row in self.db.execute(opening_query, {"start_date": start_date})}
        period_result = self.db.execute(period_query, {"start_date": start_date, "end_date": end_date})
        
        items = []
        total_opening_debit = Decimal('0')
        total_opening_credit = Decimal('0')
        total_period_debit = Decimal('0')
        total_period_credit = Decimal('0')
        total_closing_debit = Decimal('0')
        total_closing_credit = Decimal('0')
        
        for row in period_result:
            opening = opening_result.get(row.code)
            opening_debit = Decimal(str(round(float(opening.opening_debit or 0), 2))) if opening else Decimal('0')
            opening_credit = Decimal(str(round(float(opening.opening_credit or 0), 2))) if opening else Decimal('0')
            period_debit = Decimal(str(round(float(row.period_debit or 0), 2)))
            period_credit = Decimal(str(round(float(row.period_credit or 0), 2)))
            
            closing_balance = (opening_debit - opening_credit) + (period_debit - period_credit)
            closing_debit = closing_balance if closing_balance > 0 else Decimal('0')
            closing_credit = -closing_balance if closing_balance < 0 else Decimal('0')
            
            if period_debit > 0 or period_credit > 0 or opening_debit > 0 or opening_credit > 0:
                items.append({
                    "account_code": row.code,
                    "account_name": row.name,
                    "opening_debit": opening_debit,
                    "opening_credit": opening_credit,
                    "period_debit": period_debit,
                    "period_credit": period_credit,
                    "closing_debit": closing_debit,
                    "closing_credit": closing_credit
                })
                
                total_opening_debit += opening_debit
                total_opening_credit += opening_credit
                total_period_debit += period_debit
                total_period_credit += period_credit
                total_closing_debit += closing_debit
                total_closing_credit += closing_credit
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "items": items,
            "total_opening_debit": total_opening_debit,
            "total_opening_credit": total_opening_credit,
            "total_period_debit": total_period_debit,
            "total_period_credit": total_period_credit,
            "total_closing_debit": total_closing_debit,
            "total_closing_credit": total_closing_credit
        }
    
    def get_income_statement(
        self,
        start_date: date,
        end_date: date,
        cost_center_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Gelir Tablosu (Income Statement)"""
        query = text("""
            SELECT 
                a.code,
                a.name,
                a.account_type,
                SUM(tl.debit - tl.credit) as balance
            FROM accounts a
            LEFT JOIN transaction_lines tl ON a.id = tl.account_id
            LEFT JOIN transactions t ON tl.transaction_id = t.id
            WHERE t.transaction_date BETWEEN :start_date AND :end_date
            AND t.draft = 0
            AND (a.code LIKE '6%' OR a.code LIKE '7%')
            GROUP BY a.id, a.code, a.name, a.account_type
            ORDER BY a.code
        """)
        
        result = self.db.execute(
            query,
            {"start_date": start_date, "end_date": end_date}
        )
        
        income = []
        expenses = []
        
        for row in result:
            item = {
                "account_code": row.code,
                "account_name": row.name,
                "amount": Decimal(str(round(float(row.balance or 0), 2)))
            }
            if row.code.startswith('6'):
                expenses.append(item)
            else:
                income.append(item)
        
        total_income = sum(item["amount"] for item in income)
        total_expenses = sum(item["amount"] for item in expenses)
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "income_items": income,
            "expense_items": expenses,
            "total_income": total_income,
            "total_expense": total_expenses,
            "net_profit": total_income - total_expenses
        }
    
    def get_debtor_creditor_report(
        self,
        start_date: date,
        end_date: date,
        cost_center_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Borç/Alacak raporu"""
        query = text("""
            SELECT 
                c.id as contact_id,
                c.name as contact_name,
                c.tax_number,
                SUM(tl.debit) as total_debit,
                SUM(tl.credit) as total_credit
            FROM contacts c
            JOIN accounts a ON a.contact_id = c.id
            JOIN transaction_lines tl ON a.id = tl.account_id
            JOIN transactions t ON tl.transaction_id = t.id
            WHERE t.transaction_date BETWEEN :start_date AND :end_date
            AND t.draft = 0
            AND (a.code LIKE '1%' OR a.code LIKE '3%')
            GROUP BY c.id, c.name, c.tax_number
            HAVING total_debit > 0 OR total_credit > 0
            ORDER BY c.name
        """)
        
        result = self.db.execute(
            query,
            {"start_date": start_date, "end_date": end_date}
        )
        
        debtors = []
        creditors = []
        total_debtors_amount = Decimal('0')
        total_creditors_amount = Decimal('0')
        
        for row in result:
            debit = Decimal(str(round(float(row.total_debit or 0), 2)))
            credit = Decimal(str(round(float(row.total_credit or 0), 2)))
            balance = debit - credit
            
            item = {
                "contact_id": row.contact_id,
                "contact_name": row.contact_name,
                "tax_number": row.tax_number,
                "debit": debit,
                "credit": credit,
                "balance": abs(balance)
            }
            
            if balance > 0:
                debtors.append(item)
                total_debtors_amount += balance
            elif balance < 0:
                creditors.append(item)
                total_creditors_amount += abs(balance)
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "debtors": debtors,
            "creditors": creditors,
            "total_debtors": total_debtors_amount,
            "total_creditors": total_creditors_amount,
            "net_balance": total_debtors_amount - total_creditors_amount
        }
    
    def get_cari_report(
        self,
        start_date: date,
        end_date: date,
        contact_id: Optional[int] = None,
        account_filter: Optional[list] = None
    ) -> Dict[str, Any]:
        """Cari hesap raporu - fiş fiş detay"""
        if not contact_id:
            raise ValueError("contact_id is required for cari report")
        
        # Get contact info
        from app.models import Contact
        contact = self.db.query(Contact).filter(Contact.id == contact_id).first()
        if not contact:
            raise ValueError(f"Contact {contact_id} not found")
        
        # Build account filter condition
        account_filter_sql = ""
        if account_filter:
            conditions = []
            if '120' in account_filter:
                conditions.append("a.code LIKE '120%'")
            if '320' in account_filter:
                conditions.append("a.code LIKE '320%'")
            if 'collateral' in account_filter or '326' in account_filter:
                conditions.append("a.code LIKE '326%'")
            if conditions:
                account_filter_sql = f"AND ({' OR '.join(conditions)})"
        
        # Calculate opening balance (before start_date)
        opening_query = text(f"""
            SELECT 
                COALESCE(SUM(tl.debit), 0) as total_debit,
                COALESCE(SUM(tl.credit), 0) as total_credit
            FROM transaction_lines tl
            JOIN transactions t ON tl.transaction_id = t.id
            JOIN accounts a ON tl.account_id = a.id
            WHERE a.contact_id = :contact_id
            AND t.transaction_date < :start_date
            AND t.draft = 0
            {account_filter_sql}
        """)
        opening_result = self.db.execute(opening_query, {
            "contact_id": contact_id,
            "start_date": start_date
        }).fetchone()
        
        opening_balance = Decimal(str(round(float(opening_result.total_debit or 0) - float(opening_result.total_credit or 0), 2)))
        
        # Get transactions in period with account type flags
        query = text(f"""
            SELECT 
                t.id as transaction_id,
                t.transaction_number,
                t.transaction_date,
                t.description,
                a.code as account_code,
                a.name as account_name,
                dt.name as document_type,
                tl.debit,
                tl.credit,
                CASE 
                    WHEN a.code LIKE '120%' THEN 'customer'
                    WHEN a.code LIKE '320%' THEN 'supplier'
                    ELSE 'other'
                END as account_type,
                CASE WHEN a.code LIKE '326%' THEN 1 ELSE 0 END as is_collateral
            FROM transaction_lines tl
            JOIN transactions t ON tl.transaction_id = t.id
            JOIN accounts a ON tl.account_id = a.id
            LEFT JOIN document_types dt ON t.document_type_id = dt.id
            WHERE a.contact_id = :contact_id
            AND t.transaction_date BETWEEN :start_date AND :end_date
            AND t.draft = 0
            {account_filter_sql}
            ORDER BY t.transaction_date, t.id
        """)
        
        result = self.db.execute(query, {
            "contact_id": contact_id,
            "start_date": start_date,
            "end_date": end_date
        })
        
        items = []
        running_balance = opening_balance
        total_debit = Decimal('0')
        total_credit = Decimal('0')
        has_120 = False
        has_320 = False
        has_326 = False
        account_codes = []  # Kullanılan hesap kodlarını topla
        
        for row in result:
            debit = Decimal(str(round(float(row.debit or 0), 2)))
            credit = Decimal(str(round(float(row.credit or 0), 2)))
            running_balance = Decimal(str(round(float(running_balance) + float(debit) - float(credit), 2)))
            
            if row.account_code.startswith('120'):
                has_120 = True
            elif row.account_code.startswith('320'):
                has_320 = True
            elif row.account_code.startswith('326'):
                has_326 = True
            
            # Hesap kodunu ekle (tekrarları önle)
            if row.account_code not in account_codes:
                account_codes.append(row.account_code)
            
            items.append({
                "transaction_id": row.transaction_id,
                "transaction_number": row.transaction_number,
                "transaction_date": row.transaction_date,
                "due_date": None,  # TODO: vade tarihini transaction'dan al
                "document_type": row.document_type,
                "description": row.description,
                "account_code": row.account_code,
                "account_name": row.account_name,
                "account_type": row.account_type,
                "currency": None,  # TODO: döviz bilgisi
                "currency_debit": None,
                "currency_credit": None,
                "currency_balance": None,
                "debit": debit,
                "credit": credit,
                "balance": running_balance,
                "has_collateral": bool(row.is_collateral)
            })
            
            total_debit += debit
            total_credit += credit
        
        # Filtreye göre hesap kodunu belirle
        display_account_code = contact.code  # Varsayılan: cari kodu
        if account_codes:
            # İlk hesap kodunu al (çoğunlukla tek hesap olur)
            display_account_code = account_codes[0] if len(account_codes) == 1 else ', '.join(account_codes)
        
        return {
            "contact_id": contact_id,
            "contact_code": display_account_code,  # Artık hesap kodunu göster
            "contact_name": contact.name,
            "tax_number": contact.tax_number,
            "start_date": start_date,
            "end_date": end_date,
            "opening_balance": opening_balance,
            "items": items,
            "closing_balance": running_balance,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "has_120_account": has_120,
            "has_320_account": has_320,
            "has_326_account": has_326
        }
    
    def get_muavin_report(
        self,
        start_date: date,
        end_date: date,
        account_code: Optional[str] = None,
        cost_center_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Muavin defteri (General Ledger)"""
        if not account_code:
            raise ValueError("account_code is required for muavin report")
        
        # Get account info
        account_query = text("""
            SELECT code, name FROM accounts WHERE code = :account_code
        """)
        account_result = self.db.execute(account_query, {"account_code": account_code}).fetchone()
        
        if not account_result:
            raise ValueError(f"Account {account_code} not found")
        
        account_name = account_result.name
        
        # Calculate opening balance (before start_date)
        opening_query = text("""
            SELECT 
                COALESCE(SUM(tl.debit), 0) as total_debit,
                COALESCE(SUM(tl.credit), 0) as total_credit
            FROM transaction_lines tl
            JOIN transactions t ON tl.transaction_id = t.id
            JOIN accounts a ON tl.account_id = a.id
            WHERE a.code = :account_code
            AND t.transaction_date < :start_date
            AND t.draft = 0
        """)
        opening_result = self.db.execute(opening_query, {
            "account_code": account_code,
            "start_date": start_date
        }).fetchone()
        
        opening_balance = Decimal(str(round(float(opening_result.total_debit or 0) - float(opening_result.total_credit or 0), 2)))
        
        # Get transactions in period
        query = text("""
            SELECT 
                t.id as transaction_id,
                t.transaction_date,
                t.transaction_number,
                t.description,
                a.code as account_code,
                a.name as account_name,
                tl.debit,
                tl.credit
            FROM transaction_lines tl
            JOIN transactions t ON tl.transaction_id = t.id
            JOIN accounts a ON tl.account_id = a.id
            WHERE t.transaction_date BETWEEN :start_date AND :end_date
            AND t.draft = 0
            AND a.code = :account_code
            ORDER BY t.transaction_date, t.id
        """)
        
        result = self.db.execute(query, {
            "start_date": start_date,
            "end_date": end_date,
            "account_code": account_code
        })
        
        items = []
        running_balance = opening_balance
        total_debit = Decimal('0')
        total_credit = Decimal('0')
        
        for row in result:
            debit = Decimal(str(round(float(row.debit or 0), 2)))
            credit = Decimal(str(round(float(row.credit or 0), 2)))
            running_balance = Decimal(str(round(float(running_balance) + float(debit) - float(credit), 2)))
            
            items.append({
                "transaction_id": row.transaction_id,
                "transaction_number": row.transaction_number,
                "transaction_date": row.transaction_date,
                "description": row.description,
                "debit": debit,
                "credit": credit,
                "balance": running_balance
            })
            
            total_debit += debit
            total_credit += credit
        
        return {
            "account_code": account_code,
            "account_name": account_name,
            "start_date": start_date,
            "end_date": end_date,
            "opening_balance": opening_balance,
            "items": items,
            "closing_balance": running_balance,
            "total_debit": total_debit,
            "total_credit": total_credit
        }
