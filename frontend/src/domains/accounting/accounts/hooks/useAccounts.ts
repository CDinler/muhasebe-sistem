/**
 * Accounts React Query Hooks
 * Hesap planı için React Query hooks
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { accountAPI } from '../api/account.api';
import { AccountCreate, AccountUpdate, AccountFilters } from '../types/account.types';
import { message } from 'antd';

// Query keys
const ACCOUNTS_QUERY_KEY = 'accounts';

/**
 * Hesapları listele
 */
export const useAccounts = (params?: AccountFilters) => {
  return useQuery({
    queryKey: [ACCOUNTS_QUERY_KEY, 'list', params],
    queryFn: () => accountAPI.getList(params),
  });
};

/**
 * Tek hesap getir
 */
export const useAccount = (id: number) => {
  return useQuery({
    queryKey: [ACCOUNTS_QUERY_KEY, 'detail', id],
    queryFn: () => accountAPI.getById(id),
    enabled: !!id,
  });
};

/**
 * Hesap kodu ile getir
 */
export const useAccountByCode = (code: string) => {
  return useQuery({
    queryKey: [ACCOUNTS_QUERY_KEY, 'code', code],
    queryFn: () => accountAPI.getByCode(code),
    enabled: !!code,
  });
};

/**
 * Yeni hesap oluştur
 */
export const useCreateAccount = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: AccountCreate) => accountAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [ACCOUNTS_QUERY_KEY] });
      message.success('Hesap başarıyla oluşturuldu');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Hesap oluşturulurken hata oluştu');
    },
  });
};

/**
 * Hesap güncelle
 */
export const useUpdateAccount = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: AccountUpdate }) =>
      accountAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [ACCOUNTS_QUERY_KEY] });
      message.success('Hesap başarıyla güncellendi');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Hesap güncellenirken hata oluştu');
    },
  });
};

/**
 * Hesap sil
 */
export const useDeleteAccount = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => accountAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [ACCOUNTS_QUERY_KEY] });
      message.success('Hesap başarıyla silindi');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Hesap silinirken hata oluştu');
    },
  });
};
