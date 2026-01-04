/**
 * Account API service
 */
import { CRUDService } from '@/shared/api/base.api';
import { Account } from '../types/account.types';

class AccountAPI extends CRUDService<Account, any, any> {
  constructor() {
    super('/api/v2/accounts');
  }
}

export const accountAPI = new AccountAPI();
