/**
 * Transaction React Query Hooks
 * 
 * Muhasebe fişleri için React Query integration
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import { transactionAPI } from '../api/transaction.api';
import type {
  Transaction,
  TransactionCreate,
  TransactionFilters,
  TransactionSummary
} from '../types/transaction.types';

/**
 * Query keys
 */
export const transactionKeys = {
  all: ['transactions'] as const,
  lists: () => [...transactionKeys.all, 'list'] as const,
  list: (filters: TransactionFilters) => [...transactionKeys.lists(), filters] as const,
  details: () => [...transactionKeys.all, 'detail'] as const,
  detail: (id: number) => [...transactionKeys.details(), id] as const,
  summary: (params?: { date_from?: string; date_to?: string }) =>
    [...transactionKeys.all, 'summary', params] as const,
};

/**
 * Fiş özet istatistikleri
 */
export function useTransactionSummary(params?: {
  date_from?: string;
  date_to?: string;
}) {
  return useQuery({
    queryKey: transactionKeys.summary(params),
    queryFn: () => transactionAPI.getSummary(params),
    staleTime: 30000, // 30 saniye
  });
}

/**
 * Fişleri listele (filtreleme ile)
 */
export function useTransactions(filters: TransactionFilters) {
  return useQuery({
    queryKey: transactionKeys.list(filters),
    queryFn: () => transactionAPI.getFiltered(filters),
    staleTime: 30000,
  });
}

/**
 * Tek fiş detayı
 */
export function useTransaction(id: number, enabled = true) {
  return useQuery({
    queryKey: transactionKeys.detail(id),
    queryFn: () => transactionAPI.getById(id),
    enabled: enabled && id > 0,
    staleTime: 60000, // 1 dakika
  });
}

/**
 * Fiş numarasına göre getir
 */
export function useTransactionByNumber(transactionNumber: string, enabled = true) {
  return useQuery({
    queryKey: [...transactionKeys.all, 'by-number', transactionNumber],
    queryFn: () => transactionAPI.getByNumber(transactionNumber),
    enabled: enabled && !!transactionNumber,
    staleTime: 60000,
  });
}

/**
 * Yeni fiş oluştur
 */
export function useCreateTransaction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TransactionCreate) => transactionAPI.createTransaction(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: transactionKeys.lists() });
      queryClient.invalidateQueries({ queryKey: transactionKeys.all });
      message.success('Fiş başarıyla oluşturuldu');
    },
    onError: (error: any) => {
      message.error(error?.response?.data?.detail || 'Fiş oluşturulurken hata oluştu');
    },
  });
}

/**
 * Fiş güncelle
 */
export function useUpdateTransaction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: TransactionCreate }) =>
      transactionAPI.updateTransaction(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: transactionKeys.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: transactionKeys.lists() });
      queryClient.invalidateQueries({ queryKey: transactionKeys.all });
      message.success('Fiş başarıyla güncellendi');
    },
    onError: (error: any) => {
      message.error(error?.response?.data?.detail || 'Fiş güncellenirken hata oluştu');
    },
  });
}

/**
 * Fiş sil
 */
export function useDeleteTransaction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => transactionAPI.deleteTransaction(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: transactionKeys.lists() });
      queryClient.invalidateQueries({ queryKey: transactionKeys.all });
      message.success('Fiş başarıyla silindi');
    },
    onError: (error: any) => {
      message.error(error?.response?.data?.detail || 'Fiş silinirken hata oluştu');
    },
  });
}
