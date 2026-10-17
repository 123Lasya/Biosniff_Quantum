import { apiClient } from './apiClient';
import { NodeOut, NodeSensorHistoryResponse, PredictionItem } from '../types/api';

export interface NodeCreateParams {
  node_id: string;
  farm_id: number;
  node_name: string;
  latitude: number;
  longitude: number;
  battery_percentage?: number;
  signal_strength?: number;
  is_master?: boolean;
  firmware_version?: string;
}

export interface NodeUpdateParams {
  node_name?: string;
  latitude?: number;
  longitude?: number;
  battery_percentage?: number;
  signal_strength?: number;
  is_master?: boolean;
  firmware_version?: string;
  status?: string;
}

export const nodeService = {
  async createNode(data: NodeCreateParams): Promise<NodeOut> {
    return apiClient.post<NodeOut>('/nodes', data);
  },

  async getNode(nodeId: string): Promise<NodeOut> {
    return apiClient.get<NodeOut>(`/nodes/${nodeId}`);
  },

  async updateNode(nodeId: string, data: NodeUpdateParams): Promise<NodeOut> {
    return apiClient.put<NodeOut>(`/nodes/${nodeId}`, data);
  },

  async deleteNode(nodeId: string): Promise<void> {
    return apiClient.delete<void>(`/nodes/${nodeId}`);
  },

  async getNodeHistory(nodeId: string, limit = 50): Promise<any> {
    return apiClient.get<any>(`/nodes/${nodeId}/history?limit=${limit}`);
  },

  async getNodePredictions(nodeId: string, limit = 50): Promise<PredictionItem[]> {
    return apiClient.get<PredictionItem[]>(`/nodes/${nodeId}/predictions?limit=${limit}`);
  },

  async getNodeSensorHistory(
    nodeId: string,
    limit = 50,
    onlyValid = false
  ): Promise<NodeSensorHistoryResponse> {
    return apiClient.get<NodeSensorHistoryResponse>(
      `/nodes/${nodeId}/sensor-history?limit=${limit}&only_valid=${onlyValid}`
    );
  },

  async getNodeAlerts(nodeId: string, limit = 50): Promise<any> {
    return apiClient.get<any>(`/nodes/${nodeId}/alerts?limit=${limit}`);
  }
};
