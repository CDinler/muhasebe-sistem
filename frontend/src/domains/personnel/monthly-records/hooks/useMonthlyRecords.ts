import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { monthlyRecordsApi } from '../api/monthly-records.api';
import type {
  MonthlyRecordsListParams,
  UploadSicilParams
} from '../types/monthly-records.types';

const QUERY_KEYS = {
  monthlyRecords: ['monthlyRecords'] as const,
  monthlyRecordsList: (params?: MonthlyRecordsListParams) => 
    [...QUERY_KEYS.monthlyRecords, 'list', params] as const,
  monthlyRecord: (id: number) => 
    [...QUERY_KEYS.monthlyRecords, id] as const,
  periods: () => 
    [...QUERY_KEYS.monthlyRecords, 'periods'] as const,
};

export const useMonthlyRecordsList = (params?: MonthlyRecordsListParams) => {
  return useQuery({
    queryKey: QUERY_KEYS.monthlyRecordsList(params),
    queryFn: () => monthlyRecordsApi.list(params),
  });
};

export const useMonthlyRecord = (id: number) => {
  return useQuery({
    queryKey: QUERY_KEYS.monthlyRecord(id),
    queryFn: () => monthlyRecordsApi.get(id),
    enabled: !!id,
  });
};

export const usePeriods = () => {
  return useQuery({
    queryKey: QUERY_KEYS.periods(),
    queryFn: () => monthlyRecordsApi.getPeriods(),
  });
};

export const useUploadSicil = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: UploadSicilParams) => monthlyRecordsApi.uploadSicil(params),
    onSuccess: () => {
      // Invalidate all monthly records queries to refresh data
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.monthlyRecords });
    },
  });
};
