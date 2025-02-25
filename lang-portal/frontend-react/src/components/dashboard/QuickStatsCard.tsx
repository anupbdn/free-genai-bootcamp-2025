import React from 'react';
import { Card, CardContent, Typography, Grid } from '@mui/material';
import { QuickStatsCardProps } from '../../types';

export const QuickStatsCard: React.FC<QuickStatsCardProps> = ({ stats }) => {
  if (!stats) return null;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Quick Stats
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Success Rate
            </Typography>
            <Typography variant="h6">
              {stats.success_rate}%
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Study Sessions
            </Typography>
            <Typography variant="h6">
              {stats.total_study_sessions}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Active Groups
            </Typography>
            <Typography variant="h6">
              {stats.total_active_groups}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Study Streak
            </Typography>
            <Typography variant="h6">
              {stats.study_streak_days} days
            </Typography>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}; 