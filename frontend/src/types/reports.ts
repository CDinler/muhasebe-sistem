export interface CariReportItem {
  transaction_id: number;
  transaction_number: string;
  transaction_date: string;
  due_date: string | null;
  document_type: string | null;
  description: string | null;
  account_code: string;
  account_name: string;
  account_type: string;
  currency: string | null;
  currency_debit: number | null;
  currency_credit: number | null;
  currency_balance: number | null;
  debit: number;
  credit: number;
  balance: number;
}

export interface CariReport {
  contact_id: number | null;
  contact_code: string | null;
  contact_name: string;
  tax_number: string | null;
  start_date: string;
  end_date: string;
  opening_balance: number;
  items: CariReportItem[];
  closing_balance: number;
  total_debit: number;
  total_credit: number;
  has_120_account: boolean;
  has_320_account: boolean;
  has_326_account: boolean;
}
