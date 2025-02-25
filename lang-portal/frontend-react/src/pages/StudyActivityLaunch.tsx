import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container, Typography, Card, CardContent, FormControl,
  InputLabel, Select, MenuItem, Button, Alert, CircularProgress,
  Box, SelectChangeEvent
} from '@mui/material';
import { getStudyActivity, getGroups, launchStudyActivity } from '../services/api';
import { StudyActivity, Group } from '../types';

const StudyActivityLaunch: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activity, setActivity] = useState<StudyActivity | null>(null);
  const [groups, setGroups] = useState<Group[]>([]);
  const [selectedGroup, setSelectedGroup] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [launching, setLaunching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      Promise.all([
        getStudyActivity(parseInt(id)),
        getGroups()
      ]).then(([activityRes, groupsRes]) => {
        setActivity(activityRes.data);
        setGroups(groupsRes.data);
        setLoading(false);
      }).catch(error => {
        console.error('Error fetching data:', error);
        setError('Failed to load launch data');
        setLoading(false);
      });
    }
  }, [id]);

  const handleGroupChange = (event: SelectChangeEvent) => {
    setSelectedGroup(event.target.value);
  };

  const handleLaunch = async () => {
    if (!id || !selectedGroup) return;

    setLaunching(true);
    try {
      const response = await launchStudyActivity(parseInt(id), {
        group_id: parseInt(selectedGroup)
      });
      // Open study activity in new tab
      window.open(`/study/${response.data.id}`, '_blank');
      // Navigate back to study sessions page
      navigate('/study_sessions');
    } catch (error) {
      console.error('Launch error:', error);
      setError('Failed to launch activity');
    } finally {
      setLaunching(false);
    }
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  if (!activity) {
    return (
      <Container>
        <Alert severity="error">Activity not found</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="sm">
      <Typography variant="h4" gutterBottom sx={{ mt: 4 }}>
        Launch Study Activity
      </Typography>

      <Card sx={{ mt: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {activity.name}
          </Typography>
          <Typography color="text.secondary" gutterBottom>
            {activity.description}
          </Typography>

          <Box sx={{ mt: 3 }}>
            <FormControl fullWidth>
              <InputLabel>Select Word Group</InputLabel>
              <Select
                value={selectedGroup}
                label="Select Word Group"
                onChange={handleGroupChange}
              >
                {groups.map((group) => (
                  <MenuItem key={group.id} value={group.id}>
                    {group.name} ({group.word_count} words)
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          <Button
            variant="contained"
            fullWidth
            size="large"
            sx={{ mt: 3 }}
            onClick={handleLaunch}
            disabled={!selectedGroup || launching}
          >
            {launching ? 'Launching...' : 'Launch Now'}
          </Button>
        </CardContent>
      </Card>
    </Container>
  );
};

export default StudyActivityLaunch; 