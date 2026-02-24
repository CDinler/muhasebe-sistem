/**
 * Personnel Contracts Types
 */

export interface PersonnelContract {
  id: number;
  personnel_id: number;
  tc_kimlik_no?: string;
  bolum?: string;
  monthly_personnel_records_id?: number;
  
  // Tarih aralığı
  ise_giris_tarihi: string;
  isten_cikis_tarihi?: string;
  is_active?: number;
  
  // Ücret bilgileri
  ucret_nevi: string;
  kanun_tipi?: string;
  calisma_takvimi?: string;
  net_brut?: string;
  ucret?: number;
  maas2_tutar?: number;
  maas_hesabi?: string;
  iban?: string;
  
  // Oranlar
  fm_orani?: number;
  tatil_orani?: number;
  
  // Taşeron
  taseron?: number;
  taseron_id?: number;
  
  // Departman
  departman?: string;
  cost_center_id?: number;
  
  // İlişkili veriler
  personnel_ad?: string;
  personnel_soyad?: string;
  cost_center_name?: string;
  taseron_name?: string;
  
  created_at?: string;
  updated_at?: string;
  created_by?: number;
  updated_by?: number;
}

export interface PersonnelContractCreate {
  personnel_id: number;
  tc_kimlik_no: string;
  bolum?: string;
  monthly_personnel_records_id?: number;
  ise_giris_tarihi: string;
  isten_cikis_tarihi?: string;
  is_active?: number;
  ucret_nevi: string;
  kanun_tipi?: string;
  calisma_takvimi?: string;
  net_brut?: string;
  ucret?: number;
  maas2_tutar?: number;
  maas_hesabi?: string;
  iban?: string;
  fm_orani?: number;
  tatil_orani?: number;
  taseron?: number;
  taseron_id?: number;
  departman?: string;
  cost_center_id?: number;
}

export interface PersonnelContractUpdate {
  personnel_id?: number;
  tc_kimlik_no?: string;
  bolum?: string;
  monthly_personnel_records_id?: number;
  ise_giris_tarihi?: string;
  isten_cikis_tarihi?: string;
  is_active?: number;
  ucret_nevi?: string;
  kanun_tipi?: string;
  calisma_takvimi?: string;
  net_brut?: string;
  ucret?: number;
  maas2_tutar?: number;
  maas_hesabi?: string;
  iban?: string;
  fm_orani?: number;
  tatil_orani?: number;
  taseron?: number;
  taseron_id?: number;
  departman?: string;
  cost_center_id?: number;
}

export interface PersonnelContractList {
  items: PersonnelContract[];
  total: number;
  page: number;
  page_size: number;
}
