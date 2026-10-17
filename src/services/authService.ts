import { apiClient, setToken, removeToken, getToken } from './apiClient';
import { TokenResponse, UserOut } from '../types/api';

export interface LoginParams {
  username_or_email: string;
  password: string;
}

export interface RegisterParams {
  username: string;
  email: string;
  password: string;
  role?: 'farmer' | 'admin';
  full_name?: string;
  phone?: string;
  address?: string;
  state?: string;
  district?: string;
  profile_image_url?: string;
  farm_name?: string;
  crop?: string;
  crop_variety?: string;
  area?: number;
  latitude?: number;
  longitude?: number;
  boundary_geojson?: string;
}

export const authService = {
  async login(credentials: LoginParams): Promise<TokenResponse> {
    const data = await apiClient.post<TokenResponse>('/auth/login', credentials);
    if (data.access_token) {
      setToken(data.access_token);
      localStorage.setItem('biosniff_user', JSON.stringify(data));
    }
    return data;
  },

  async register(params: RegisterParams): Promise<UserOut> {
    return apiClient.post<UserOut>('/auth/register', params);
  },

  async uploadAvatar(file: File): Promise<{ url: string; filename: string }> {
    const formData = new FormData();
    formData.append('file', file);
    const token = getToken();
    const baseUrl = (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8000/api';
    const response = await fetch(`${baseUrl}/auth/upload-avatar`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || 'Failed to upload profile photo');
    }
    return response.json();
  },

  async getMe(): Promise<UserOut> {
    return apiClient.get<UserOut>('/auth/me');
  },

  logout(): void {
    removeToken();
  },

  getStoredUser(): TokenResponse | null {
    const userStr = localStorage.getItem('biosniff_user');
    if (!userStr) return null;
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  },

  isAuthenticated(): boolean {
    return !!getToken();
  }
};
