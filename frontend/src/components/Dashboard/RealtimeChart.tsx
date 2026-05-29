import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, Box, Typography } from '@mui/material';
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
import { useStore } from '../../store';
import { format } from 'date-fns';
import { CHART_COLORS } from '../../utils/constants';

interface DataPoint {
  time: string;
  timestamp: number;
  [key: string]: string | number;
}

const MAX_DATA_POINTS = 30;

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
        minWidth: 160,
      }}
    >
      <Typography sx={{ fontSize: '0.7rem', color: '#64748b', mb: 0.5 }}>{label}</Typography>
      {payload.map((entry, idx) => (
        <Box key={idx} sx={{ display: 'flex', justifyContent: 'space-between', gap: 2, py: 0.2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: entry.color,
              }}
            />
            <Typography sx={{ fontSize: '0.75rem', color: '#94a3b8' }}>{entry.name}</Typography>
          </Box>
          <Typography sx={{ fontSize: '0.75rem', fontWeight: 600, color: '#e2e8f0' }}>
            {typeof entry.value === 'number' ? entry.value.toFixed(1) : entry.value}°C
          </Typography>
        </Box>
      ))}
    </Box>
  );
};

const RealtimeChart: React.FC = () => {
  const liveData = useStore((s) => s.liveData);
  const devices = useStore((s) => s.devices);
  const [chartData, setChartData] = useState<DataPoint[]>([]);
  const deviceKeys = useRef<Set<string>>(new Set());

  useEffect(() => {
    if (Object.keys(liveData).length === 0) return;

    const now = new Date();
    const point: DataPoint = {
      time: format(now, 'HH:mm:ss'),
      timestamp: now.getTime(),
    };

    Object.entries(liveData).forEach(([deviceId, data]) => {
      const device = devices.find((d) => d.device_id === deviceId);
      const label = device?.name || deviceId;
      point[label] = data.temperature;
      deviceKeys.current.add(label);
    });

    setChartData((prev) => {
      const updated = [...prev, point];
      return updated.slice(-MAX_DATA_POINTS);
    });
  }, [liveData, devices]);

  // Generate demo data if no live data
  useEffect(() => {
    if (Object.keys(liveData).length > 0) return;

    const demoDevices = ['CNC-001', 'Robot-002', 'Conv-003', 'Press-004'];
    demoDevices.forEach((d) => deviceKeys.current.add(d));

    const initialData: DataPoint[] = Array.from({ length: 20 }, (_, i) => {
      const t = new Date(Date.now() - (20 - i) * 5000);
      const point: DataPoint = {
        time: format(t, 'HH:mm:ss'),
        timestamp: t.getTime(),
      };
      demoDevices.forEach((device, idx) => {
        point[device] = 40 + idx * 5 + Math.sin(i * 0.3 + idx) * 8 + Math.random() * 3;
      });
      return point;
    });
    setChartData(initialData);

    const interval = setInterval(() => {
      const now = new Date();
      const point: DataPoint = {
        time: format(now, 'HH:mm:ss'),
        timestamp: now.getTime(),
      };
      demoDevices.forEach((device, idx) => {
        const prev = chartData.length > 0 ? (chartData[chartData.length - 1][device] as number) || 50 : 50;
        point[device] = prev + (Math.random() - 0.5) * 4;
      });
      setChartData((prev) => [...prev.slice(-MAX_DATA_POINTS + 1), point]);
    }, 3000);

    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const keys = Array.from(deviceKeys.current);

  return (
    <Card>
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, fontSize: '1rem' }}>
              Real-Time Temperature
            </Typography>
            <Typography sx={{ fontSize: '0.8rem', color: '#64748b' }}>
              Live sensor data from active devices
            </Typography>
          </Box>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 0.8,
              px: 1.5,
              py: 0.5,
              borderRadius: '8px',
              background: 'rgba(16, 185, 129, 0.1)',
              border: '1px solid rgba(16, 185, 129, 0.2)',
            }}
          >
            <Box
              sx={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                backgroundColor: '#10b981',
                boxShadow: '0 0 8px #10b981',
                animation: 'pulse 2s infinite',
                '@keyframes pulse': {
                  '0%, 100%': { opacity: 1 },
                  '50%': { opacity: 0.5 },
                },
              }}
            />
            <Typography sx={{ fontSize: '0.7rem', fontWeight: 600, color: '#10b981' }}>
              LIVE
            </Typography>
          </Box>
        </Box>

        <ResponsiveContainer width="100%" height={320}>
          <AreaChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: -10 }}>
            <defs>
              {keys.map((key, idx) => (
                <linearGradient key={key} id={`gradient-${idx}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={CHART_COLORS[idx % CHART_COLORS.length]} stopOpacity={0.3} />
                  <stop offset="100%" stopColor={CHART_COLORS[idx % CHART_COLORS.length]} stopOpacity={0} />
                </linearGradient>
              ))}
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.06)" />
            <XAxis
              dataKey="time"
              stroke="#475569"
              tick={{ fontSize: 11, fill: '#475569' }}
              axisLine={{ stroke: 'rgba(148,163,184,0.08)' }}
              tickLine={false}
            />
            <YAxis
              stroke="#475569"
              tick={{ fontSize: 11, fill: '#475569' }}
              axisLine={{ stroke: 'rgba(148,163,184,0.08)' }}
              tickLine={false}
              domain={['auto', 'auto']}
              tickFormatter={(v) => `${v}°`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: '0.75rem', paddingTop: '8px' }}
              iconType="circle"
              iconSize={8}
            />
            {keys.map((key, idx) => (
              <Area
                key={key}
                type="monotone"
                dataKey={key}
                stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                strokeWidth={2}
                fill={`url(#gradient-${idx})`}
                dot={false}
                activeDot={{
                  r: 5,
                  stroke: CHART_COLORS[idx % CHART_COLORS.length],
                  strokeWidth: 2,
                  fill: '#0a0e1a',
                }}
                animationDuration={500}
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default RealtimeChart;
