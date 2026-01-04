/**
 * E-Invoice React Query Hooks
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import { einvoiceAPI } from '../api/einvoice.api';
import type {
  EInvoice,
  EInvoiceFilters,
  EInvoiceCreate,
  EInvoiceUpdate
} from '../types/einvoice.types';

const QUERY_KEY = 'einvoices';

/**
 * Özet istatistikler
 */
export function useEInvoiceSummary(params?: {
  date_from?: string;
  date_to?: string;
}) {
  return useQuery({
    queryKey: [QUERY_KEY, 'summary', params],
    queryFn: () => einvoiceAPI.getSummary(params),
    staleTime: 30000, // 30 saniye
  });
}

/**
 * Filtrelenmiş e-fatura listesi
 */
export function useEInvoices(filters: EInvoiceFilters) {
  return useQuery({
    queryKey: [QUERY_KEY, 'list', filters],
    queryFn: () => einvoiceAPI.getFiltered(filters),
    staleTime: 10000, // 10 saniye
  });
}

/**
 * Tek bir e-fatura detayı
 */
export function useEInvoice(id: number | undefined) {
  return useQuery({
    queryKey: [QUERY_KEY, 'detail', id],
    queryFn: () => einvoiceAPI.getById(id!),
    enabled: !!id,
  });
}

/**
 * E-fatura oluşturma
 */
export function useCreateEInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: EInvoiceCreate) => einvoiceAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
      message.success('E-fatura oluşturuldu');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'E-fatura oluşturulamadı');
    },
  });
}

/**
 * E-fatura güncelleme
 */
export function useUpdateEInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: EInvoiceUpdate }) =>
      einvoiceAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
      message.success('E-fatura güncellendi');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'E-fatura güncellenemedi');
    },
  });
}

/**
 * E-fatura silme
 */
export function useDeleteEInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => einvoiceAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
      message.success('E-fatura silindi');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'E-fatura silinemedi');
    },
  });
}

/**
 * XML yükleme (V1 API - legacy)
 */
export function useUploadXML() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (formData: FormData) => einvoiceAPI.uploadXML(formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
      message.success('XML dosyaları yüklendi');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'XML yüklenemedi');
    },
  });
}

/**
 * PDF yükleme (V1 API - legacy)
 */
export function useUploadPDF() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (formData: FormData) => einvoiceAPI.uploadPDF(formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
      message.success('PDF dosyaları yüklendi');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'PDF yüklenemedi');
    },
  });
}

/**
 * XML önizleme (V1 API - legacy)
 */
export function usePreviewXML() {
  return useMutation({
    mutationFn: (formData: FormData) => einvoiceAPI.previewXML(formData),
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Önizleme alınamadı');
    },
  });
}

/**
 * Muhasebe işlemi oluşturma (V1 API - legacy)
 */
export function useCreateTransaction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ invoiceId, data }: { invoiceId: number; data: any }) =>
      einvoiceAPI.createTransaction(invoiceId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
      message.success('Muhasebe işlemi oluşturuldu');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'İşlem oluşturulamadı');
    },
  });
}

/**
 * Muhasebe işlemi önizleme (V1 API - legacy)
 */
export function useTransactionPreview() {
  return useMutation({
    mutationFn: ({ invoiceId, data }: { invoiceId: number; data: any }) =>
      einvoiceAPI.getTransactionPreview(invoiceId, data),
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Önizleme alınamadı');
    },
  });
}
