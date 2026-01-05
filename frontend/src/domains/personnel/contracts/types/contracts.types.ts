/**
 * Personnel Contracts Types
 */

export interface PersonnelContract {
  id: number;
  personnel_id: number;
  cost_center_id?: number;
  contact_id?: number;
  tc_kimlik_no?: string;
  bolum?: string;
  maas_hesabi?: string;
  taseron?: boolean;
  ucret_nevi?: string;
  calisma_takvimi?: string;
  departman?: string;
  sigorta_durumu?: string;
  ise_giris_tarihi?: string;
  isten_cikis_tarihi?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface PersonnelContractCreate {
  personnel_id: number;
  cost_center_id?: number;
  contact_id?: number;
  tc_kimlik_no?: string;
  bolum?: string;
  maas_hesabi?: string;
  taseron?: boolean;
  ucret_nevi?: string;
  calisma_takvimi?: string;
  departman?: string;
  sigorta_durumu?: string;
  ise_giris_tarihi?: string;
  isten_cikis_tarihi?: string;
  is_active?: boolean;
}

export interface PersonnelContractUpdate {
  cost_center_id?: number;
  contact_id?: number;
  tc_kimlik_no?: string;
  bolum?: string;
  maas_hesabi?: string;
  taseron?: boolean;
  ucret_nevi?: string;
  calisma_takvimi?: string;
  departman?: string;
  sigorta_durumu?: string;
  ise_giris_tarihi?: string;
  isten_cikis_tarihi?: string;
  is_active?: boolean;
}

export interface PersonnelContractList {
  contracts: PersonnelContract[];
  total: number;
}
