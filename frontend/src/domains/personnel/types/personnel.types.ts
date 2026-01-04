/**
 * Personnel domain types
 */
export interface Personnel {
  id: number;
  tc_kimlik_no: string;
  ad: string;
  soyad: string;
  accounts_id?: number;
  iban?: string;
  created_at: string;
  updated_at: string;
  created_by?: number;
  updated_by?: number;
}

export interface PersonnelCreate {
  tc_kimlik_no: string;
  ad: string;
  soyad: string;
  accounts_id?: number;
  iban?: string;
  created_by?: number;
}

export interface PersonnelUpdate {
  tc_kimlik_no?: string;
  ad?: string;
  soyad?: string;
  accounts_id?: number;
  iban?: string;
  updated_by?: number;
}

export interface PersonnelList {
  items: Personnel[];
  total: number;
  page: number;
  page_size: number;
}
