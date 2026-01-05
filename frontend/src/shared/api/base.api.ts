/**
 * Generic CRUD API service (P1 - Code duplication reduction)
 */
import apiClient from './client';

export class CRUDService<T, TCreate, TUpdate = TCreate> {
  protected client = apiClient;
  protected baseURL: string;

  constructor(protected endpoint: string) {
    this.baseURL = endpoint;
  }

  async getAll(): Promise<T[]> {
    const response = await apiClient.get(this.endpoint);
    return response.data.items || response.data;
  }

  async getById(id: number | string): Promise<T> {
    const response = await apiClient.get(`${this.endpoint}/${id}`);
    return response.data;
  }

  async create(data: TCreate): Promise<T> {
    const response = await apiClient.post(this.endpoint, data);
    return response.data;
  }

  async update(id: number | string, data: TUpdate): Promise<T> {
    const response = await apiClient.put(`${this.endpoint}/${id}`, data);
    return response.data;
  }

  async delete(id: number | string): Promise<void> {
    await apiClient.delete(`${this.endpoint}/${id}`);
  }

  async search(params: Record<string, any>): Promise<T[]> {
    const response = await apiClient.get(this.endpoint, { params });
    return response.data.items || response.data;
  }
}
