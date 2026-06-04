import React, { useState, useEffect } from 'react';
import { Box, Grid, Card, CardContent, Typography, CircularProgress, Button } from '@mui/material';
import { Refresh as RefreshIcon, TrendingUp, Warning, DevicesOther, CheckCircle } from '@mui/icons-material';
import api from '../api/axios';
import RealtimeChart from '../components/Dashboard/RealtimeChart';
import DeviceStatusGrid from '../components/Dashboard/DeviceStatusGrid';
import TemperatureChart from '../components/Charts/TemperatureChart';
import VibrationChart from '../components/Charts/VibrationChart';
import DeviceUtilizationChart from '../components/Charts/DeviceUtilizationChart';

// A simple StatCard component for the dashboard
const StatCard = ({ title, value, icon, color }: { title: string, value: string | number, icon: React.ReactNode, color: string }) => (
  <Card>
    <CardContent sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', p: 3 }}>
      <Box>
        <Typography color="textSecondary" gutterBottom variant="overline" sx={{ letterSpacing: 1, fontWeight: 600 }}>
          {title}
        </Typography>
        <Typography variant="h4" color="textPrimary" fontWeight="700">
          {value}
        </Typography>
      </Box>
      <Box sx={{ 
        backgroundColor: `${color}15`, 
        p: 2, 
        borderRadius: '50%',
        display: 'flex',
        color: color,
        boxShadow: `0 0 10px ${color}10`
      }}>
        {icon}
      </Box>
    </CardContent>
  </Card>
);

const Dashboard = () => {
  const [summary, setSummary] = useState<any>(null);
  const [devices, setDevices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const summaryRes = await api.get('/analytics/');
      setSummary(summaryRes.data);
      
      const devicesRes = await api.get('/devices/');
      setDevices(devicesRes.data.items);
    } catch (error) {
      console.error("Error fetching dashboard data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  if (loading && !summary) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">
          Overview
        </Typography>
        <Button 
          startIcon={<RefreshIcon />} 
          variant="outlined" 
          onClick={fetchSummary}
          disabled={loading}
          sx={{ borderRadius: '8px' }}
        >
          Refresh Data
        </Button>
      </Box>

      {summary && (
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard 
              title="Total Devices" 
              value={summary.total_devices} 
              icon={<DevicesOther fontSize="large" />} 
              color="#2196f3" 
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard 
              title="Online Devices" 
              value={summary.online_devices} 
              icon={<CheckCircle fontSize="large" />} 
              color="#4caf50" 
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard 
              title="Alerts (24h)" 
              value={summary.alerts_24h} 
              icon={<Warning fontSize="large" />} 
              color="#f44336" 
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard 
              title="Avg Health Score" 
              value={`${summary.average_health_score}%`} 
              icon={<TrendingUp fontSize="large" />} 
              color="#ff9800" 
            />
          </Grid>
        </Grid>
      )}
      
      {/* Real-time Ingestion Metrics */}
      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} lg={8}>
          <RealtimeChart />
        </Grid>
        <Grid item xs={12} lg={4}>
          <DeviceStatusGrid devices={devices} />
        </Grid>
      </Grid>

      {/* Historical Telemetry Analytics */}
      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} lg={6}>
          <TemperatureChart />
        </Grid>
        <Grid item xs={12} lg={6}>
          <VibrationChart />
        </Grid>
      </Grid>

      {/* Operational Utilization */}
      <Grid container spacing={3} sx={{ mt: 1, mb: 3 }}>
        <Grid item xs={12}>
          <DeviceUtilizationChart />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
