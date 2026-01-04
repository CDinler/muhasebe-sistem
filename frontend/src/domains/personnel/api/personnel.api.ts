/**
 * Personnel API service
 */
import { CRUDService } from '@/shared/api/base.api';
import apiClient from '@/shared/api/client';
import {
  Personnel,
  PersonnelCreate,
  PersonnelUpdate,
  PersonnelList,
} from '../types/personnel.types';

class PersonnelAPI extends CRUDService<Personnel, PersonnelCreate, PersonnelUpdate> {
  constructor() {
    super('/api/v2/personnel');
  }

  async getAll(params?: { skip?: number; limit?: number; search?: string }): Promise<PersonnelList> {
    const response = await apiClient.get(this.endpoint, { params });
    return response.data;
  }

  async search(term: string): Promise<Personnel[]> {
    const response = await apiClient.get(this.endpoint, {
      params: { search: term },
    });
    return response.data.items;
  }
}

export const personnelAPI = new PersonnelAPI();
