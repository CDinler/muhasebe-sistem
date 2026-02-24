/**
 * Account API Client
 * Hesap planı için API istekleri
 */
import { CRUDService } from '../../../../shared/api/base.api';
import { Account, AccountCreate, AccountUpdate, AccountFilters } from '../types/account.types';

class AccountAPI extends CRUDService<Account, AccountCreate, AccountUpdate> {
  constructor() {
    super('/api/v2/accounts');
  }

  /**
   * Hesapları listele
   */
  async getList(params?: AccountFilters): Promise<Account[]> {
    const response = await this.client.get<{ items: Account[]; total: number }>(this.endpoint, { params });
    return response.data.items || [];
  }

  /**
   * Tek hesap getir
   */
  async getById(id: number): Promise<Account> {
    const response = await this.client.get<Account>(`${this.endpoint}/${id}`);
    return response.data;
  }

  /**
   * Hesap kodu ile getir
   */
  async getByCode(code: string): Promise<Account> {
    const response = await this.client.get<Account>(`${this.endpoint}/by-code/${code}`);
    return response.data;
  }

  /**
   * Yeni hesap oluştur
   */
  async create(data: AccountCreate): Promise<Account> {
    const response = await this.client.post<Account>(this.endpoint, data);
    return response.data;
  }

  /**
   * Hesap güncelle
   */
  async update(id: number, data: AccountUpdate): Promise<Account> {
    const response = await this.client.put<Account>(`${this.endpoint}/${id}`, data);
    return response.data;
  }

  /**
   * Hesap sil (soft delete)
   */
  async delete(id: number): Promise<void> {
    await this.client.delete(`${this.endpoint}/${id}`);
  }
}

export const accountAPI = new AccountAPI();
