import React from 'react';
import { Chip, type ChipProps } from '@mui/material';
import { getSeverityColor, getStatusColor } from '../../utils/formatters';

interface StatusBadgeProps {
  label: string;
  type?: 'severity' | 'status';
  size?: ChipProps['size'];
  variant?: 'filled' | 'outlined';
}

const StatusBadge: React.FC<StatusBadgeProps> = ({
  label,
  type = 'severity',
  size = 'small',
  variant = 'filled',
}) => {
  const color = type === 'severity' ? getSeverityColor(label) : getStatusColor(label);

  return (
    <Chip
      label={label.charAt(0).toUpperCase() + label.slice(1)}
      size={size}
      sx={{
        fontWeight: 700,
        fontSize: '0.7rem',
        letterSpacing: '0.03em',
        ...(variant === 'filled'
          ? {
              backgroundColor: `${color}20`,
              color: color,
              border: `1px solid ${color}40`,
            }
          : {
              backgroundColor: 'transparent',
              color: color,
              border: `1px solid ${color}60`,
            }),
        '& .MuiChip-label': {
          px: 1,
        },
      }}
    />
  );
};

export default StatusBadge;
