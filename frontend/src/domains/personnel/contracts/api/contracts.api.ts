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
  }): Promise<PersonnelContractList> {
    const response = await this.client.get<PersonnelContractList>('/list', { params });
    return response.data;
  }

  async getById(id: number): Promise<PersonnelContract> {
    const response = await this.client.get<PersonnelContract>(`/${id}`);
    return response.data;
  }

  async getActiveByPersonnel(personnelId: number): Promise<PersonnelContract> {
    const response = await this.client.get<PersonnelContract>(`/personnel/${personnelId}/active`);
    return response.data;
  }

  async create(data: PersonnelContractCreate): Promise<PersonnelContract> {
    const response = await this.client.post<PersonnelContract>('/', data);
    return response.data;
  }

  async update(id: number, data: PersonnelContractUpdate): Promise<PersonnelContract> {
    const response = await this.client.put<PersonnelContract>(`/${id}`, data);
    return response.data;
  }

  async delete(id: number): Promise<void> {
    await this.client.delete(`/${id}`);
  }

  async deactivate(id: number): Promise<void> {
    await this.client.post(`/${id}/deactivate`);
  }
}

export const contractsAPI = new ContractsAPI();
