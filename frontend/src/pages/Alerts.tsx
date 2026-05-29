import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Paper, Table, TableBody, TableCell, 
  TableContainer, TableHead, TableRow, Chip, CircularProgress, 
  Button, Pagination
} from '@mui/material';
import { CheckCircle as AckIcon } from '@mui/icons-material';
import api from '../api/axios';
import { format } from 'date-fns';

const Alerts = () => {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const rowsPerPage = 15;

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const skip = (page - 1) * rowsPerPage;
      const response = await api.get(`/alerts/?skip=${skip}&limit=${rowsPerPage}`);
      setAlerts(response.data.items);
      setTotal(response.data.total);
    } catch (error) {
      console.error("Error fetching alerts", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [page]);

  const handleAcknowledge = async (id: number) => {
    try {
      await api.put(`/alerts/${id}/acknowledge`, { is_acknowledged: true });
      fetchAlerts(); // Refresh list
    } catch (error) {
      console.error("Error acknowledging alert", error);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toUpperCase()) {
      case 'INFO': return 'info';
      case 'WARNING': return 'warning';
      case 'CRITICAL': return 'error';
      default: return 'default';
    }
  };

  if (loading && alerts.length === 0) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;
  }

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Alerts
      </Typography>
      
      <TableContainer component={Paper} sx={{ mt: 3, borderRadius: 2 }}>
        <Table size="small">
          <TableHead>
            <TableRow sx={{ backgroundColor: 'rgba(255,255,255,0.05)' }}>
              <TableCell>Time</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Device ID</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Message</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {alerts.map((alert) => (
              <TableRow key={alert.id} hover>
                <TableCell>{format(new Date(alert.created_at), 'yyyy-MM-dd HH:mm:ss')}</TableCell>
                <TableCell>
                  <Chip 
                    label={alert.severity} 
                    color={getSeverityColor(alert.severity) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell sx={{ fontFamily: 'monospace' }}>{alert.device_id}</TableCell>
                <TableCell>{alert.alert_type}</TableCell>
                <TableCell>{alert.message}</TableCell>
                <TableCell>
                  {alert.is_acknowledged ? (
                    <Typography variant="body2" color="success.main" display="flex" alignItems="center">
                      <AckIcon fontSize="small" sx={{ mr: 0.5 }} /> Ack by {alert.acknowledged_by}
                    </Typography>
                  ) : (
                    <Typography variant="body2" color="error.main">Unacknowledged</Typography>
                  )}
                </TableCell>
                <TableCell align="right">
                  {!alert.is_acknowledged && (
                    <Button 
                      size="small" 
                      variant="outlined" 
                      color="primary"
                      onClick={() => handleAcknowledge(alert.id)}
                    >
                      Acknowledge
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      
      {total > rowsPerPage && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Pagination 
            count={Math.ceil(total / rowsPerPage)} 
            page={page} 
            onChange={(_, value) => setPage(value)} 
            color="primary" 
          />
        </Box>
      )}
    </Box>
  );
};

export default Alerts;
