/**
 * Cost Center Types
 * Maliyet merkezi TypeScript interfaces
 */

export interface CostCenter {
  id: number;
  code: string;
  name: string;
  is_active: boolean;
  bolum_adi?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CostCenterCreateRequest {
  code: string;
  name: string;
  is_active?: boolean;
  bolum_adi?: string;
}

export interface CostCenterListParams {
  skip?: number;
  limit?: number;
  is_active?: boolean;
}
