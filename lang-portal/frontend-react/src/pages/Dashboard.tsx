import React, { useEffect, useState } from 'react';
import { getLastStudySession, getDashboardStats, getStudyProgress } from '../services/api';
import { StudySession, QuickStats, StudyProgress } from '../types';
import { Container, Typography, Card, CardContent, CircularProgress, Alert, Grid, Button } from '@mui/material';
import { Link } from 'react-router-dom';
import { LastSessionCard } from '../components/dashboard/LastSessionCard';
import { StudyProgressCard } from '../components/dashboard/StudyProgressCard';
import { QuickStatsCard } from '../components/dashboard/QuickStatsCard';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<QuickStats | null>(null);
  const [progress, setProgress] = useState<StudyProgress | null>(null);
  const [session, setSession] = useState<StudySession | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch all dashboard data
    Promise.all([
      getLastStudySession(),
      getDashboardStats(),
      getStudyProgress()
    ]).then(([sessionRes, statsRes, progressRes]) => {
      setSession(sessionRes.data);
      setStats(statsRes.data);
      setProgress(progressRes.data);
      setLoading(false);
    })
    .catch((error) => {
      console.error('Error fetching dashboard data:', error);
      setError(error.message || 'Failed to load dashboard data');
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="error">
          {error}
        </Alert>
      </Container>
    );
  }

  if (!session) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="info">
          No study sessions found. Start learning to see your progress!
        </Alert>
      </Container>
    );
  }

  return (
    <Container>
      <Grid container spacing={3}>
        {/* Last Study Session */}
        <Grid item xs={12}>
          <LastSessionCard session={session} />
        </Grid>

        {/* Study Progress */}
        <Grid item xs={12} md={6}>
          <StudyProgressCard progress={progress} />
        </Grid>

        {/* Quick Stats */}
        <Grid item xs={12} md={6}>
          <QuickStatsCard stats={stats} />
        </Grid>

        {/* Start Studying Button */}
        <Grid item xs={12}>
          <Button
            variant="contained"
            size="large"
            fullWidth
            component={Link}
            to="/study_activities"
          >
            Start Studying
          </Button>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;