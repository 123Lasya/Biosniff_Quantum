import { apiClient } from './apiClient';
import {
  AdminDashboardResponse,
  AdminFarmMapItem,
  AdminFarmersListResponse,
  AdminFarmerProfileResponse,
  AdminNodeListItem
} from '../types/api';

export interface AdminFarmersFilterParams {
  search?: string;
  state?: string;
  district?: string;
  crop?: string;
  health?: string;
  status?: string;
  page?: number;
  page_size?: number;
}

export const adminService = {
  async getDashboard(): Promise<AdminDashboardResponse> {
    return apiClient.get<AdminDashboardResponse>('/admin/dashboard');
  },

  async getFarmsMap(): Promise<AdminFarmMapItem[]> {
    return apiClient.get<AdminFarmMapItem[]>('/admin/farms/map');
  },

  async getFarmers(params: AdminFarmersFilterParams = {}): Promise<AdminFarmersListResponse> {
    const query = new URLSearchParams();
    if (params.search) query.append('search', params.search);
    if (params.state && params.state !== 'All States') query.append('state', params.state);
    if (params.district) query.append('district', params.district);
    if (params.crop && params.crop !== 'All Crops') query.append('crop', params.crop);
    if (params.health && params.health !== 'All Health') query.append('health', params.health);
    if (params.status && params.status !== 'All Status') query.append('status', params.status);
    if (params.page) query.append('page', params.page.toString());
    if (params.page_size) query.append('page_size', params.page_size.toString());

    const queryString = query.toString();
    const endpoint = `/admin/farmers${queryString ? `?${queryString}` : ''}`;
    return apiClient.get<AdminFarmersListResponse>(endpoint);
  },

  async getFarmerProfile(farmerId: number): Promise<AdminFarmerProfileResponse> {
    return apiClient.get<AdminFarmerProfileResponse>(`/admin/farmers/${farmerId}`);
  },

  async getNodes(): Promise<AdminNodeListItem[]> {
    return apiClient.get<AdminNodeListItem[]>('/admin/nodes');
  }
};

