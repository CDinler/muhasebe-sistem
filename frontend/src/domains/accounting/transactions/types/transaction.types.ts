/**
 * Transaction Types
 * 
 * Muhasebe fişi ve satır tipleri
 */

export interface TransactionLine {
  id?: number;
  transaction_id?: number;
  account_id: number;
  contact_id?: number | null;
  description?: string | null;
  debit?: number | null;
  credit?: number | null;
  quantity?: number | null;
  unit?: string | null;
  vat_rate?: number | null;
  withholding_rate?: number | null;
  vat_base?: number | null;
  
  // Relations (populated by backend)
  account?: {
    id: number;
    code: string;
    name: string;
  };
  contact?: {
    id: number;
    name: string;
  };
}

export interface Transaction {
  id?: number;
  transaction_number: string;
  transaction_date: string; // YYYY-MM-DD
  accounting_period: string; // YYYY-MM
  cost_center_id?: number | null;
  description?: string | null;
  document_type?: string | null;
  document_subtype?: string | null;
  document_number?: string | null;
  related_invoice_number?: string | null;
  
  // Relations
  lines?: TransactionLine[];
  cost_center?: {
    id: number;
    code: string;
    name: string;
  };
  doc_type?: {
    id: number;
    name: string;
  };
  doc_subtype?: {
    id: number;
    name: string;
  };
}

export interface TransactionCreate {
  transaction_number: string;
  transaction_date: string;
  accounting_period: string;
  cost_center_id?: number | null;
  description?: string | null;
  document_type?: string | null;
  document_subtype?: string | null;
  document_number?: string | null;
  related_invoice_number?: string | null;
  lines: TransactionLine[];
}

export interface TransactionFilters {
  skip?: number;
  limit?: number;
  date_from?: string;
  date_to?: string;
  cost_center_id?: number;
  document_type_id?: number;
  search?: string;
  order_by?: string;
}

export interface TransactionListResponse {
  items: Transaction[];
  total: number;
  skip: number;
  limit: number;
}

export interface TransactionSummary {
  total_count: number;
  by_cost_center: Array<{
    cost_center_id: number;
    count: number;
  }>;
}
