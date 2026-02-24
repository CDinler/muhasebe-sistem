export interface MonthlyPersonnelRecord {
  id: number;
  personnel_id: number;
  donem: string;
  yil: number;
  ay: number;
  tc_kimlik_no: string;
  adi: string | null;
  soyadi: string | null;
  cinsiyeti: string | null;
  unvan: string | null;
  isyeri: string | null;
  bolum: string | null;
  ssk_no: string | null;
  baba_adi: string | null;
  anne_adi: string | null;
  dogum_yeri: string | null;
  dogum_tarihi: string | null;
  nufus_cuzdani_no: string | null;
  nufusa_kayitli_oldugu_il: string | null;
  nufusa_kayitli_oldugu_ilce: string | null;
  nufusa_kayitli_oldugu_mah: string | null;
  cilt_no: string | null;
  sira_no: string | null;
  kutuk_no: string | null;
  ise_giris_tarihi: string;
  isten_cikis_tarihi: string | null;
  isten_ayrilis_kodu: string | null;
  isten_ayrilis_nedeni: string | null;
  adres: string | null;
  telefon: string | null;
  banka_sube_adi: string | null;
  hesap_no: string | null;
  ucret: number | null;
  net_brut: string | null;
  kan_grubu: string | null;
  meslek_kodu: string | null;
  meslek_adi: string | null;
  contract_id: number | null;
}

export interface MonthlyRecordsListParams {
  donem?: string;
  personnel_id?: number;
  skip?: number;
  limit?: number;
}

export interface MonthlyRecordsListResponse {
  items: MonthlyPersonnelRecord[];
  total: number;
}

export interface UploadSicilParams {
  donem: string;
  file: File;
}

export interface UploadSicilResponse {
  message: string;
  donem: string;
  total_records: number;
  created_personnel: number;
  updated_personnel: number;
  created_contracts: number;
  updated_contracts: number;
  created_records: number;
  updated_records: number;
  errors: Array<{
    row: number;
    tc_kimlik_no: string;
    error: string;
  }>;
}
