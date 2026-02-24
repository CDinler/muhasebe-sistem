/**
 * Reports Types
 * Finansal raporlar için TypeScript interfaces
 */

export interface MizanItem {
  account_code: string;
  account_name: string;
  opening_debit: number;
  opening_credit: number;
  period_debit: number;
  period_credit: number;
  closing_debit: number;
  closing_credit: number;
}

export interface MizanReport {
  start_date: string;
  end_date: string;
  items: MizanItem[];
  total_opening_debit: number;
  total_opening_credit: number;
  total_period_debit: number;
  total_period_credit: number;
  total_closing_debit: number;
  total_closing_credit: number;
}

export interface IncomeStatementItem {
  account_code: string;
  account_name: string;
  amount: number;
}

export interface IncomeStatement {
  start_date: string;
  end_date: string;
  income_items: IncomeStatementItem[];
  expense_items: IncomeStatementItem[];
  total_income: number;
  total_expense: number;
  net_profit: number;
}

export interface DebtorCreditorItem {
  contact_id: number;
  contact_name: string;
  tax_number?: string;
  debit: number;
  credit: number;
  balance: number;
}

export interface DebtorCreditorReport {
  start_date: string;
  end_date: string;
  debtors: DebtorCreditorItem[];
  creditors: DebtorCreditorItem[];
  total_debtors: number;
  total_creditors: number;
  net_balance: number;
}

export interface CariReportItem {
  transaction_id: number;
  transaction_number: string;
  transaction_date: string;
  due_date?: string;
  document_type?: string;
  description?: string;
  account_code: string;
  account_name: string;
  account_type: string;
  currency?: string;
  currency_debit?: number;
  currency_credit?: number;
  currency_balance?: number;
  debit: number;
  credit: number;
  balance: number;
  has_collateral?: boolean; // Bu fişte 326 hesabı var mı (nakit teminat)
}

export interface CariReport {
  contact_id?: number;
  contact_code?: string;
  contact_name: string;
  tax_number?: string;
  start_date: string;
  end_date: string;
  opening_balance: number;
  items: CariReportItem[];
  closing_balance: number;
  total_debit: number;
  total_credit: number;
}

export interface MuavinReportItem {
  transaction_id: number;
  transaction_number: string;
  transaction_date: string;
  description?: string;
  debit: number;
  credit: number;
  balance: number;
}

export interface MuavinReport {
  account_code?: string;
  account_name: string;
  start_date: string;
  end_date: string;
  opening_balance: number;
  items: MuavinReportItem[];
  closing_balance: number;
  total_debit: number;
  total_credit: number;
}

export interface ReportParams {
  start_date: string;
  end_date: string;
  cost_center_id?: number;
  contact_id?: number;
  account_code?: string;
}
