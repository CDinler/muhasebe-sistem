/**
 * Account React Query hooks
 */
import { useQuery } from '@tanstack/react-query';
import { accountAPI } from '../api/account.api';

export function useAccounts() {
  return useQuery({
    queryKey: ['accounts'],
    queryFn: () => accountAPI.getAll(),
    staleTime: 10 * 60 * 1000, // 10 minutes (rarely changes)
  });
}
