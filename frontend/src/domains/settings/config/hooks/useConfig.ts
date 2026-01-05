/**
 * Config React Query Hooks
 * Sistem ayarları için React Query hooks
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { configAPI } from '../api/config.api';
import {
  SystemConfigCreate,
  SystemConfigUpdate,
  TaxBracketCreate,
  TaxBracketUpdate
} from '../types/config.types';
import { message } from 'antd';

// Query keys
const CONFIG_QUERY_KEY = 'config';
const TAX_BRACKETS_QUERY_KEY = 'tax-brackets';

// System Configs
export const useConfigs = (category?: string) => {
  return useQuery({
    queryKey: [CONFIG_QUERY_KEY, 'list', category],
    queryFn: () => configAPI.getConfigs(category),
  });
};

export const useConfig = (key: string) => {
  return useQuery({
    queryKey: [CONFIG_QUERY_KEY, 'detail', key],
    queryFn: () => configAPI.getConfig(key),
    enabled: !!key,
  });
};

export const useCreateConfig = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SystemConfigCreate) => configAPI.createConfig(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CONFIG_QUERY_KEY] });
      message.success('Ayar başarıyla oluşturuldu');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Ayar oluşturulurken hata oluştu');
    },
  });
};

export const useUpdateConfig = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ key, data }: { key: string; data: SystemConfigUpdate }) =>
      configAPI.updateConfig(key, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CONFIG_QUERY_KEY] });
      message.success('Ayar başarıyla güncellendi');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Ayar güncellenirken hata oluştu');
    },
  });
};

export const useDeleteConfig = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => configAPI.deleteConfig(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CONFIG_QUERY_KEY] });
      message.success('Ayar başarıyla silindi');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Ayar silinirken hata oluştu');
    },
  });
};

// Tax Brackets
export const useTaxBrackets = (year?: number) => {
  return useQuery({
    queryKey: [TAX_BRACKETS_QUERY_KEY, year],
    queryFn: () => configAPI.getTaxBrackets(year),
  });
};

export const useCreateTaxBracket = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TaxBracketCreate) => configAPI.createTaxBracket(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [TAX_BRACKETS_QUERY_KEY] });
      message.success('Vergi dilimi başarıyla oluşturuldu');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Vergi dilimi oluşturulurken hata oluştu');
    },
  });
};

export const useUpdateTaxBracket = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: TaxBracketUpdate }) =>
      configAPI.updateTaxBracket(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [TAX_BRACKETS_QUERY_KEY] });
      message.success('Vergi dilimi başarıyla güncellendi');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Vergi dilimi güncellenirken hata oluştu');
    },
  });
};

export const useDeleteTaxBracket = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => configAPI.deleteTaxBracket(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [TAX_BRACKETS_QUERY_KEY] });
      message.success('Vergi dilimi başarıyla silindi');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Vergi dilimi silinirken hata oluştu');
    },
  });
};
