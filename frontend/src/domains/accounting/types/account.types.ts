/**
 * Account types
 */
export interface Account {
  id: number;
  account_code: string;
  account_name: string;
  parent_id?: number;
  account_type?: string;
}
