/**
 * Reports API Client
 * Finansal raporlar için API istekleri
 */
import { BaseAPI } from '../../../../shared/api/base.api';
import {
  MizanReport,
  IncomeStatement,
  DebtorCreditorReport,
  CariReport,
  MuavinReport,
  ReportParams
} from '../types/reports.types';

class ReportsAPI extends BaseAPI {
  constructor() {
    super('/api/v2/reporting/reports');
  }

  /**
   * Mizan (Trial Balance) raporu
   */
  async getMizan(params: ReportParams): Promise<MizanReport> {
    const response = await this.client.get<MizanReport>('/mizan', { params });
    return response.data;
  }

  /**
   * Gelir Tablosu (Income Statement)
   */
  async getIncomeStatement(params: ReportParams): Promise<IncomeStatement> {
    const response = await this.client.get<IncomeStatement>('/income-statement', { params });
    return response.data;
  }

  /**
   * Borç/Alacak raporu
   */
  async getDebtorCreditor(params: ReportParams): Promise<DebtorCreditorReport> {
    const response = await this.client.get<DebtorCreditorReport>('/debtor-creditor', { params });
    return response.data;
  }

  /**
   * Cari hesap raporu
   */
  async getCariReport(params: ReportParams): Promise<CariReport> {
    const response = await this.client.get<CariReport>('/cari', { params });
    return response.data;
  }

  /**
   * Muavin defteri (General Ledger)
   */
  async getMuavinReport(params: ReportParams): Promise<MuavinReport> {
    const response = await this.client.get<MuavinReport>('/muavin', { params });
    return response.data;
  }
}

export const reportsAPI = new ReportsAPI();
