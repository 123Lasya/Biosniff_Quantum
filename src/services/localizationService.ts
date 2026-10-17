import { apiClient } from './apiClient';
import { LocalizationResponse } from '../types/api';

export const localizationService = {
  async getLatestLocalization(farmId: number): Promise<LocalizationResponse> {
    return apiClient.get<LocalizationResponse>(`/farms/${farmId}/localization/latest`);
  },

  async getLocalizationHistory(farmId: number, limit = 50): Promise<any> {
    return apiClient.get<any>(`/farms/${farmId}/localization/history?limit=${limit}`);
  }
};
