import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Avatar,
  Divider,
  IconButton,
  Tooltip,
  Chip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Memory as DevicesIcon,
  Analytics as AnalyticsIcon,
  NotificationsActive as AlertsIcon,
  Assessment as ReportsIcon,
  Logout as LogoutIcon,
  FiberManualRecord as DotIcon,
} from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';
import { SIDEBAR_WIDTH } from '../../utils/constants';
import { keyframes } from '@mui/system';

const shimmer = keyframes`
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
`;

const glow = keyframes`
  0%, 100% { box-shadow: 0 0 5px rgba(0, 212, 255, 0.2); }
  50% { box-shadow: 0 0 15px rgba(0, 212, 255, 0.4); }
`;

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  { label: 'Dashboard', path: '/', icon: <DashboardIcon /> },
  { label: 'Devices', path: '/devices', icon: <DevicesIcon /> },
  { label: 'Analytics', path: '/analytics', icon: <AnalyticsIcon /> },
  { label: 'Alerts', path: '/alerts', icon: <AlertsIcon /> },
  { label: 'Reports', path: '/reports', icon: <ReportsIcon /> },
];

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Box
      sx={{
        width: SIDEBAR_WIDTH,
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        background: 'rgba(17, 24, 39, 0.8)',
        backdropFilter: 'blur(24px)',
        borderRight: '1px solid rgba(148, 163, 184, 0.06)',
        display: 'flex',
        flexDirection: 'column',
        zIndex: 1200,
        '&::after': {
          content: '""',
          position: 'absolute',
          top: 0,
          right: 0,
          width: '1px',
          height: '100%',
          background:
            'linear-gradient(180deg, transparent 0%, rgba(0, 212, 255, 0.15) 30%, rgba(124, 58, 237, 0.15) 70%, transparent 100%)',
        },
      }}
    >
      {/* Logo Section */}
      <Box sx={{ p: 3, pb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              animation: `${glow} 3s ease-in-out infinite`,
            }}
          >
            <Typography sx={{ fontSize: '1.2rem', fontWeight: 800, color: '#fff' }}>SF</Typography>
          </Box>
          <Box>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 800,
                fontSize: '1rem',
                background: 'linear-gradient(135deg, #00d4ff 0%, #7c3aed 50%, #f43f5e 100%)',
                backgroundSize: '200% auto',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                animation: `${shimmer} 4s linear infinite`,
              }}
            >
              Smart Factory
            </Typography>
            <Typography
              sx={{
                fontSize: '0.65rem',
                fontWeight: 600,
                color: '#64748b',
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
              }}
            >
              IoT Platform
            </Typography>
          </Box>
        </Box>
      </Box>

      <Divider sx={{ borderColor: 'rgba(148, 163, 184, 0.06)', mx: 2 }} />

      {/* Navigation */}
      <Box sx={{ flex: 1, py: 2, px: 1.5 }}>
        <Typography
          sx={{
            fontSize: '0.65rem',
            fontWeight: 700,
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: '#475569',
            px: 1.5,
            mb: 1,
          }}
        >
          Navigation
        </Typography>
        <List sx={{ p: 0 }}>
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <ListItemButton
                key={item.path}
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: '10px',
                  mb: 0.5,
                  py: 1.2,
                  px: 1.5,
                  position: 'relative',
                  overflow: 'hidden',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  ...(isActive
                    ? {
                        background: 'rgba(0, 212, 255, 0.08)',
                        '&::before': {
                          content: '""',
                          position: 'absolute',
                          left: 0,
                          top: '15%',
                          bottom: '15%',
                          width: 3,
                          borderRadius: '0 3px 3px 0',
                          background: 'linear-gradient(180deg, #00d4ff, #7c3aed)',
                        },
                      }
                    : {
                        '&:hover': {
                          background: 'rgba(148, 163, 184, 0.05)',
                          '& .MuiListItemIcon-root': {
                            color: '#00d4ff',
                          },
                        },
                      }),
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 40,
                    color: isActive ? '#00d4ff' : '#64748b',
                    transition: 'color 0.3s ease',
                    '& .MuiSvgIcon-root': {
                      fontSize: '1.3rem',
                    },
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{
                    fontSize: '0.875rem',
                    fontWeight: isActive ? 600 : 500,
                    color: isActive ? '#e2e8f0' : '#94a3b8',
                  }}
                />
                {isActive && (
                  <DotIcon
                    sx={{
                      fontSize: 8,
                      color: '#00d4ff',
                      filter: 'drop-shadow(0 0 4px #00d4ff)',
                    }}
                  />
                )}
              </ListItemButton>
            );
          })}
        </List>
      </Box>

      <Divider sx={{ borderColor: 'rgba(148, 163, 184, 0.06)', mx: 2 }} />

      {/* User Section */}
      <Box sx={{ p: 2 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1.5,
            p: 1.5,
            borderRadius: '12px',
            background: 'rgba(15, 23, 42, 0.5)',
            border: '1px solid rgba(148, 163, 184, 0.06)',
          }}
        >
          <Avatar
            sx={{
              width: 36,
              height: 36,
              background: 'linear-gradient(135deg, #00d4ff, #7c3aed)',
              fontSize: '0.85rem',
              fontWeight: 700,
            }}
          >
            {user?.username?.charAt(0).toUpperCase() || 'U'}
          </Avatar>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography
              sx={{
                fontSize: '0.8rem',
                fontWeight: 600,
                color: '#e2e8f0',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {user?.username || 'User'}
            </Typography>
            <Chip
              label={user?.role || 'Operator'}
              size="small"
              sx={{
                height: 18,
                fontSize: '0.6rem',
                fontWeight: 700,
                backgroundColor: 'rgba(0, 212, 255, 0.1)',
                color: '#00d4ff',
                border: '1px solid rgba(0, 212, 255, 0.2)',
                '& .MuiChip-label': { px: 0.8, py: 0 },
              }}
            />
          </Box>
          <Tooltip title="Logout">
            <IconButton
              onClick={handleLogout}
              size="small"
              sx={{
                color: '#64748b',
                '&:hover': {
                  color: '#f43f5e',
                  backgroundColor: 'rgba(244, 63, 94, 0.1)',
                },
              }}
            >
              <LogoutIcon sx={{ fontSize: '1.1rem' }} />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
    </Box>
  );
};

export default Sidebar;
