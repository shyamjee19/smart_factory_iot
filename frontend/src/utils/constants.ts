export const DEVICE_TYPES = [
  'CNC Machine',
  'Robotic Arm',
  'Conveyor Belt',
  'Hydraulic Press',
  'Welding Station',
  'Assembly Line',
  'Packaging Unit',
  'Quality Inspector',
] as const;

export type DeviceType = (typeof DEVICE_TYPES)[number];

export const SEVERITY_LEVELS = ['critical', 'warning', 'info'] as const;
export type SeverityLevel = (typeof SEVERITY_LEVELS)[number];

export const STATUS_OPTIONS = ['online', 'offline', 'warning', 'critical'] as const;
export type DeviceStatus = (typeof STATUS_OPTIONS)[number];

export const TIME_RANGES = [
  { label: '1H', value: '1h' },
  { label: '6H', value: '6h' },
  { label: '24H', value: '24h' },
  { label: '7D', value: '7d' },
  { label: '30D', value: '30d' },
] as const;

export type TimeRange = '1h' | '6h' | '24h' | '7d' | '30d';

export const METRIC_NAMES = [
  'temperature',
  'humidity',
  'pressure',
  'vibration',
  'voltage',
  'current',
] as const;

export type MetricName = (typeof METRIC_NAMES)[number];

export const COLORS = {
  primary: '#00d4ff',
  secondary: '#7c3aed',
  success: '#10b981',
  warning: '#f59e0b',
  error: '#f43f5e',
  info: '#3b82f6',
  cyan: '#00d4ff',
  emerald: '#10b981',
  violet: '#7c3aed',
  amber: '#f59e0b',
  rose: '#f43f5e',
  blue: '#3b82f6',
  indigo: '#6366f1',
  teal: '#14b8a6',
  orange: '#f97316',
  pink: '#ec4899',
} as const;

export const CHART_COLORS = [
  '#00d4ff',
  '#10b981',
  '#f59e0b',
  '#f43f5e',
  '#7c3aed',
  '#3b82f6',
  '#14b8a6',
  '#f97316',
  '#ec4899',
  '#6366f1',
];

export const GLASSMORPHISM = {
  background: 'rgba(17, 24, 39, 0.7)',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(148, 163, 184, 0.08)',
  borderRadius: '16px',
} as const;

export const SIDEBAR_WIDTH = 260;
export const HEADER_HEIGHT = 70;

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';
export const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || `ws://${window.location.host}/ws`;
