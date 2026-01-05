/**
 * Cost Centers API Client
 * Maliyet merkezleri için API istekleri
 */
import { BaseAPI } from '../../../../shared/api/base.api';
import { CostCenter, CostCenterCreateRequest, CostCenterListParams } from '../types/cost-center.types';

class CostCentersAPI extends BaseAPI {
  constructor() {
    super('/api/v2/partners/cost-centers');
  }

  /**
   * Maliyet merkezlerini listele
   */
  async getList(params?: CostCenterListParams): Promise<CostCenter[]> {
    const response = await this.client.get<CostCenter[]>('/', { params });
    return response.data;
  }

  /**
   * Tüm aktif maliyet merkezlerini getir
   */
  async getAllActive(): Promise<CostCenter[]> {
    const response = await this.client.get<CostCenter[]>('/active');
    return response.data;
  }

  /**
   * Tek maliyet merkezi getir
   */
  async getById(id: number): Promise<CostCenter> {
    const response = await this.client.get<CostCenter>(`/${id}`);
    return response.data;
  }

  /**
   * Koda göre maliyet merkezi getir
   */
  async getByCode(code: string): Promise<CostCenter> {
    const response = await this.client.get<CostCenter>(`/code/${code}`);
    return response.data;
  }

  /**
   * Yeni maliyet merkezi oluştur
   */
  async create(data: CostCenterCreateRequest): Promise<CostCenter> {
    const response = await this.client.post<CostCenter>('/', data);
    return response.data;
  }

  /**
   * Maliyet merkezi güncelle
   */
  async update(id: number, data: CostCenterCreateRequest): Promise<CostCenter> {
    const response = await this.client.put<CostCenter>(`/${id}`, data);
    return response.data;
  }

  /**
   * Maliyet merkezi sil (soft delete)
   */
  async delete(id: number): Promise<void> {
    await this.client.delete(`/${id}`);
  }
}

export const costCentersAPI = new CostCentersAPI();
