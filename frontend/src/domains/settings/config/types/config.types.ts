/**
 * Config Types
 * Sistem ayarları için TypeScript interfaces
 */

export interface SystemConfig {
  id: number;
  key: string;
  value: string;
  type: string;
  description?: string;
}

export interface SystemConfigCreate {
  config_key: string;
  config_value: string;
  config_type?: string;
  category?: string;
  description?: string;
}

export interface SystemConfigUpdate {
  config_value: string;
  description?: string;
}

export interface TaxBracket {
  id: number;
  year: number;
  min_amount: number;
  max_amount?: number;
  tax_rate: number;
}

export interface TaxBracketCreate {
  year: number;
  min_amount: number;
  max_amount?: number;
  tax_rate: number;
}

export interface TaxBracketUpdate {
  min_amount?: number;
  max_amount?: number;
  tax_rate?: number;
}

export interface ConfigsGrouped {
  [category: string]: SystemConfig[];
}
