/**
 * Payroll Hooks
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import payrollAPI from '../api/payroll.api';
import type { PayrollCalculateRequest } from '../types/payroll.types';

/**
 * Bordro listesi
 */
export function usePayrollList(yil: number, ay: number) {
  return useQuery({
    queryKey: ['payroll', 'list', yil, ay],
    queryFn: () => payrollAPI.getList(yil, ay),
    enabled: !!yil && !!ay,
  });
}

/**
 * Bordro hesaplama
 */
export function useCalculatePayroll() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: PayrollCalculateRequest) => payrollAPI.calculate(data),
    onSuccess: (_, variables) => {
      message.success('Bordro hesaplaması tamamlandı');
      queryClient.invalidateQueries({ queryKey: ['payroll', 'list', variables.yil, variables.ay] });
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Hesaplama başarısız');
    },
  });
}
