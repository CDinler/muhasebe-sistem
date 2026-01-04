/**
 * Transaction API Service
 * 
 * V2 API endpoints for transactions (muhasebe fişleri)
 */
import { CRUDService } from '@/shared/api/base.api';
import type {
  Transaction,
  TransactionCreate,
  TransactionFilters,
  TransactionListResponse,
  TransactionSummary
} from '../types/transaction.types';

class TransactionAPI extends CRUDService<Transaction, TransactionCreate> {
  constructor() {
    super('/api/v2/accounting/transactions');
  }

  /**
   * Fiş özet istatistikleri
   */
  async getSummary(params?: {
    date_from?: string;
    date_to?: string;
  }): Promise<TransactionSummary> {
    const response = await this.client.get<TransactionSummary>(`${this.baseURL}/summary`, {
      params
    });
    return response.data;
  }

  /**
   * Fişleri filtrele ve listele
   */
  async getFiltered(filters: TransactionFilters): Promise<TransactionListResponse> {
    const response = await this.client.get<TransactionListResponse>(this.baseURL, {
      params: filters
    });
    return response.data;
  }

  /**
   * Fiş numarasına göre getir
   */
  async getByNumber(transactionNumber: string): Promise<Transaction> {
    const response = await this.client.get<Transaction>(
      `${this.baseURL}/by-number/${transactionNumber}`
    );
    return response.data;
  }

  /**
   * Yeni fiş oluştur
   */
  async createTransaction(data: TransactionCreate): Promise<Transaction> {
    const response = await this.client.post<Transaction>(this.baseURL, data);
    return response.data;
  }

  /**
   * Fiş güncelle
   */
  async updateTransaction(id: number, data: TransactionCreate): Promise<Transaction> {
    const response = await this.client.put<Transaction>(`${this.baseURL}/${id}`, data);
    return response.data;
  }

  /**
   * Fiş sil
   */
  async deleteTransaction(id: number): Promise<void> {
    await this.client.delete(`${this.baseURL}/${id}`);
  }
}

export const transactionAPI = new TransactionAPI();
