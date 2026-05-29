import { format, formatDistanceToNow, parseISO, isValid } from 'date-fns';

export function formatNumber(value: number | undefined | null, decimals: number = 1): string {
  if (value === undefined || value === null || isNaN(value)) return '—';
  if (Math.abs(value) >= 1_000_000) {
    return (value / 1_000_000).toFixed(decimals) + 'M';
  }
  if (Math.abs(value) >= 1_000) {
    return (value / 1_000).toFixed(decimals) + 'K';
  }
  return value.toFixed(decimals);
}

export function formatInteger(value: number | undefined | null): string {
  if (value === undefined || value === null || isNaN(value)) return '0';
  return Math.round(value).toLocaleString();
}

export function formatTimestamp(
  date: string | Date | undefined | null,
  fmt: string = 'MMM dd, HH:mm'
): string {
  if (!date) return '—';
  try {
    const d = typeof date === 'string' ? parseISO(date) : date;
    if (!isValid(d)) return '—';
    return format(d, fmt);
  } catch {
    return '—';
  }
}

export function formatRelativeTime(date: string | Date | undefined | null): string {
  if (!date) return '—';
  try {
    const d = typeof date === 'string' ? parseISO(date) : date;
    if (!isValid(d)) return '—';
    return formatDistanceToNow(d, { addSuffix: true });
  } catch {
    return '—';
  }
}

export function formatDuration(seconds: number | undefined | null): string {
  if (seconds === undefined || seconds === null || isNaN(seconds)) return '—';
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  if (hrs > 0) return `${hrs}h ${mins}m`;
  if (mins > 0) return `${mins}m ${secs}s`;
  return `${secs}s`;
}

export function formatPercentage(value: number | undefined | null, decimals: number = 1): string {
  if (value === undefined || value === null || isNaN(value)) return '—';
  return `${value.toFixed(decimals)}%`;
}

export function getSeverityColor(severity: string): string {
  switch (severity.toLowerCase()) {
    case 'critical':
      return '#f43f5e';
    case 'warning':
      return '#f59e0b';
    case 'info':
      return '#3b82f6';
    default:
      return '#64748b';
  }
}

export function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'online':
      return '#10b981';
    case 'warning':
      return '#f59e0b';
    case 'critical':
      return '#f43f5e';
    case 'offline':
      return '#64748b';
    default:
      return '#64748b';
  }
}

export function getHealthColor(score: number): string {
  if (score >= 90) return '#10b981';
  if (score >= 70) return '#f59e0b';
  if (score >= 50) return '#f97316';
  return '#f43f5e';
}

export function getMetricUnit(metric: string): string {
  switch (metric.toLowerCase()) {
    case 'temperature':
      return '°C';
    case 'humidity':
      return '%';
    case 'pressure':
      return 'hPa';
    case 'vibration':
      return 'mm/s';
    case 'voltage':
      return 'V';
    case 'current':
      return 'A';
    default:
      return '';
  }
}
