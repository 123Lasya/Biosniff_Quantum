import { apiClient } from './apiClient';
import { PredictionItem } from '../types/api';

export const predictionService = {
  async getFarmPredictions(farmId: number, limit = 50): Promise<{ farm_id: number; predictions: PredictionItem[]; total: number }> {
    return apiClient.get<{ farm_id: number; predictions: PredictionItem[]; total: number }>(`/farms/${farmId}/predictions?limit=${limit}`);
  }
};
