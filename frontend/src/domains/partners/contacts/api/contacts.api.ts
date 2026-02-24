/**
 * Contacts API Client
 * Cari hesaplar için API istekleri
 */
import { CRUDService } from '../../../../shared/api/base.api';
import { Contact, ContactCreateRequest, ContactListParams } from '../types/contact.types';

class ContactsAPI extends CRUDService<Contact, ContactCreateRequest, ContactCreateRequest> {
  constructor() {
    super('/api/v2/partners/contacts');
  }

  /**
   * Carileri listele
   */
  async getList(params?: ContactListParams): Promise<{ items: Contact[]; total: number }> {
    const response = await this.client.get<{ items: Contact[]; total: number }>(this.endpoint, { params });
    return response.data;
  }

  /**
   * Tek cari getir
   */
  async getById(id: number): Promise<Contact> {
    const response = await this.client.get<Contact>(`${this.endpoint}/${id}`);
    return response.data;
  }

  /**
   * Vergi numarasına göre cari getir
   */
  async getByTaxNumber(taxNumber: string): Promise<Contact> {
    const response = await this.client.get<Contact>(`${this.endpoint}/tax/${taxNumber}`);
    return response.data;
  }

  /**
   * Cari ara
   */
  async search(query: string, isActive: boolean = true): Promise<Contact[]> {
    const response = await this.client.get<Contact[]>(`${this.endpoint}/search`, {
      params: { q: query, is_active: isActive }
    });
    return response.data;
  }

  /**
   * Yeni cari oluştur
   */
  async create(data: ContactCreateRequest): Promise<Contact> {
    const response = await this.client.post<Contact>(this.endpoint, data);
    return response.data;
  }

  /**
   * Cari güncelle
   */
  async update(id: number, data: ContactCreateRequest): Promise<Contact> {
    const response = await this.client.put<Contact>(`${this.endpoint}/${id}`, data);
    return response.data;
  }

  /**
   * Cari sil (soft delete)
   */
  async delete(id: number): Promise<void> {
    await this.client.delete(`${this.endpoint}/${id}`);
  }
}

export const contactsAPI = new ContactsAPI();
