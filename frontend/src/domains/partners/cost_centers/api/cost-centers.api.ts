/**
 * Cost Centers API Client
 * Maliyet merkezleri için API istekleri
 */
import { CRUDService } from '../../../../shared/api/base.api';
import { CostCenter, CostCenterCreateRequest, CostCenterListParams } from '../types/cost-center.types';

class CostCentersAPI extends CRUDService<CostCenter, CostCenterCreateRequest, CostCenterCreateRequest> {
  constructor() {
    super('/api/v2/partners/cost-centers');
  }

  /**
   * Maliyet merkezlerini listele
   */
  async getList(params?: CostCenterListParams): Promise<{ items: CostCenter[]; total: number }> {
    const response = await this.client.get<{ items: CostCenter[]; total: number }>(this.endpoint, { params });
    return response.data;
  }

  /**
   * Tüm aktif maliyet merkezlerini getir
   */
  async getAllActive(): Promise<CostCenter[]> {
    const response = await this.client.get<CostCenter[]>(`${this.endpoint}/active`);
    return response.data;
  }

  /**
   * Tek maliyet merkezi getir
   */
  async getById(id: number): Promise<CostCenter> {
    const response = await this.client.get<CostCenter>(`${this.endpoint}/${id}`);
    return response.data;
  }

  /**
   * Koda göre maliyet merkezi getir
   */
  async getByCode(code: string): Promise<CostCenter> {
    const response = await this.client.get<CostCenter>(`${this.endpoint}/code/${code}`);
    return response.data;
  }

  /**
   * Yeni maliyet merkezi oluştur
   */
  async create(data: CostCenterCreateRequest): Promise<CostCenter> {
    const response = await this.client.post<CostCenter>(`${this.endpoint}/`, data);
    return response.data;
  }

  /**
   * Maliyet merkezi güncelle
   */
  async update(id: number, data: CostCenterCreateRequest): Promise<CostCenter> {
    const response = await this.client.put<CostCenter>(`${this.endpoint}/${id}`, data);
    return response.data;
  }

  /**
   * Maliyet merkezi sil (soft delete)
   */
  async delete(id: number): Promise<void> {
    await this.client.delete(`${this.endpoint}/${id}`);
  }
}

export const costCentersAPI = new CostCentersAPI();
