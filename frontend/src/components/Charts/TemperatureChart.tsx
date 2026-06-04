import React, { useState, useEffect } from 'react';
import { Card, CardContent, Box, Typography, ToggleButtonGroup, ToggleButton } from '@mui/material';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { getTemperatureTrend } from '../../api/endpoints';
import { CHART_COLORS, TIME_RANGES } from '../../utils/constants';
import type { TrendDataPoint } from '../../types';
import { format, parseISO } from 'date-fns';

const CustomTooltip: React.FC<{
  active?: boolean;
  payload?: Array<{ name: string; value: number; color: string }>;
  label?: string;
}> = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <Box
      sx={{
        background: 'rgba(17, 24, 39, 0.95)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(148, 163, 184, 0.15)',
        borderRadius: '10px',
        p: 1.5,
        minWidth: 150,
      }}
    >
      <Typography sx={{ fontSize: '0.7rem', color: '#64748b', mb: 0.5 }}>{label}</Typography>
      {payload.map((entry, idx) => (
        <Box key={idx} sx={{ display: 'flex', justifyContent: 'space-between', gap: 2, py: 0.2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box sx={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: entry.color }} />
            <Typography sx={{ fontSize: '0.75rem', color: '#94a3b8' }}>{entry.name}</Typography>
          </Box>
          <Typography sx={{ fontSize: '0.75rem', fontWeight: 600, color: '#e2e8f0' }}>
            {entry.value?.toFixed(1)}°C
          </Typography>
        </Box>
      ))}
    </Box>
  );
};

const TemperatureChart: React.FC = () => {
  const [range, setRange] = useState('24h');
  const [data, setData] = useState<TrendDataPoint[]>([]);
  const [deviceKeys, setDeviceKeys] = useState<string[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await getTemperatureTrend(range);
        setData(result);
        if (result.length > 0) {
          const keys = Object.keys(result[0]).filter((k) => k !== 'timestamp');
          setDeviceKeys(keys);
        }
      } catch {
        setData([]);
        setDeviceKeys([]);
      }
    };
    fetchData();
  }, [range]);

  const formatXAxis = (value: string) => {
    try {
      const d = parseISO(value);
      return range === '1h' || range === '6h' ? format(d, 'HH:mm') : format(d, 'MMM dd HH:mm');
    } catch {
      return value;
    }
  };

  if (data.length === 0) {
    return (
      <Card>
        <CardContent sx={{ p: 3, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 410 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#e2e8f0', mb: 1 }}>
            No Temperature Historical Data
          </Typography>
          <Typography variant="body2" sx={{ color: '#64748b', fontSize: '0.8rem' }} align="center">
            No telemetry records have been logged in PostgreSQL for the selected time range.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, fontSize: '1rem' }}>
              Temperature Trends
            </Typography>
            <Typography sx={{ fontSize: '0.8rem', color: '#64748b' }}>
              Temperature readings across devices
            </Typography>
          </Box>
          <ToggleButtonGroup
            value={range}
            exclusive
            onChange={(_, v) => v && setRange(v)}
            size="small"
            sx={{
              '& .MuiToggleButton-root': {
                color: '#64748b',
                borderColor: 'rgba(148, 163, 184, 0.15)',
                fontSize: '0.7rem',
                fontWeight: 600,
                px: 1.5,
                py: 0.5,
                '&.Mui-selected': {
                  color: '#00d4ff',
                  backgroundColor: 'rgba(0, 212, 255, 0.1)',
                  borderColor: 'rgba(0, 212, 255, 0.3)',
                },
              },
            }}
          >
            {TIME_RANGES.map((t) => (
              <ToggleButton key={t.value} value={t.value}>
                {t.label}
              </ToggleButton>
            ))}
          </ToggleButtonGroup>
        </Box>

        <ResponsiveContainer width="100%" height={350}>
          <AreaChart data={data} margin={{ top: 5, right: 10, bottom: 5, left: -10 }}>
            <defs>
              {deviceKeys.map((key, idx) => (
                <linearGradient key={key} id={`temp-grad-${idx}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={CHART_COLORS[idx % CHART_COLORS.length]} stopOpacity={0.25} />
                  <stop offset="100%" stopColor={CHART_COLORS[idx % CHART_COLORS.length]} stopOpacity={0} />
                </linearGradient>
              ))}
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.06)" />
            <XAxis
              dataKey="timestamp"
              tickFormatter={formatXAxis}
              stroke="#475569"
              tick={{ fontSize: 10, fill: '#475569' }}
              axisLine={{ stroke: 'rgba(148,163,184,0.08)' }}
              tickLine={false}
            />
            <YAxis
              stroke="#475569"
              tick={{ fontSize: 10, fill: '#475569' }}
              axisLine={{ stroke: 'rgba(148,163,184,0.08)' }}
              tickLine={false}
              tickFormatter={(v) => `${v}°`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: '0.75rem', paddingTop: '8px' }} iconType="circle" iconSize={8} />
            {deviceKeys.map((key, idx) => (
              <Area
                key={key}
                type="monotone"
                dataKey={key}
                stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                strokeWidth={2}
                fill={`url(#temp-grad-${idx})`}
                dot={false}
                activeDot={{ r: 4, strokeWidth: 2, fill: '#0a0e1a' }}
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default TemperatureChart;
