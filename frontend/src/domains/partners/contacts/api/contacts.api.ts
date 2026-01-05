/**
 * Contacts API Client
 * Cari hesaplar için API istekleri
 */
import { BaseAPI } from '../../../../shared/api/base.api';
import { Contact, ContactCreateRequest, ContactListParams } from '../types/contact.types';

class ContactsAPI extends BaseAPI {
  constructor() {
    super('/api/v2/partners/contacts');
  }

  /**
   * Carileri listele
   */
  async getList(params?: ContactListParams): Promise<Contact[]> {
    const response = await this.client.get<Contact[]>('/', { params });
    return response.data;
  }

  /**
   * Tek cari getir
   */
  async getById(id: number): Promise<Contact> {
    const response = await this.client.get<Contact>(`/${id}`);
    return response.data;
  }

  /**
   * Vergi numarasına göre cari getir
   */
  async getByTaxNumber(taxNumber: string): Promise<Contact> {
    const response = await this.client.get<Contact>(`/tax/${taxNumber}`);
    return response.data;
  }

  /**
   * Cari ara
   */
  async search(query: string, isActive: boolean = true): Promise<Contact[]> {
    const response = await this.client.get<Contact[]>('/search', {
      params: { q: query, is_active: isActive }
    });
    return response.data;
  }

  /**
   * Yeni cari oluştur
   */
  async create(data: ContactCreateRequest): Promise<Contact> {
    const response = await this.client.post<Contact>('/', data);
    return response.data;
  }

  /**
   * Cari güncelle
   */
  async update(id: number, data: ContactCreateRequest): Promise<Contact> {
    const response = await this.client.put<Contact>(`/${id}`, data);
    return response.data;
  }

  /**
   * Cari sil (soft delete)
   */
  async delete(id: number): Promise<void> {
    await this.client.delete(`/${id}`);
  }
}

export const contactsAPI = new ContactsAPI();
