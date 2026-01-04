/**
 * E-Invoice API Service
 * 
 * V2 API kullanır (yeni DDD architecture)
 */
import axios from 'axios';
import { CRUDService } from '@/shared/api/crud-service';
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
  async uploadXML(formData: FormData): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}/v1/einvoices/upload`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    );
    return response.data;
  }

  async uploadPDF(formData: FormData): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}/v1/einvoices/pdf/upload`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    );
    return response.data;
  }

  async previewXML(formData: FormData): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}/v1/einvoices/preview`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
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
