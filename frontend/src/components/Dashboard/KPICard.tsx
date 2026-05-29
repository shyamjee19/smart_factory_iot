import React from 'react';
import { Card, CardContent, Box, Typography } from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';
import { keyframes } from '@mui/system';

const countUp = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

interface KPICardProps {
  title: string;
  value: number | string;
  icon: React.ReactNode;
  color: string;
  trend?: number;
  trendLabel?: string;
  suffix?: string;
}

const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  icon,
  color,
  trend,
  trendLabel,
  suffix,
}) => {
  const isPositiveTrend = trend !== undefined && trend >= 0;

  return (
    <Card
      sx={{
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          background: `linear-gradient(90deg, ${color}, ${color}80, transparent)`,
        },
        '&::after': {
          content: '""',
          position: 'absolute',
          top: -40,
          right: -40,
          width: 120,
          height: 120,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${color}08 0%, transparent 70%)`,
        },
      }}
    >
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box sx={{ flex: 1 }}>
            <Typography
              sx={{
                fontSize: '0.75rem',
                fontWeight: 600,
                color: '#64748b',
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                mb: 1,
              }}
            >
              {title}
            </Typography>
            <Typography
              sx={{
                fontSize: '2rem',
                fontWeight: 800,
                color: '#e2e8f0',
                lineHeight: 1,
                animation: `${countUp} 0.6s ease-out`,
              }}
            >
              {value}
              {suffix && (
                <Typography
                  component="span"
                  sx={{ fontSize: '0.9rem', fontWeight: 500, color: '#94a3b8', ml: 0.5 }}
                >
                  {suffix}
                </Typography>
              )}
            </Typography>
            {trend !== undefined && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 1 }}>
                {isPositiveTrend ? (
                  <TrendingUp sx={{ fontSize: '0.9rem', color: '#10b981' }} />
                ) : (
                  <TrendingDown sx={{ fontSize: '0.9rem', color: '#f43f5e' }} />
                )}
                <Typography
                  sx={{
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    color: isPositiveTrend ? '#10b981' : '#f43f5e',
                  }}
                >
                  {Math.abs(trend).toFixed(1)}%
                </Typography>
                {trendLabel && (
                  <Typography sx={{ fontSize: '0.7rem', color: '#475569' }}>
                    {trendLabel}
                  </Typography>
                )}
              </Box>
            )}
          </Box>
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: '14px',
              background: `${color}15`,
              border: `1px solid ${color}25`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: color,
              flexShrink: 0,
              '& .MuiSvgIcon-root': {
                fontSize: '1.4rem',
              },
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default KPICard;
