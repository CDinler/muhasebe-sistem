import apiClient from './api';

export interface Account {
  id: number;
  code: string;
  name: string;
  account_type: 'asset' | 'liability' | 'revenue' | 'expense';
  is_active: boolean;
}

export interface DocumentType {
  id: number;
  code: string;
  name: string;
  category: string;
  is_active: boolean;
  sort_order: number;
}

export interface DocumentSubtype {
  id: number;
  code: string;
  name: string;
  category: string;
  parent_code: string | null;
  is_active: boolean;
  sort_order: number;
}

export interface Contact {
  id?: number;
  code?: string | null;
  name: string;
  tax_number?: string | null;
  tax_office?: string | null;
  contact_type?: string | null;
  is_active: boolean;
  
  // İletişim
  phone?: string | null;
  phone2?: string | null;
  email?: string | null;
  website?: string | null;
  address?: string | null;
  city?: string | null;
  district?: string | null;
  postal_code?: string | null;
  country?: string | null;
  
  // Fatura Adresi
  invoice_address?: string | null;
  invoice_city?: string | null;
  invoice_district?: string | null;
  
  // Yetkili Kişi
  contact_person?: string | null;
  contact_person_phone?: string | null;
  contact_person_email?: string | null;
  contact_person_title?: string | null;
  
  // İş Bilgileri
  sector?: string | null;
  region?: string | null;
  customer_group?: string | null;
  
  // Finansal
  risk_limit?: number | null;
  payment_term_days?: number | null;
  payment_method?: string | null;
  discount_rate?: number | null;
  
  // Banka
  bank_name?: string | null;
  bank_branch?: string | null;
  bank_account_no?: string | null;
  iban?: string | null;
  swift?: string | null;
  
  // Bakiye
  current_balance?: number | null;
  
  // Notlar
  notes?: string | null;
  private_notes?: string | null;
  
  // Tarihler
  first_transaction_date?: string | null;
  last_transaction_date?: string | null;
}

export interface CostCenter {
  id?: number;
  code: string;
  name: string;
  is_active: boolean;
}

export interface TransactionLine {
  id?: number;
  account_id: number;
  contact_id?: number | null;
  description?: string;
  debit?: string | null;
  credit?: string | null;
  quantity?: string | null;
  unit?: string | null;
}

export interface Transaction {
  id?: number;
  transaction_number: string;
  transaction_date: string;
  accounting_period: string;
  cost_center_id?: number | null;
  description?: string;
  document_type?: string;
  document_subtype?: string | null;
  document_number?: string | null;
  related_invoice_number?: string | null;
  lines: TransactionLine[];
}

export const accountService = {
  getAll: (params?: { limit?: number; offset?: number }) => 
    apiClient.get<Account[]>('/accounts', { params: { limit: 10000, ...params } }),
  getById: (id: number) => apiClient.get<Account>(`/accounts/${id}`),
  getByCode: (code: string) => apiClient.get<Account>(`/accounts/code/${code}`),
  create: (data: Omit<Account, 'id'>) => apiClient.post<Account>('/accounts', data),
  update: (id: number, data: Omit<Account, 'id'>) => apiClient.put<Account>(`/accounts/${id}`, data),
  delete: (id: number) => apiClient.delete(`/accounts/${id}`),
};

export const transactionService = {
  getAll: (params?: { start_date?: string; end_date?: string; cost_center_id?: number; skip?: number; limit?: number; order_by?: string }) =>
    apiClient.get<Transaction[]>('/transactions', { params }),
  getById: (id: number) => apiClient.get<Transaction>(`/transactions/${id}`),
  getByNumber: (number: string) => apiClient.get<Transaction>(`/transactions/number/${number}`),
  create: (data: Transaction) => apiClient.post<Transaction>('/transactions', data),
  update: (id: number, data: Transaction) => apiClient.put<Transaction>(`/transactions/${id}`, data),
  delete: (id: number) => apiClient.delete(`/transactions/${id}`),
};

export const contactService = {
  getAll: (params?: { is_active?: boolean; contact_type?: string }) =>
    apiClient.get<Contact[]>('/contacts', { params }),
  getById: (id: number) => apiClient.get<Contact>(`/contacts/${id}`),
  getByTaxNumber: (taxNumber: string) => apiClient.get<Contact>(`/contacts/tax/${taxNumber}`),
  create: (data: Contact) => apiClient.post<Contact>('/contacts', data),
  update: (id: number, data: Contact) => apiClient.put<Contact>(`/contacts/${id}`, data),
  delete: (id: number) => apiClient.delete(`/contacts/${id}`),
};

export const costCenterService = {
  getAll: (params?: { is_active?: boolean }) =>
    apiClient.get<CostCenter[]>('/cost-centers', { params }),
  getById: (id: number) => apiClient.get<CostCenter>(`/cost-centers/${id}`),
  getByCode: (code: string) => apiClient.get<CostCenter>(`/cost-centers/code/${code}`),
  create: (data: CostCenter) => apiClient.post<CostCenter>('/cost-centers', data),
  update: (id: number, data: CostCenter) => apiClient.put<CostCenter>(`/cost-centers/${id}`, data),
  delete: (id: number) => apiClient.delete(`/cost-centers/${id}`),
};

export const documentTypeService = {
  getAll: (params?: { is_active?: boolean; category?: string }) =>
    apiClient.get<DocumentType[]>('/document-types', { params }),
  getById: (id: number) => apiClient.get<DocumentType>(`/document-types/${id}`),
};

export const documentSubtypeService = {
  getAll: (params?: { is_active?: boolean; parent_code?: string }) =>
    apiClient.get<DocumentSubtype[]>('/document-subtypes', { params }),
  getById: (id: number) => apiClient.get<DocumentSubtype>(`/document-subtypes/${id}`),
  getByParentCode: (parentCode: string) => 
    apiClient.get<DocumentSubtype[]>('/document-subtypes', { params: { parent_code: parentCode } }),
};
