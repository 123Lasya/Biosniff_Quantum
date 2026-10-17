import { apiClient } from './apiClient';
import { FarmerDashboardResponse, FarmerSystemOverviewResponse } from '../types/api';

export const dashboardService = {
  async getFarmerDashboard(farmId: number): Promise<FarmerDashboardResponse> {
    return apiClient.get<FarmerDashboardResponse>(`/farmer/dashboard/${farmId}`);
  },

  async getFarmerSystemOverview(farmId: number): Promise<FarmerSystemOverviewResponse> {
    return apiClient.get<FarmerSystemOverviewResponse>(`/farmer/system/${farmId}`);
  }
};
