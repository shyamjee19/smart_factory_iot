export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface Device {
  id: number;
  device_id: string;
  name: string;
  type: string;
  location: string;
  status: string;
  health_score: number;
  install_date: string;
  last_seen: string;
  firmware_version: string;
  ip_address: string;
}

export interface SensorData {
  id: number;
  device_id: string;
  timestamp: string;
  temperature: number;
  humidity: number;
  pressure: number;
  vibration: number;
  voltage: number;
  current: number;
}

export interface Alert {
  id: number;
  device_id: string;
  device_name?: string;
  alert_type: string;
  severity: string;
  metric: string;
  value: number;
  threshold: number;
  message: string;
  acknowledged: boolean;
  acknowledged_by?: string;
  acknowledged_at?: string;
  created_at: string;
}

export interface DashboardSummary {
  total_devices: number;
  online_devices: number;
  offline_devices: number;
  active_alerts: number;
  critical_alerts: number;
  warning_alerts: number;
  info_alerts: number;
  avg_health_score: number;
}

export interface TrendDataPoint {
  timestamp: string;
  [key: string]: string | number;
}

export interface DeviceHealth {
  device_id: string;
  device_name: string;
  health_score: number;
  status: string;
  uptime_percentage: number;
}

export interface AlertParams {
  severity?: string;
  device_id?: string;
  acknowledged?: boolean;
  skip?: number;
  limit?: number;
}

export interface ExportParams {
  start_date?: string;
  end_date?: string;
  device_ids?: string[];
  metrics?: string[];
  format: 'csv' | 'excel';
}

export interface WebSocketMessage {
  type: string;
  device_id: string;
  data: SensorData;
  timestamp: string;
}

export interface KPIData {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
  trend?: number;
  trendLabel?: string;
}

export interface ChartDataPoint {
  time: string;
  [key: string]: string | number;
}

export interface ReportData {
  device_id: string;
  device_name: string;
  timestamp: string;
  temperature: number;
  humidity: number;
  pressure: number;
  vibration: number;
  voltage: number;
  current: number;
}
