/**
 * E-Invoice API Service
 * 
 * V2 API kullanır (yeni DDD architecture)
 */
import axios from 'axios';
import { CRUDService } from '@/shared/api/base.api';
import type {
  EInvoice,
  EInvoiceSummary,
  EInvoiceFilters,
  EInvoiceCreate,
  EInvoiceUpdate
} from '../types/einvoice.types';

const API_BASE_URL = 'http://localhost:8000/api';

class EInvoiceAPI extends CRUDService<EInvoice, EInvoiceCreate, EInvoiceUpdate> {
  constructor() {
    super('/v2/invoicing/einvoices');
  }

  /**
   * Özet istatistikler
   */
  async getSummary(params?: {
    date_from?: string;
    date_to?: string;
  }): Promise<EInvoiceSummary> {
    const response = await axios.get(
      `${API_BASE_URL}${this.endpoint}/summary`,
      { params }
    );
    return response.data;
  }

  /**
   * Filtrelenmiş liste
   */
  async getFiltered(filters: EInvoiceFilters): Promise<EInvoice[]> {
    const response = await axios.get(
      `${API_BASE_URL}${this.endpoint}`,
      { params: filters }
    );
    return response.data;
  }

  /**
   * V1 API'ye fallback için (XML upload, PDF matching vb.)
   * Legacy endpoint'ler henüz V2'ye taşınmadı
   */
  async getEInvoice(id: number): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/v1/einvoices/${id}`);
    return response.data;
  }

  async previewImport(id: number, data?: any): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}/v1/einvoices/${id}/preview-import`,
      data
    );
    return response.data;
  }

  async importToAccounting(id: number, data: any): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}/v1/einvoices/${id}/import`,
      data
    );
    return response.data;
  }

  async uploadFile(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await axios.post(
      `${API_BASE_URL}/v1/einvoices/upload-file`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    );
    return response.data;
  }

  async uploadXML(files: File[], direction: string): Promise<any> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    formData.append('direction', direction);
    
    const response = await axios.post(
      `${API_BASE_URL}/v1/einvoices/upload-xml`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    );
    return response.data;
  }

  async uploadPDF(file: File, direction: string): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('direction', direction);
    
    const response = await axios.post(
      `${API_BASE_URL}/v1/einvoices/pdf/upload`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    );
    return response.data;
  }

  async getPDF(id: number): Promise<Blob> {
    const response = await axios.get(
      `${API_BASE_URL}/v1/einvoices/${id}/pdf`,
      { responseType: 'blob' }
    );
    return response.data;
  }

  async previewXML(files: File[]): Promise<any> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    
    const response = await axios.post(
      `${API_BASE_URL}/v1/einvoices/preview-xml`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    );
    return response.data;
  }

  async updateEInvoice(id: number, data: any): Promise<any> {
    const response = await axios.patch(
      `${API_BASE_URL}/v1/einvoices/${id}`,
      data
    );
    return response.data;
  }

  async createTransaction(invoiceId: number, data: any): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}/v1/einvoices/${invoiceId}/transaction`,
      data
    );
    return response.data;
  }

  async getTransactionPreview(invoiceId: number, data: any): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}/v1/einvoices/${invoiceId}/transaction/preview`,
      data
    );
    return response.data;
  }
}

export const einvoiceAPI = new EInvoiceAPI();
