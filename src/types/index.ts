export type UserRole = 'farmer' | 'admin';

export type HealthStatus = 'healthy' | 'at-risk' | 'diseased' | 'inactive';
export type NodeStatus = 'online' | 'offline' | 'maintenance';
export type AlertSeverity = 'critical' | 'high' | 'medium' | 'low';

export interface FarmCoordinate {
  lat: number;
  lng: number;
}

export interface SensorNode {
  id: string; // e.g. "Node 1"
  nodeId: string; // e.g. "BSN-01"
  name: string;
  status: NodeStatus;
  battery: number;
  signal: 'Excellent' | 'Good' | 'Fair' | 'Poor';
  signalDbm?: number;
  coordinates: FarmCoordinate;
  lastTransmission: string;
  firmwareVersion: string;
  deploymentDate: string;
  hardware: string;
  powerSource: string;
  deviceTemp?: number;
  batteryVoltage?: number;
  uptime?: string;
  readings: {
    temperature: number;
    humidity: number;
    pressure: number;
    totalVoc: number;
    gasResistance10: number[]; // 10 elements (kΩ)
    iaq?: string;
  };
}

export interface Farm {
  id: string;
  name: string;
  farmerName: string;
  farmerId: string;
  state: string;
  district: string;
  village: string;
  locationName: string;
  coordinates: FarmCoordinate;
  boundary: FarmCoordinate[];
  areaAcres: number;
  crop: string;
  cropVariety: string;
  growthStage: string;
  healthStatus: HealthStatus;
  confidence: number;
  lastAnalysis: string;
  disease?: {
    name: string;
    confidence: number;
    detectedAt: string;
    affectedZone: string;
    localizationStatus: 'Active' | 'Complete';
    sourceCoordinates: FarmCoordinate;
    recommendedAction: string;
    precautions: string[];
  };
  nodes: SensorNode[];
  environmental: {
    temperature: number;
    humidity: number;
    pressure: number;
    windSpeed: number; // m/s
    windDirection: string; // "NE (48°)"
    windAngle: number;
    weatherCondition: string;
  };
}

export interface FarmerRecord {
  id: string;
  name: string;
  farmerId: string;
  phone: string;
  email: string;
  village: string;
  district: string;
  state: string;
  crops: string[];
  farmCount: number;
  totalAreaAcres: number;
  healthStatus: HealthStatus;
  status: 'Active' | 'Inactive';
  avatarUrl: string;
  farmingExperienceYears: number;
  memberSince: string;
  aadhaarMasked?: string;
  landOwnership?: string;
  preferredLanguage?: string;
}

export interface NetworkHealth {
  onlineNodes: number;
  offlineNodes: number;
  maintenanceNodes: number;
  healthPercent: number;
  uptimePercent: number;
}

export interface AlertItem {
  id: string;
  time: string;
  farm: string;
  issue: string;
  severity: AlertSeverity;
  status: 'Open' | 'Investigating' | 'Resolved';
}
