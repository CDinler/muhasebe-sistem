/**
 * Payroll Types
 */

export interface PayrollCalculation {
  id: number;
  personnel_id: number;
  adi_soyadi: string;
  yil: number;
  ay: number;
  brut_ucret: number;
  net_ucret: number;
}

export interface PayrollCalculateRequest {
  yil: number;
  ay: number;
  donem: string; // YYYY-MM format
}
