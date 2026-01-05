/**
 * Config API Client
 * Sistem ayarları için API istekleri
 */
import { BaseAPI } from '../../../../shared/api/base.api';
import {
  SystemConfig,
  SystemConfigCreate,
  SystemConfigUpdate,
  TaxBracket,
  TaxBracketCreate,
  TaxBracketUpdate,
  ConfigsGrouped
} from '../types/config.types';

class ConfigAPI extends BaseAPI {
  constructor() {
    super('/api/v2/settings/config');
  }

  // System Configs
  async getConfigs(category?: string): Promise<ConfigsGrouped> {
    const response = await this.client.get<ConfigsGrouped>('/configs', {
      params: category ? { category } : undefined
    });
    return response.data;
  }

  async getConfig(key: string): Promise<SystemConfig> {
    const response = await this.client.get<SystemConfig>(`/configs/${key}`);
    return response.data;
  }

  async createConfig(data: SystemConfigCreate): Promise<SystemConfig> {
    const response = await this.client.post<SystemConfig>('/configs', data);
    return response.data;
  }

  async updateConfig(key: string, data: SystemConfigUpdate): Promise<SystemConfig> {
    const response = await this.client.put<SystemConfig>(`/configs/${key}`, data);
    return response.data;
  }

  async deleteConfig(id: number): Promise<void> {
    await this.client.delete(`/configs/${id}`);
  }

  // Tax Brackets
  async getTaxBrackets(year?: number): Promise<TaxBracket[]> {
    const response = await this.client.get<TaxBracket[]>('/tax-brackets', {
      params: year ? { year } : undefined
    });
    return response.data;
  }

  async createTaxBracket(data: TaxBracketCreate): Promise<TaxBracket> {
    const response = await this.client.post<TaxBracket>('/tax-brackets', data);
    return response.data;
  }

  async updateTaxBracket(id: number, data: TaxBracketUpdate): Promise<TaxBracket> {
    const response = await this.client.put<TaxBracket>(`/tax-brackets/${id}`, data);
    return response.data;
  }

  async deleteTaxBracket(id: number): Promise<void> {
    await this.client.delete(`/tax-brackets/${id}`);
  }
}

export const configAPI = new ConfigAPI();
