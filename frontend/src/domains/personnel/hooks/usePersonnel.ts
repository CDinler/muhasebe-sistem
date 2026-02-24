/**
 * Personnel React Query hooks (P1 - State management)
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { personnelAPI } from '../api/personnel.api';
import { PersonnelCreate, PersonnelUpdate } from '../types/personnel.types';
import { message } from 'antd';

const PERSONNEL_QUERY_KEY = 'personnel';

export function usePersonnel(params?: { skip?: number; limit?: number; search?: string; year_filter?: number; month_filter?: number }) {
  return useQuery({
    queryKey: [PERSONNEL_QUERY_KEY, params],
    queryFn: () => personnelAPI.getAll(params),
    staleTime: 5 * 60 * 1000, // 5 minutes cache
  });
}

export function usePersonnelById(id: number) {
  return useQuery({
    queryKey: [PERSONNEL_QUERY_KEY, id],
    queryFn: () => personnelAPI.getById(id),
    enabled: !!id,
  });
}

export function useCreatePersonnel() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: PersonnelCreate) => personnelAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [PERSONNEL_QUERY_KEY] });
      message.success('Personel başarıyla oluşturuldu');
    },
    onError: (error: any) => {
      message.error(error.message || 'Personel oluşturulamadı');
    },
  });
}

export function useUpdatePersonnel() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: PersonnelUpdate }) =>
      personnelAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [PERSONNEL_QUERY_KEY] });
      message.success('Personel başarıyla güncellendi');
    },
    onError: (error: any) => {
      message.error(error.message || 'Personel güncellenemedi');
    },
  });
}

export function useDeletePersonnel() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => personnelAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [PERSONNEL_QUERY_KEY] });
      message.success('Personel başarıyla silindi');
    },
    onError: (error: any) => {
      message.error(error.message || 'Personel silinemedi');
    },
  });
}

export function useSearchPersonnel(term: string) {
  return useQuery({
    queryKey: [PERSONNEL_QUERY_KEY, 'search', term],
    queryFn: () => personnelAPI.search(term),
    enabled: term.length >= 2,
  });
}
