import { apiClient } from './apiClient';
import { ConnectivityCurrentResponse, ConnectivityHistoryResponse } from '../types/api';

export const connectivityService = {
  async getFarmConnectivity(farmId: number): Promise<ConnectivityCurrentResponse> {
    return apiClient.get<ConnectivityCurrentResponse>(`/farms/${farmId}/connectivity`);
  },

  async getFarmConnectivityHistory(
    farmId: number,
    hours = 24,
    limit = 50
  ): Promise<ConnectivityHistoryResponse> {
    return apiClient.get<ConnectivityHistoryResponse>(
      `/farms/${farmId}/connectivity/history?hours=${hours}&limit=${limit}`
    );
  }
};
