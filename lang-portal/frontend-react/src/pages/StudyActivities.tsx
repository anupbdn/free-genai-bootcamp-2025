import React, { useEffect, useState } from 'react';
import { 
  Container, Typography, Grid, Card, CardMedia, CardContent, 
  CardActions, Button, CircularProgress, Alert 
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { getStudyActivities } from '../services/api';
import { StudyActivity } from '../types';

const StudyActivities: React.FC = () => {
  const [activities, setActivities] = useState<StudyActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    getStudyActivities()
      .then(response => {
        setActivities(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching activities:', error);
        setError('Failed to load study activities');
        setLoading(false);
      });
  }, []);

  const handleLaunch = (id: number) => {
    navigate(`/study_activities/${id}/launch`);
  };

  const handleView = (id: number) => {
    navigate(`/study_activities/${id}`);
  };

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
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container>
      <Typography variant="h4" gutterBottom sx={{ mt: 4 }}>
        Study Activities
      </Typography>
      <Grid container spacing={4}>
        {activities.map((activity) => (
          <Grid item xs={12} sm={6} md={4} key={activity.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              {activity.thumbnail_url && (
                <CardMedia
                  component="img"
                  height="140"
                  image={activity.thumbnail_url}
                  alt={activity.name}
                />
              )}
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography gutterBottom variant="h5" component="h2">
                  {activity.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {activity.description || 'No description available'}
                </Typography>
                <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                  Type: {activity.type}
                </Typography>
              </CardContent>
              <CardActions sx={{ justifyContent: 'space-between', p: 2 }}>
                <Button 
                  size="small" 
                  onClick={() => handleView(activity.id)}
                >
                  View Details
                </Button>
                <Button 
                  size="small" 
                  variant="contained" 
                  onClick={() => handleLaunch(activity.id)}
                >
                  Launch Activity
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default StudyActivities; 