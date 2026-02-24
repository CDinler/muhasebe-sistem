// Personnel Draft Contracts Types

export interface PersonnelDraftContract {
  id: number;
  personnel_id: number;
  tc_kimlik_no: string | null;
  ucret_nevi: 'aylik' | 'sabit aylik' | 'gunluk';
  net_ucret: number | null;
  fm_orani: number;
  tatil_orani: number;
  cost_center_id: number | null;
  calisma_takvimi: 'atipi' | 'btipi' | 'ctipi' | null;
  is_active: number;
  created_at: string;
  updated_at: string;
  created_by: number | null;
  updated_by: number | null;
}

export interface PersonnelDraftContractCreate {
  personnel_id: number;
  tc_kimlik_no?: string | null;
  ucret_nevi: 'aylik' | 'sabit aylik' | 'gunluk';
  net_ucret?: number | null;
  fm_orani?: number;
  tatil_orani?: number;
  cost_center_id?: number | null;
  calisma_takvimi?: 'atipi' | 'btipi' | 'ctipi' | null;
  is_active?: number;
  created_by?: number | null;
}

export interface PersonnelDraftContractUpdate {
  ucret_nevi?: 'aylik' | 'sabit aylik' | 'gunluk';
  net_ucret?: number | null;
  fm_orani?: number;
  tatil_orani?: number;
  cost_center_id?: number | null;
  calisma_takvimi?: 'atipi' | 'btipi' | 'ctipi' | null;
  is_active?: number;
  updated_by?: number | null;
}
