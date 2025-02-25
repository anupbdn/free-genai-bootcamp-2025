import React from 'react';
import { Card, CardContent, Typography, LinearProgress, Box } from '@mui/material';
import { StudyProgressCardProps } from '../../types';

export const StudyProgressCard: React.FC<StudyProgressCardProps> = ({ progress }) => {
  if (!progress) return null;

  // Ensure we have a valid value for the progress bar
  const progressValue = progress.mastery_percentage || 0;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Study Progress
        </Typography>
        <Typography variant="body1" gutterBottom>
          Words Studied: {progress.total_words_studied}/{progress.total_available_words}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Box sx={{ width: '100%', mr: 1 }}>
            <LinearProgress 
              variant="determinate" 
              value={progressValue} 
            />
          </Box>
          <Box sx={{ minWidth: 35 }}>
            <Typography variant="body2">
              {Math.round(progressValue)}%
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}; 