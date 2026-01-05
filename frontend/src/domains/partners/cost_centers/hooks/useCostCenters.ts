/**
 * Cost Centers React Query Hooks
 * Maliyet merkezleri için React Query hooks
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { costCentersAPI } from '../api/cost-centers.api';
import { CostCenter, CostCenterCreateRequest, CostCenterListParams } from '../types/cost-center.types';
import { message } from 'antd';

// Query keys
const COST_CENTERS_QUERY_KEY = 'cost-centers';

/**
 * Maliyet merkezlerini listele
 */
export const useCostCentersList = (params?: CostCenterListParams) => {
  return useQuery({
    queryKey: [COST_CENTERS_QUERY_KEY, 'list', params],
    queryFn: () => costCentersAPI.getList(params),
  });
};

/**
 * Tüm aktif maliyet merkezlerini getir
 */
export const useActiveCostCenters = () => {
  return useQuery({
    queryKey: [COST_CENTERS_QUERY_KEY, 'active'],
    queryFn: () => costCentersAPI.getAllActive(),
  });
};

/**
 * Tek maliyet merkezi getir
 */
export const useCostCenter = (id: number) => {
  return useQuery({
    queryKey: [COST_CENTERS_QUERY_KEY, 'detail', id],
    queryFn: () => costCentersAPI.getById(id),
    enabled: !!id,
  });
};

/**
 * Koda göre maliyet merkezi getir
 */
export const useCostCenterByCode = (code: string) => {
  return useQuery({
    queryKey: [COST_CENTERS_QUERY_KEY, 'code', code],
    queryFn: () => costCentersAPI.getByCode(code),
    enabled: !!code,
  });
};

/**
 * Yeni maliyet merkezi oluştur
 */
export const useCreateCostCenter = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CostCenterCreateRequest) => costCentersAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [COST_CENTERS_QUERY_KEY] });
      message.success('Maliyet merkezi başarıyla oluşturuldu');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Maliyet merkezi oluşturulurken hata oluştu');
    },
  });
};

/**
 * Maliyet merkezi güncelle
 */
export const useUpdateCostCenter = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: CostCenterCreateRequest }) =>
      costCentersAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [COST_CENTERS_QUERY_KEY] });
      message.success('Maliyet merkezi başarıyla güncellendi');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Maliyet merkezi güncellenirken hata oluştu');
    },
  });
};

/**
 * Maliyet merkezi sil
 */
export const useDeleteCostCenter = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => costCentersAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [COST_CENTERS_QUERY_KEY] });
      message.success('Maliyet merkezi başarıyla silindi');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Maliyet merkezi silinirken hata oluştu');
    },
  });
};
