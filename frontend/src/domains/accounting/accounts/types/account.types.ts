/**
 * Account Types
 * Hesap planı TypeScript interfaces
 */

export interface Account {
  id: number;
  code: string;
  name: string;
  account_type: 'asset' | 'liability' | 'revenue' | 'expense';
  is_active: boolean;
  parent_id?: number | null;
  description?: string | null;
}

export interface AccountCreate {
  code: string;
  name: string;
  account_type: 'asset' | 'liability' | 'revenue' | 'expense';
  is_active?: boolean;
  parent_id?: number | null;
  description?: string | null;
}

export interface AccountUpdate {
  name?: string;
  account_type?: 'asset' | 'liability' | 'revenue' | 'expense';
  is_active?: boolean;
  parent_id?: number | null;
  description?: string | null;
}

export interface AccountFilters {
  skip?: number;
  limit?: number;
  is_active?: boolean;
  account_type?: string;
  search?: string;
}
