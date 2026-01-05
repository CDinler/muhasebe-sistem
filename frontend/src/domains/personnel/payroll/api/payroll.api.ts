/**
 * Payroll API Client
 */
import { BaseAPI } from '@/shared/api/base';
import apiClient from '@/shared/api/client';
import type { PayrollCalculation, PayrollCalculateRequest } from '../types/payroll.types';

class PayrollAPI extends BaseAPI {
  constructor() {
    super('/api/v2/personnel/payroll');
  }

  /**
   * Döneme göre bordro listesi
   */
  async getList(yil: number, ay: number): Promise<PayrollCalculation[]> {
    const response = await apiClient.get<PayrollCalculation[]>(`${this.endpoint}/list`, {
      params: { yil, ay }
    });
    return response.data;
  }

  /**
   * Bordro hesapla
   */
  async calculate(data: PayrollCalculateRequest): Promise<any> {
    const response = await apiClient.post(`${this.endpoint}/calculate`, data);
    return response.data;
  }
}

export const payrollAPI = new PayrollAPI();
export default payrollAPI;
