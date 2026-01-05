/**
 * Personnel Contracts React Query Hooks
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { contractsAPI } from '../api/contracts.api';
import { PersonnelContractCreate, PersonnelContractUpdate } from '../types/contracts.types';
import { message } from 'antd';

const CONTRACTS_QUERY_KEY = 'personnel-contracts';

export const useContractsList = (params?: {
  personnel_id?: number;
  cost_center_id?: number;
  is_active?: boolean;
}) => {
  return useQuery({
    queryKey: [CONTRACTS_QUERY_KEY, 'list', params],
    queryFn: () => contractsAPI.getList(params),
  });
};

export const useContract = (id: number) => {
  return useQuery({
    queryKey: [CONTRACTS_QUERY_KEY, 'detail', id],
    queryFn: () => contractsAPI.getById(id),
    enabled: !!id,
  });
};

export const useActiveContract = (personnelId: number) => {
  return useQuery({
    queryKey: [CONTRACTS_QUERY_KEY, 'active', personnelId],
    queryFn: () => contractsAPI.getActiveByPersonnel(personnelId),
    enabled: !!personnelId,
  });
};

export const useCreateContract = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: PersonnelContractCreate) => contractsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CONTRACTS_QUERY_KEY] });
      message.success('Sözleşme başarıyla oluşturuldu');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Sözleşme oluşturulurken hata oluştu');
    },
  });
};

export const useUpdateContract = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: PersonnelContractUpdate }) =>
      contractsAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CONTRACTS_QUERY_KEY] });
      message.success('Sözleşme başarıyla güncellendi');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Sözleşme güncellenirken hata oluştu');
    },
  });
};

export const useDeleteContract = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => contractsAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CONTRACTS_QUERY_KEY] });
      message.success('Sözleşme başarıyla silindi');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Sözleşme silinirken hata oluştu');
    },
  });
};

export const useDeactivateContract = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => contractsAPI.deactivate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CONTRACTS_QUERY_KEY] });
      message.success('Sözleşme başarıyla pasif yapıldı');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Sözleşme pasif yapılırken hata oluştu');
    },
  });
};
