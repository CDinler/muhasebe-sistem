/**
 * Contacts React Query Hooks
 * Cari hesaplar için React Query hooks
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { contactsAPI } from '../api/contacts.api';
import { ContactCreateRequest, ContactListParams } from '../types/contact.types';
import { message } from 'antd';

// Query keys
const CONTACTS_QUERY_KEY = 'contacts';

/**
 * Carileri listele
 */
export const useContactsList = (params?: ContactListParams) => {
  return useQuery({
    queryKey: [CONTACTS_QUERY_KEY, 'list', params],
    queryFn: () => contactsAPI.getList(params),
  });
};

/**
 * Tek cari getir
 */
export const useContact = (id: number) => {
  return useQuery({
    queryKey: [CONTACTS_QUERY_KEY, 'detail', id],
    queryFn: () => contactsAPI.getById(id),
    enabled: !!id,
  });
};

/**
 * Vergi numarasına göre cari getir
 */
export const useContactByTaxNumber = (taxNumber: string) => {
  return useQuery({
    queryKey: [CONTACTS_QUERY_KEY, 'tax', taxNumber],
    queryFn: () => contactsAPI.getByTaxNumber(taxNumber),
    enabled: !!taxNumber,
  });
};

/**
 * Cari ara
 */
export const useContactSearch = (query: string, isActive: boolean = true) => {
  return useQuery({
    queryKey: [CONTACTS_QUERY_KEY, 'search', query, isActive],
    queryFn: () => contactsAPI.search(query, isActive),
    enabled: query.length >= 2, // En az 2 karakter girilince ara
  });
};

/**
 * Yeni cari oluştur
 */
export const useCreateContact = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ContactCreateRequest) => contactsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CONTACTS_QUERY_KEY] });
      message.success('Cari başarıyla oluşturuldu');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Cari oluşturulurken hata oluştu');
    },
  });
};

/**
 * Cari güncelle
 */
export const useUpdateContact = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ContactCreateRequest }) =>
      contactsAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CONTACTS_QUERY_KEY] });
      message.success('Cari başarıyla güncellendi');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Cari güncellenirken hata oluştu');
    },
  });
};

/**
 * Cari sil
 */
export const useDeleteContact = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => contactsAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CONTACTS_QUERY_KEY] });
      message.success('Cari başarıyla silindi');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Cari silinirken hata oluştu');
    },
  });
};
