/**
 * Contact Types
 * Cari hesap TypeScript interfaces
 */

export interface Contact {
  id: number;
  code?: string;
  name: string;
  tax_number?: string;
  tax_office?: string;
  contact_type?: 'customer' | 'supplier' | 'both';
  is_active: boolean;
  
  // İletişim
  phone?: string;
  phone2?: string;
  email?: string;
  website?: string;
  address?: string;
  city?: string;
  district?: string;
  postal_code?: string;
  country?: string;
  
  // Fatura Adresi
  invoice_address?: string;
  invoice_city?: string;
  invoice_district?: string;
  
  // Yetkili Kişi
  contact_person?: string;
  contact_person_phone?: string;
  contact_person_email?: string;
  contact_person_title?: string;
  
  // İş Bilgileri
  sector?: string;
  region?: string;
  customer_group?: string;
  
  // Finansal
  risk_limit?: number;
  payment_term_days?: number;
  currency?: string;
  
  // Banka
  iban?: string;
  bank_name?: string;
  bank_branch?: string;
  
  // Notlar
  notes?: string;
}

export interface ContactCreateRequest {
  name: string;
  code?: string;
  tax_number?: string;
  tax_office?: string;
  contact_type?: 'customer' | 'supplier' | 'both';
  is_active?: boolean;
  
  phone?: string;
  phone2?: string;
  email?: string;
  website?: string;
  address?: string;
  city?: string;
  district?: string;
  postal_code?: string;
  country?: string;
  
  invoice_address?: string;
  invoice_city?: string;
  invoice_district?: string;
  
  contact_person?: string;
  contact_person_phone?: string;
  contact_person_email?: string;
  contact_person_title?: string;
  
  sector?: string;
  region?: string;
  customer_group?: string;
  
  risk_limit?: number;
  payment_term_days?: number;
  currency?: string;
  
  iban?: string;
  bank_name?: string;
  bank_branch?: string;
  
  notes?: string;
}

export interface ContactListParams {
  skip?: number;
  limit?: number;
  is_active?: boolean;
  contact_type?: 'customer' | 'supplier' | 'both';
}
