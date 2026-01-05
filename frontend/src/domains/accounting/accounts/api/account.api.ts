/**
 * Account API Client
 * Hesap planı için API istekleri
 */
import { BaseAPI } from '../../../../shared/api/base.api';
import { Account, AccountCreate, AccountUpdate, AccountFilters } from '../types/account.types';

class AccountAPI extends BaseAPI {
  constructor() {
    super('/api/v2/accounting/accounts');
  }

  /**
   * Hesapları listele
   */
  async getList(params?: AccountFilters): Promise<Account[]> {
    const response = await this.client.get<Account[]>('/', { params });
    return response.data;
  }

  /**
   * Tek hesap getir
   */
  async getById(id: number): Promise<Account> {
    const response = await this.client.get<Account>(`/${id}`);
    return response.data;
  }

  /**
   * Hesap kodu ile getir
   */
  async getByCode(code: string): Promise<Account> {
    const response = await this.client.get<Account>(`/by-code/${code}`);
    return response.data;
  }

  /**
   * Yeni hesap oluştur
   */
  async create(data: AccountCreate): Promise<Account> {
    const response = await this.client.post<Account>('/', data);
    return response.data;
  }

  /**
   * Hesap güncelle
   */
  async update(id: number, data: AccountUpdate): Promise<Account> {
    const response = await this.client.put<Account>(`/${id}`, data);
    return response.data;
  }

  /**
   * Hesap sil (soft delete)
   */
  async delete(id: number): Promise<void> {
    await this.client.delete(`/${id}`);
  }
}

export const accountAPI = new AccountAPI();
