import React, { useState, useEffect } from 'react';
import { Card, CardContent, Box, Typography } from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { getDeviceHealth } from '../../api/endpoints';
import { getHealthColor } from '../../utils/formatters';
import type { DeviceHealth } from '../../types';

const CustomTooltip: React.FC<{
  active?: boolean;
  payload?: Array<{ payload: { device_name: string; uptime_percentage: number; health_score: number } }>;
}> = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
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
      <Typography sx={{ fontSize: '0.8rem', fontWeight: 600, color: '#e2e8f0', mb: 0.5 }}>
        {d.device_name}
      </Typography>
      <Typography sx={{ fontSize: '0.75rem', color: '#94a3b8' }}>
        Uptime: <strong style={{ color: '#e2e8f0' }}>{d.uptime_percentage?.toFixed(1)}%</strong>
      </Typography>
      <Typography sx={{ fontSize: '0.75rem', color: '#94a3b8' }}>
        Health: <strong style={{ color: getHealthColor(d.health_score) }}>{d.health_score}%</strong>
      </Typography>
    </Box>
  );
};

const DeviceUtilizationChart: React.FC = () => {
  const [data, setData] = useState<DeviceHealth[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await getDeviceHealth();
        setData(result);
      } catch {
        setData([]);
      }
    };
    fetchData();
  }, []);

  if (data.length === 0) {
    return (
      <Card>
        <CardContent sx={{ p: 3, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 356 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#e2e8f0', mb: 1 }}>
            No Device Utilization Data
          </Typography>
          <Typography variant="body2" sx={{ color: '#64748b', fontSize: '0.8rem' }} align="center">
            No health records have been logged in PostgreSQL for the active devices.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 700, fontSize: '1rem' }}>
            Device Utilization
          </Typography>
          <Typography sx={{ fontSize: '0.8rem', color: '#64748b' }}>
            Uptime percentage by device
          </Typography>
        </Box>

        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} layout="vertical" margin={{ top: 0, right: 10, bottom: 0, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.06)" horizontal={false} />
            <XAxis
              type="number"
              domain={[0, 100]}
              stroke="#475569"
              tick={{ fontSize: 10, fill: '#475569' }}
              axisLine={{ stroke: 'rgba(148,163,184,0.08)' }}
              tickLine={false}
              tickFormatter={(v) => `${v}%`}
            />
            <YAxis
              type="category"
              dataKey="device_name"
              width={110}
              stroke="#475569"
              tick={{ fontSize: 10, fill: '#94a3b8' }}
              axisLine={{ stroke: 'rgba(148,163,184,0.08)' }}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0, 212, 255, 0.03)' }} />
            <Bar dataKey="uptime_percentage" radius={[0, 6, 6, 0]} barSize={18}>
              {data.map((entry, idx) => (
                <Cell
                  key={idx}
                  fill={getHealthColor(entry.uptime_percentage)}
                  fillOpacity={0.8}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default DeviceUtilizationChart;
