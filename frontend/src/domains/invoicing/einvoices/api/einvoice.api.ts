/**
 * E-Invoice API Service
 * 
 * V2 API kullanır (yeni DDD architecture)
 */
import apiClient from '@/shared/api/client';
import { CRUDService } from '@/shared/api/base.api';
import type {
  EInvoice,
  EInvoiceSummary,
  EInvoiceFilters,
  EInvoiceCreate,
  EInvoiceUpdate
} from '../types/einvoice.types';

class EInvoiceAPI extends CRUDService<EInvoice, EInvoiceCreate, EInvoiceUpdate> {
  constructor() {
    super('/api/v2/invoicing/einvoices');
  }

  /**
   * Özet istatistikler
   */
  async getSummary(params?: {
    date_from?: string;
    date_to?: string;
  }): Promise<EInvoiceSummary> {
    // Remove undefined/invalid params to avoid "Invalid Date" in query string
    const cleanParams = params ? Object.fromEntries(
      Object.entries(params).filter(([_, v]) => v !== undefined && v !== 'Invalid Date')
    ) : {};
    
    const response = await apiClient.get<EInvoiceSummary>(
      `${this.endpoint}/summary`,
      { params: cleanParams }
    );
    return response.data;
  }

  /**
   * Filtrelenmiş liste
   */
  async getFiltered(filters: EInvoiceFilters): Promise<EInvoice[]> {
    // Remove undefined/invalid filters to avoid "Invalid Date" in query string
    const cleanFilters = Object.fromEntries(
      Object.entries(filters).filter(([_, v]) => v !== undefined && v !== 'Invalid Date')
    );
    
    const response = await apiClient.get<EInvoice[]>(
      this.endpoint,
      { params: cleanFilters }
    );
    return response.data;
  }

  /**
   * V2 API endpoints (migrated from V1)
   */
  async getEInvoice(id: number): Promise<any> {
    const response = await apiClient.get(`${this.endpoint}/${id}`);
    return response.data;
  }

  async previewImport(id: number, data?: any): Promise<any> {
    const response = await apiClient.post(
      `${this.endpoint}/${id}/preview-import`,
      data
    );
    return response.data;
  }

  /**
   * V2 API endpoints
   */
  async importToAccounting(id: number, data: any): Promise<any> {
    const response = await apiClient.post(
      `${this.endpoint}/${id}/import`,
      data
    );
    return response.data;
  }

  async uploadFile(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post(
      `${this.endpoint}/upload-file`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    );
    return response.data;
  }

  async uploadXML(formData: FormData): Promise<any> {
    const response = await apiClient.post(
      `${this.endpoint}/upload-xml`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    );
    return response.data;
  }

  async uploadPDF(formData: FormData): Promise<any> {
    const response = await apiClient.post(
      `${this.endpoint}/pdf/upload`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    );
    return response.data;
  }

  async getPDF(id: number): Promise<Blob> {
    const response = await apiClient.get(
      `${this.endpoint}/pdf/${id}`,
      { responseType: 'blob' }
    );
    return response.data;
  }

  async previewXML(formData: FormData): Promise<any> {
    const response = await apiClient.post(
      `${this.endpoint}/preview-xml`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    );
    return response.data;
  }

  async updateEInvoice(id: number, data: any): Promise<any> {
    const response = await apiClient.patch(
      `${this.endpoint}/${id}`,
      data
    );
    return response.data;
  }

  async createTransaction(invoiceId: number, data: any): Promise<any> {
    const response = await apiClient.post(
      `${this.endpoint}/${invoiceId}/transaction`,
      data
    );
    return response.data;
  }

  async getTransactionPreview(invoiceId: number, data: any): Promise<any> {
    const response = await apiClient.post(
      `${this.endpoint}/${invoiceId}/transaction/preview`,
      data
    );
    return response.data;
  }
}

export const einvoiceAPI = new EInvoiceAPI();
