import { apiClient } from './apiClient';
import { FarmOut, NodeOut } from '../types/api';

export interface FarmCreateParams {
  farm_name: string;
  crop: string;
  crop_variety?: string;
  growth_stage?: string;
  area: number;
  latitude: number;
  longitude: number;
  address?: string;
  boundary_geojson?: string;
}

export interface FarmUpdateParams {
  farm_name?: string;
  crop?: string;
  crop_variety?: string;
  growth_stage?: string;
  area?: number;
  latitude?: number;
  longitude?: number;
  address?: string;
  boundary_geojson?: string;
  status?: string;
}

export const farmService = {
  async getFarms(skip = 0, limit = 100): Promise<FarmOut[]> {
    return apiClient.get<FarmOut[]>(`/farms?skip=${skip}&limit=${limit}`);
  },

  async createFarm(data: FarmCreateParams): Promise<FarmOut> {
    return apiClient.post<FarmOut>('/farms', data);
  },

  async getFarm(farmId: number): Promise<FarmOut> {
    return apiClient.get<FarmOut>(`/farms/${farmId}`);
  },

  async updateFarm(farmId: number, data: FarmUpdateParams): Promise<FarmOut> {
    return apiClient.put<FarmOut>(`/farms/${farmId}`, data);
  },

  async deleteFarm(farmId: number): Promise<void> {
    return apiClient.delete<void>(`/farms/${farmId}`);
  },

  async getFarmNodes(farmId: number): Promise<NodeOut[]> {
    return apiClient.get<NodeOut[]>(`/farms/${farmId}/nodes`);
  }
};
