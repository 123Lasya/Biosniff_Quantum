import { apiClient } from './apiClient';
import { FarmAlertsResponse } from '../types/api';

export const alertService = {
  async getFarmAlerts(farmId: number, limit = 50): Promise<FarmAlertsResponse> {
    return apiClient.get<FarmAlertsResponse>(`/farms/${farmId}/alerts?limit=${limit}`);
  },

  async markAlertRead(alertId: number): Promise<{ alert_id: number; is_read: boolean }> {
    return apiClient.put<{ alert_id: number; is_read: boolean }>(`/alerts/${alertId}/read`);
  }
};
