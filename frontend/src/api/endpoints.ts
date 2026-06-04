import client from './client';
import type {
  LoginResponse,
  Device,
  Alert,
  AlertParams,
  DashboardSummary,
  TrendDataPoint,
  DeviceHealth,
  SensorData,
  ReportData,
} from '../types';

// ─── Auth ───────────────────────────────────────────────
export async function login(username: string, password: string): Promise<LoginResponse> {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  const { data } = await client.post<LoginResponse>('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return data;
}

export async function register(
  username: string,
  email: string,
  password: string
): Promise<{ id: number; username: string; email: string }> {
  const { data } = await client.post('/auth/register', { username, email, password });
  return data;
}

export async function getCurrentUser() {
  const { data } = await client.get('/auth/me');
  return data;
}

// ─── Devices ────────────────────────────────────────────
export async function getDevices(): Promise<Device[]> {
  const { data } = await client.get<any>('/devices');
  return data.items || [];
}

export async function getDevice(id: string): Promise<Device> {
  const { data } = await client.get<Device>(`/devices/${id}`);
  return data;
}

export async function getDeviceLatestData(deviceId: string): Promise<SensorData> {
  const { data } = await client.get<SensorData>(`/devices/${deviceId}/data/latest`);
  return data;
}

// ─── Alerts ─────────────────────────────────────────────
export async function getAlerts(params?: AlertParams): Promise<Alert[]> {
  const { data } = await client.get<any>('/alerts', { params });
  return data.items || [];
}

export async function acknowledgeAlert(id: number): Promise<Alert> {
  const { data } = await client.put<Alert>(`/alerts/${id}/acknowledge`);
  return data;
}

// ─── Dashboard ──────────────────────────────────────────
export async function getDashboardSummary(): Promise<DashboardSummary> {
  const { data } = await client.get<DashboardSummary>('/dashboard/summary');
  return data;
}

// ─── Analytics ──────────────────────────────────────────
export async function getTemperatureTrend(range: string = '24h'): Promise<TrendDataPoint[]> {
  const { data } = await client.get<any>('/analytics/temperature-trend', {
    params: { range },
  });
  return data.data || [];
}

export async function getVibrationTrend(range: string = '24h'): Promise<TrendDataPoint[]> {
  const { data } = await client.get<any>('/analytics/vibration-trend', {
    params: { range },
  });
  return data.data || [];
}

export async function getDeviceHealth(): Promise<DeviceHealth[]> {
  const { data } = await client.get<DeviceHealth[]>('/analytics/device-health');
  return data;
}

// ─── Reports / Export ───────────────────────────────────
export async function getReportData(params: {
  start_date?: string;
  end_date?: string;
  device_ids?: string;
  metrics?: string;
}): Promise<ReportData[]> {
  const { data } = await client.get<ReportData[]>('/reports/data', { params });
  return data;
}

export async function exportData(
  format: 'csv' | 'excel',
  params: {
    start_date?: string;
    end_date?: string;
    device_ids?: string;
    metrics?: string;
  }
): Promise<Blob> {
  const { data } = await client.get(`/reports/export/${format}`, {
    params,
    responseType: 'blob',
  });
  return data;
}
