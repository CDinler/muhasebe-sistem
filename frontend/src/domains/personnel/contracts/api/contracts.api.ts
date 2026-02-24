/**
 * Personnel Contracts API Client
 */
import { CRUDService } from '../../../../shared/api/base.api';
import {
  PersonnelContract,
  PersonnelContractCreate,
  PersonnelContractUpdate,
  PersonnelContractList
} from '../types/contracts.types';

class ContractsAPI extends CRUDService<PersonnelContract, PersonnelContractCreate, PersonnelContractUpdate> {
  constructor() {
    super('/api/v2/personnel/contracts');
  }

  async getList(params?: {
    personnel_id?: number;
    cost_center_id?: number;
    is_active?: boolean;
    donem?: string;
    page?: number;
    page_size?: number;
    skip?: number;
    limit?: number;
    order_by?: string;
    order_direction?: string;
  }): Promise<PersonnelContractList> {
    const response = await this.client.get<PersonnelContractList>(`${this.baseURL}/list`, { params });
    return response.data;
  }

  async getById(id: number): Promise<PersonnelContract> {
    const response = await this.client.get<PersonnelContract>(`${this.baseURL}/${id}`);
    return response.data;
  }

  async getActiveByPersonnel(personnelId: number): Promise<PersonnelContract> {
    const response = await this.client.get<PersonnelContract>(`${this.baseURL}/personnel/id/${personnelId}/active`);
    return response.data;
  }

  async create(data: PersonnelContractCreate): Promise<PersonnelContract> {
    const response = await this.client.post<PersonnelContract>(`${this.baseURL}`, data);
    return response.data;
  }

  async update(id: number, data: PersonnelContractUpdate): Promise<PersonnelContract> {
    const response = await this.client.put<PersonnelContract>(`${this.baseURL}/${id}`, data);
    return response.data;
  }

  async delete(id: number): Promise<void> {
    await this.client.delete(`${this.baseURL}/${id}`);
  }

  async deactivate(id: number): Promise<void> {
    await this.client.post(`${this.baseURL}/${id}/deactivate`);
  }
}

export const contractsAPI = new ContractsAPI();
