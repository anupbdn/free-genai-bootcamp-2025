import React, { useEffect, useState } from 'react';
import { 
  Container, Typography, Grid, Card, CardContent, 
  CardMedia, Button, CircularProgress 
} from '@mui/material';
import { getStudyActivities } from '../services/api';
import { StudyActivity } from '../types';

const Launchpad: React.FC = () => {
  const [activities, setActivities] = useState<StudyActivity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getStudyActivities()
      .then(response => {
        setActivities(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching activities:', error);
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

  return (
    <Container>
      <Typography variant="h4" gutterBottom sx={{ mt: 4 }}>
        Learning Activities
      </Typography>
      <Grid container spacing={4}>
        {activities.map((activity) => (
          <Grid item xs={12} sm={6} md={4} key={activity.id}>
            <Card>
              {activity.thumbnail_url && (
                <CardMedia
                  component="img"
                  height="140"
                  image={activity.thumbnail_url}
                  alt={activity.name}
                />
              )}
              <CardContent>
                <Typography gutterBottom variant="h5" component="div">
                  {activity.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {activity.description}
                </Typography>
                <Button 
                  variant="contained" 
                  fullWidth 
                  sx={{ mt: 2 }}
                >
                  Start Activity
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default Launchpad;