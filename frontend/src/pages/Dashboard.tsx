import React, { useState, useEffect } from 'react';
import { Box, Grid, Card, CardContent, Typography, CircularProgress, IconButton, Button } from '@mui/material';
import { Refresh as RefreshIcon, TrendingUp, Warning, DevicesOther, CheckCircle } from '@mui/icons-material';
import api from '../api/axios';

// A simple StatCard component for the dashboard
const StatCard = ({ title, value, icon, color }: { title: string, value: string | number, icon: React.ReactNode, color: string }) => (
  <Card>
    <CardContent sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <Box>
        <Typography color="textSecondary" gutterBottom variant="overline">
          {title}
        </Typography>
        <Typography variant="h4" color="textPrimary">
          {value}
        </Typography>
      </Box>
      <Box sx={{ 
        backgroundColor: `${color}20`, 
        p: 1.5, 
        borderRadius: '50%',
        display: 'flex',
        color: color
      }}>
        {icon}
      </Box>
    </CardContent>
  </Card>
);

const Dashboard = () => {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const response = await api.get('/analytics/');
      setSummary(response.data);
    } catch (error) {
      console.error("Error fetching summary", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
    // Optional: setup polling here
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
        >
          Refresh
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
      
      {/* Placeholders for Charts */}
      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} lg={8}>
          <Card sx={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography color="textSecondary">Temperature Trend Chart (Placeholder)</Typography>
          </Card>
        </Grid>
        <Grid item xs={12} lg={4}>
          <Card sx={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography color="textSecondary">Device Health Distribution (Placeholder)</Typography>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
