import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import { keyframes } from '@mui/system';

const pulse = keyframes`
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.05); }
`;

const rotate = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

interface LoadingSpinnerProps {
  message?: string;
  size?: number;
  fullScreen?: boolean;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = 'Loading...',
  size = 48,
  fullScreen = false,
}) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 2.5,
        ...(fullScreen
          ? {
              position: 'fixed',
              inset: 0,
              backgroundColor: 'rgba(10, 14, 26, 0.9)',
              backdropFilter: 'blur(8px)',
              zIndex: 9999,
            }
          : {
              py: 8,
              minHeight: 200,
            }),
      }}
    >
      <Box sx={{ position: 'relative', display: 'inline-flex' }}>
        <CircularProgress
          size={size}
          thickness={2}
          sx={{
            color: '#00d4ff',
            animation: `${rotate} 1.4s linear infinite`,
          }}
        />
        <CircularProgress
          size={size}
          thickness={2}
          variant="determinate"
          value={30}
          sx={{
            color: '#7c3aed',
            position: 'absolute',
            left: 0,
            animation: `${rotate} 2s linear infinite reverse`,
            opacity: 0.6,
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: size * 0.25,
            height: size * 0.25,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #00d4ff, #7c3aed)',
            animation: `${pulse} 1.5s ease-in-out infinite`,
          }}
        />
      </Box>
      {message && (
        <Typography
          variant="body2"
          sx={{
            color: '#94a3b8',
            fontWeight: 500,
            animation: `${pulse} 2s ease-in-out infinite`,
          }}
        >
          {message}
        </Typography>
      )}
    </Box>
  );
};

export default LoadingSpinner;
