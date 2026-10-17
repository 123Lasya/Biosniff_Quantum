import { apiClient } from './apiClient';
import { EnvironmentCurrentResponse, EnvironmentHistoryResponse } from '../types/api';

export const environmentService = {
  async getFarmEnvironment(farmId: number): Promise<EnvironmentCurrentResponse> {
    return apiClient.get<EnvironmentCurrentResponse>(`/farms/${farmId}/environment`);
  },

  async getFarmEnvironmentHistory(
    farmId: number,
    hours = 24,
    limit = 100
  ): Promise<EnvironmentHistoryResponse> {
    return apiClient.get<EnvironmentHistoryResponse>(
      `/farms/${farmId}/environment/history?hours=${hours}&limit=${limit}`
    );
  }
};
