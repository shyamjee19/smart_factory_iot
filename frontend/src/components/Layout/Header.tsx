import React from 'react';
import {
  Box,
  Typography,
  IconButton,
  Badge,
  InputBase,
  Tooltip,
  Chip,
} from '@mui/material';
import {
  NotificationsOutlined as NotifIcon,
  Search as SearchIcon,
  FiberManualRecord as DotIcon,
} from '@mui/icons-material';
import { SIDEBAR_WIDTH, HEADER_HEIGHT } from '../../utils/constants';
import { useStore } from '../../store';

interface HeaderProps {
  title: string;
  subtitle?: string;
}

const Header: React.FC<HeaderProps> = ({ title, subtitle }) => {
  const alerts = useStore((s) => s.alerts);
  const unacknowledgedCount = alerts.filter((a) => !a.acknowledged).length;

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: SIDEBAR_WIDTH,
        right: 0,
        height: HEADER_HEIGHT,
        background: 'rgba(10, 14, 26, 0.85)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(148, 163, 184, 0.06)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        px: 4,
        zIndex: 1100,
      }}
    >
      {/* Left - Page Title */}
      <Box>
        <Typography
          variant="h4"
          sx={{
            fontWeight: 700,
            fontSize: '1.4rem',
            color: '#e2e8f0',
            letterSpacing: '-0.01em',
          }}
        >
          {title}
        </Typography>
        {subtitle && (
          <Typography
            sx={{
              fontSize: '0.8rem',
              color: '#64748b',
              mt: 0.2,
            }}
          >
            {subtitle}
          </Typography>
        )}
      </Box>

      {/* Right - Search, Notifications, Status */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        {/* Search Bar */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            px: 2,
            py: 0.8,
            borderRadius: '10px',
            background: 'rgba(15, 23, 42, 0.6)',
            border: '1px solid rgba(148, 163, 184, 0.1)',
            transition: 'all 0.3s ease',
            minWidth: 200,
            '&:focus-within': {
              borderColor: 'rgba(0, 212, 255, 0.3)',
              boxShadow: '0 0 0 3px rgba(0, 212, 255, 0.05)',
            },
          }}
        >
          <SearchIcon sx={{ fontSize: '1.1rem', color: '#475569' }} />
          <InputBase
            placeholder="Search..."
            sx={{
              fontSize: '0.85rem',
              color: '#e2e8f0',
              '& ::placeholder': {
                color: '#475569',
                opacity: 1,
              },
            }}
          />
        </Box>

        {/* Connection Status */}
        <Chip
          icon={<DotIcon sx={{ fontSize: '8px !important', color: '#10b981 !important' }} />}
          label="Live"
          size="small"
          sx={{
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            color: '#10b981',
            border: '1px solid rgba(16, 185, 129, 0.2)',
            fontWeight: 600,
            fontSize: '0.7rem',
            height: 28,
            '& .MuiChip-icon': {
              ml: 0.5,
            },
          }}
        />

        {/* Notifications */}
        <Tooltip title={`${unacknowledgedCount} unread alerts`}>
          <IconButton
            sx={{
              color: '#94a3b8',
              position: 'relative',
              '&:hover': {
                color: '#00d4ff',
                backgroundColor: 'rgba(0, 212, 255, 0.08)',
              },
            }}
          >
            <Badge
              badgeContent={unacknowledgedCount}
              max={99}
              sx={{
                '& .MuiBadge-badge': {
                  backgroundColor: '#f43f5e',
                  color: '#fff',
                  fontSize: '0.65rem',
                  fontWeight: 700,
                  minWidth: 18,
                  height: 18,
                  boxShadow: '0 0 8px rgba(244, 63, 94, 0.4)',
                },
              }}
            >
              <NotifIcon sx={{ fontSize: '1.3rem' }} />
            </Badge>
          </IconButton>
        </Tooltip>
      </Box>
    </Box>
  );
};

export default Header;
