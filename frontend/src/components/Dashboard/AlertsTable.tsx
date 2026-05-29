import React from 'react';
import {
  Card,
  CardContent,
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import StatusBadge from '../Common/StatusBadge';
import { formatTimestamp } from '../../utils/formatters';
import type { Alert } from '../../types';

interface AlertsTableProps {
  alerts: Alert[];
  maxRows?: number;
}

const AlertsTable: React.FC<AlertsTableProps> = ({ alerts, maxRows = 8 }) => {
  const displayAlerts = alerts.slice(0, maxRows);

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 3, '&:last-child': { pb: 2 } }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, fontSize: '1rem' }}>
              Recent Alerts
            </Typography>
            <Typography sx={{ fontSize: '0.8rem', color: '#64748b' }}>
              Latest system notifications
            </Typography>
          </Box>
          <Box
            sx={{
              px: 1.5,
              py: 0.3,
              borderRadius: '8px',
              background: 'rgba(244, 63, 94, 0.1)',
              border: '1px solid rgba(244, 63, 94, 0.2)',
            }}
          >
            <Typography sx={{ fontSize: '0.7rem', fontWeight: 700, color: '#f43f5e' }}>
              {alerts.filter((a) => !a.acknowledged).length} Active
            </Typography>
          </Box>
        </Box>

        <TableContainer sx={{ maxHeight: 380, overflowY: 'auto' }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Severity</TableCell>
                <TableCell>Device</TableCell>
                <TableCell>Message</TableCell>
                <TableCell>Time</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {displayAlerts.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} align="center" sx={{ py: 4, border: 'none' }}>
                    <Typography sx={{ color: '#475569', fontSize: '0.85rem' }}>
                      No recent alerts
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                displayAlerts.map((alert) => (
                  <TableRow key={alert.id}>
                    <TableCell>
                      <StatusBadge label={alert.severity} type="severity" />
                    </TableCell>
                    <TableCell>
                      <Typography sx={{ fontSize: '0.8rem', fontWeight: 500 }}>
                        {alert.device_name || alert.device_id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography
                        sx={{
                          fontSize: '0.8rem',
                          color: '#94a3b8',
                          maxWidth: 220,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {alert.message}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography sx={{ fontSize: '0.75rem', color: '#64748b' }}>
                        {formatTimestamp(alert.created_at, 'HH:mm:ss')}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
};

export default AlertsTable;
