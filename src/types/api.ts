export interface Coordinates {
  lat: number;
  lng: number;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  role: 'farmer' | 'admin';
  farmer_id: number | null;
  username: string;
  email: string;
  full_name?: string | null;
  profile_image_url?: string | null;
}

export interface UserOut {
  user_id: number;
  username: string;
  email: string;
  role: 'farmer' | 'admin';
  is_active: boolean;
  farmer_id: number | null;
  full_name?: string | null;
  profile_image_url?: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserRegisterRequest {
  username: string;
  email: string;
  password: string;
  role?: 'farmer' | 'admin';
  full_name?: string | null;
  phone?: string | null;
  address?: string | null;
  state?: string | null;
  district?: string | null;
  profile_image_url?: string | null;
  farm_name?: string | null;
  crop?: string | null;
  crop_variety?: string | null;
  area?: number | null;
  latitude?: number | null;
  longitude?: number | null;
  boundary_geojson?: string | null;
}

export interface FarmCreateRequest {
  farm_name: string;
  area: number;
  crop: string;
  crop_variety?: string | null;
  growth_stage?: string | null;
  address?: string | null;
  latitude: number;
  longitude: number;
  boundary_geojson?: string | null;
  status?: string;
  farmer_id?: number | null;
}

export interface FarmerDashboardResponse {
  farmer: Record<string, any>;
  farm: Record<string, any>;
  crop: string;
  crop_variety: string | null;
  farm_coordinates: Coordinates;
  farm_boundary: Coordinates[];
  health_status: 'healthy' | 'diseased' | 'at-risk' | 'inactive' | string;
  latest_node_states: Record<string, any>[];
  battery: number;
  signal: string;
  latest_prediction: Record<string, any> | null;
  confidence: number;
  all_node_predictions: Record<string, any>[];
  detected_diseases: string[];
  disease_status: string | null;
  localization: Record<string, any> | null;
  affected_zone: Record<string, any> | null;
  localized_source: Record<string, any> | null;
  wind: {
    speed: number;
    direction: string;
    angle: number;
  };
  wind_speed: number;
  wind_direction: string;
  temperature: number;
  humidity: number;
  pressure: number;
  soil_moisture: number;
  weather_summary: Record<string, any> | null;
  alerts_summary: Record<string, any> | null;
  latest_recommendation: Record<string, any> | null;
  recommended_action_summary: string | null;
  prediction_trend_24h: Record<string, any>[];
  system_connectivity_summary: Record<string, any> | null;
  active_alerts: Record<string, any>[];
  unread_alerts_count: number;
  last_update: string | null;
}

export interface FarmerSystemOverviewResponse {
  farm_id: number;
  nodes: Record<string, any>; // Node 1, Node 2, Node 3
  connectivity_summary: Record<string, any>;
  wind_summary: Record<string, any>;
  environment_summary: Record<string, any>;
  farm_health: Record<string, any>;
  latest_activity: Record<string, any>[];
}

export interface FarmOut {
  farm_id: number;
  farmer_id: number;
  farm_name: string;
  crop: string;
  crop_variety: string | null;
  growth_stage: string | null;
  area: number;
  latitude: number;
  longitude: number;
  address: string | null;
  boundary_geojson: string | null;
  status: string;
  node_count: number;
  created_at?: string;
  updated_at?: string;
}

export interface NodeOut {
  node_id: string;
  farm_id: number;
  node_name: string;
  latitude: number;
  longitude: number;
  battery_percentage: number;
  signal_strength: number;
  is_master: boolean;
  firmware_version: string;
  status: string;
  last_seen: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface NodeSensorHistoryResponse {
  node_id: string;
  cycles: Record<string, any>[];
  latest_5_cycle_window: Record<string, any>[];
  window_ready: boolean;
  available_cycles: number;
  required_cycles: number;
}

export interface PredictionItem {
  prediction_id: number;
  node_id: string;
  farm_id: number;
  cycle_id: number;
  timestamp: string;
  window_start: string | null;
  window_end: string | null;
  predicted_class: string;
  disease_detected: boolean;
  confidence: number;
  anomaly_score: number | null;
  all_class_probabilities: Record<string, number>;
  model_version: string | null;
}

export interface EnvironmentCurrentResponse {
  farm_id: number;
  node_id: string | null;
  wind_speed: number;
  wind_direction: string;
  wind_angle: number;
  soil_moisture: number;
  temperature: number;
  humidity: number;
  pressure: number;
  solar_radiation: number;
  recorded_at: string;
}

export interface EnvironmentHistoryResponse {
  farm_id: number;
  readings: Record<string, any>[];
  total_records: number;
}

export interface ConnectivityCurrentResponse {
  farm_id: number;
  node_id: string | null;
  gateway_type: string;
  carrier: string;
  rssi: number;
  rsrp: number | null;
  rsrq: number | null;
  sinr: number | null;
  latency_ms: number;
  packet_loss_pct: number;
  uplink_mbps: number;
  downlink_mbps: number;
  status: string;
  recorded_at: string;
}

export interface ConnectivityHistoryResponse {
  farm_id: number;
  logs: Record<string, any>[];
  total_records: number;
}

export interface LocalizationResponse {
  localization_id: number | null;
  farm_id: number;
  active: boolean;
  estimated_latitude: number | null;
  estimated_longitude: number | null;
  confidence_radius_meters: number | null;
  affected_zone: Record<string, any> | null;
  detected_conditions: string[];
  trigger_nodes: string[];
  severity: string | null;
  created_at: string | null;
}

export interface FarmAlertsResponse {
  farm_id: number;
  alerts: Record<string, any>[];
  unread_count: number;
}

export interface AdminDashboardResponse {
  total_farmers: number;
  total_farms: number;
  active_farms: number;
  inactive_farms: number;
  healthy_farms: number;
  diseased_farms: number;
  at_risk_farms: number;
  active_nodes: number;
  offline_nodes: number;
  active_alerts: number;
  network_health: Record<string, any>;
  regional_summaries: Record<string, any>[];
  crops_monitored: Record<string, any>[];
  recent_activity: Record<string, any>[];
  recent_alerts: Record<string, any>[];
}

export interface AdminFarmMapItem {
  farm_id: number;
  farm_name: string;
  farmer: string;
  state: string | null;
  district: string | null;
  latitude: number;
  longitude: number;
  crop: string;
  crop_variety: string | null;
  area_acres: number;
  health_status: string;
  disease_status: string;
  active_status: string;
  status: string;
}

export interface AdminFarmersListResponse {
  items: Record<string, any>[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AdminFarmerProfileResponse {
  farmer_details: Record<string, any>;
  farms: Record<string, any>[];
  farm_areas: number;
  crops: string[];
  locations: Record<string, any>[];
  health: string;
  nodes: Record<string, any>[];
  alerts: Record<string, any>[];
  latest_predictions: Record<string, any>[];
  environment_summaries: Record<string, any>[];
  history_summaries: Record<string, any>[];
  advisories: Record<string, any>[];
}

export interface AdminNodeListItem {
  node_id: string;
  node_name: string;
  farm_id: number;
  farm_name: string;
  farmer_id: number;
  farmer_name: string;
  latitude: number;
  longitude: number;
  status: string;
  battery_percentage: number | null;
  signal_strength: number | null;
  firmware_version: string | null;
  is_master: boolean;
  last_seen: string | null;
  latest_temperature: number | null;
  latest_humidity: number | null;
  latest_pressure: number | null;
  latest_voc: number | null;
  latest_prediction: string | null;
}

