// Personnel Draft Contracts API Service
import { apiClient } from '../../../../shared/api/client';
import { PersonnelDraftContract, PersonnelDraftContractCreate, PersonnelDraftContractUpdate } from '../types/draft-contracts.types';

const API_PATH = '/api/v2/personnel/draft-contracts';

export const draftContractsApi = {
  // List draft contracts
  getAll: (params?: { 
    personnel_id?: number; 
    ucret_nevi?: string;
    is_active?: boolean;
    skip?: number; 
    limit?: number 
  }) => apiClient.get<PersonnelDraftContract[]>(API_PATH, { params }),

  // Get single draft contract
  getById: (id: number) => 
    apiClient.get<PersonnelDraftContract>(`${API_PATH}/${id}`),

  // Create draft contract
  create: (data: PersonnelDraftContractCreate) => 
    apiClient.post<PersonnelDraftContract>(API_PATH, data),

  // Update draft contract
  update: (id: number, data: PersonnelDraftContractUpdate) => 
    apiClient.put<PersonnelDraftContract>(`${API_PATH}/${id}`, data),

  // Delete draft contract
  delete: (id: number) => 
    apiClient.delete(`${API_PATH}/${id}`),

  // Get draft contracts by personnel
  getByPersonnel: (personnelId: number) => 
    apiClient.get<PersonnelDraftContract[]>(API_PATH, { params: { personnel_id: personnelId } })
};

