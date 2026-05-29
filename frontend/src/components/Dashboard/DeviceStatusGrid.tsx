import React from 'react';
import { Card, CardContent, Box, Typography, Grid, LinearProgress } from '@mui/material';
import { FiberManualRecord as DotIcon } from '@mui/icons-material';
import { getStatusColor, getHealthColor, formatRelativeTime } from '../../utils/formatters';
import type { Device } from '../../types';

interface DeviceStatusGridProps {
  devices: Device[];
}

const DeviceStatusGrid: React.FC<DeviceStatusGridProps> = ({ devices }) => {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 3, '&:last-child': { pb: 2 } }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, fontSize: '1rem' }}>
              Device Status
            </Typography>
            <Typography sx={{ fontSize: '0.8rem', color: '#64748b' }}>
              Fleet overview
            </Typography>
          </Box>
          <Typography sx={{ fontSize: '0.75rem', color: '#64748b' }}>
            {devices.filter((d) => d.status === 'online').length}/{devices.length} online
          </Typography>
        </Box>

        <Box sx={{ maxHeight: 380, overflowY: 'auto', pr: 0.5 }}>
          <Grid container spacing={1.5}>
            {devices.slice(0, 12).map((device) => {
              const statusColor = getStatusColor(device.status);
              const healthColor = getHealthColor(device.health_score);

              return (
                <Grid item xs={6} key={device.id}>
                  <Box
                    sx={{
                      p: 1.5,
                      borderRadius: '10px',
                      background: 'rgba(15, 23, 42, 0.5)',
                      border: '1px solid rgba(148, 163, 184, 0.06)',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        border: `1px solid ${statusColor}30`,
                        background: 'rgba(15, 23, 42, 0.8)',
                      },
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.8 }}>
                      <Typography
                        sx={{
                          fontSize: '0.78rem',
                          fontWeight: 600,
                          color: '#e2e8f0',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                          maxWidth: '70%',
                        }}
                      >
                        {device.name}
                      </Typography>
                      <DotIcon
                        sx={{
                          fontSize: 10,
                          color: statusColor,
                          filter: `drop-shadow(0 0 3px ${statusColor})`,
                        }}
                      />
                    </Box>
                    <Typography sx={{ fontSize: '0.65rem', color: '#475569', mb: 0.8 }}>
                      {device.type}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={device.health_score}
                        sx={{
                          flex: 1,
                          height: 4,
                          borderRadius: 2,
                          backgroundColor: 'rgba(148, 163, 184, 0.08)',
                          '& .MuiLinearProgress-bar': {
                            borderRadius: 2,
                            backgroundColor: healthColor,
                          },
                        }}
                      />
                      <Typography sx={{ fontSize: '0.65rem', fontWeight: 600, color: healthColor, minWidth: 28 }}>
                        {device.health_score}%
                      </Typography>
                    </Box>
                    <Typography sx={{ fontSize: '0.6rem', color: '#374151', mt: 0.5 }}>
                      {formatRelativeTime(device.last_seen)}
                    </Typography>
                  </Box>
                </Grid>
              );
            })}
          </Grid>
        </Box>
      </CardContent>
    </Card>
  );
};

export default DeviceStatusGrid;
