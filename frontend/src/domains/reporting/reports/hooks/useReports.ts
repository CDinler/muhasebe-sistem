/**
 * Reports React Query Hooks
 * Finansal raporlar için React Query hooks
 */
import { useQuery } from '@tanstack/react-query';
import { reportsAPI } from '../api/reports.api';
import { ReportParams } from '../types/reports.types';

// Query keys
const REPORTS_QUERY_KEY = 'reports';

/**
 * Mizan raporu
 */
export const useMizanReport = (params: ReportParams) => {
  return useQuery({
    queryKey: [REPORTS_QUERY_KEY, 'mizan', params],
    queryFn: () => reportsAPI.getMizan(params),
    enabled: !!params.start_date && !!params.end_date,
  });
};

/**
 * Gelir Tablosu
 */
export const useIncomeStatement = (params: ReportParams) => {
  return useQuery({
    queryKey: [REPORTS_QUERY_KEY, 'income-statement', params],
    queryFn: () => reportsAPI.getIncomeStatement(params),
    enabled: !!params.start_date && !!params.end_date,
  });
};

/**
 * Borç/Alacak raporu
 */
export const useDebtorCreditorReport = (params: ReportParams) => {
  return useQuery({
    queryKey: [REPORTS_QUERY_KEY, 'debtor-creditor', params],
    queryFn: () => reportsAPI.getDebtorCreditor(params),
    enabled: !!params.start_date && !!params.end_date,
  });
};

/**
 * Cari hesap raporu
 */
export const useCariReport = (params: ReportParams) => {
  return useQuery({
    queryKey: [REPORTS_QUERY_KEY, 'cari', params],
    queryFn: () => reportsAPI.getCariReport(params),
    enabled: !!params.start_date && !!params.end_date,
  });
};

/**
 * Muavin defteri
 */
export const useMuavinReport = (params: ReportParams) => {
  return useQuery({
    queryKey: [REPORTS_QUERY_KEY, 'muavin', params],
    queryFn: () => reportsAPI.getMuavinReport(params),
    enabled: !!params.start_date && !!params.end_date,
  });
};
