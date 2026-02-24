/**
 * Config API Client
 * Sistem ayarları için API istekleri
 */
import { CRUDService } from '../../../../shared/api/base.api';
import {
  SystemConfig,
  SystemConfigCreate,
  SystemConfigUpdate,
  TaxBracket,
  TaxBracketCreate,
  TaxBracketUpdate,
  ConfigsGrouped
} from '../types/config.types';

class ConfigAPI extends CRUDService<SystemConfig, SystemConfigCreate, SystemConfigUpdate> {
  constructor() {
    super('/api/v2/settings/config');
  }

  // System Configs
  async getConfigs(category?: string): Promise<ConfigsGrouped> {
    const response = await this.client.get<ConfigsGrouped>(`${this.endpoint}/configs`, {
      params: category ? { category } : undefined
    });
    return response.data;
  }

  async getConfig(key: string): Promise<SystemConfig> {
    const response = await this.client.get<SystemConfig>(`${this.endpoint}/configs/${key}`);
    return response.data;
  }

  async createConfig(data: SystemConfigCreate): Promise<SystemConfig> {
    const response = await this.client.post<SystemConfig>(`${this.endpoint}/configs`, data);
    return response.data;
  }

  async updateConfig(key: string, data: SystemConfigUpdate): Promise<SystemConfig> {
    const response = await this.client.put<SystemConfig>(`${this.endpoint}/configs/${key}`, data);
    return response.data;
  }

  async deleteConfig(id: number): Promise<void> {
    await this.client.delete(`${this.endpoint}/configs/${id}`);
  }

  // Tax Brackets
  async getTaxBrackets(year?: number): Promise<TaxBracket[]> {
    const response = await this.client.get<TaxBracket[]>(`${this.endpoint}/tax-brackets`, {
      params: year ? { year } : undefined
    });
    return response.data;
  }

  async createTaxBracket(data: TaxBracketCreate): Promise<TaxBracket> {
    const response = await this.client.post<TaxBracket>(`${this.endpoint}/tax-brackets`, data);
    return response.data;
  }

  async updateTaxBracket(id: number, data: TaxBracketUpdate): Promise<TaxBracket> {
    const response = await this.client.put<TaxBracket>(`${this.endpoint}/tax-brackets/${id}`, data);
    return response.data;
  }

  async deleteTaxBracket(id: number): Promise<void> {
    await this.client.delete(`${this.endpoint}/tax-brackets/${id}`);
  }
}

export const configAPI = new ConfigAPI();
