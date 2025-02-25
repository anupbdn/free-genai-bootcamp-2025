import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';
import { LastSessionCardProps } from '../../types';

export const LastSessionCard: React.FC<LastSessionCardProps> = ({ session }) => {
  if (!session) return null;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Last Study Session
        </Typography>
        <Typography variant="h5">{session.group_name}</Typography>
        <Typography>Activity: {session.activity.name}</Typography>
        <Typography>Words Reviewed: {session.stats.words_reviewed}</Typography>
        <Typography>Correct: {session.stats.correct_answers}</Typography>
        <Typography>Incorrect: {session.stats.incorrect_answers}</Typography>
        <Typography>Completion: {session.stats.completion_rate}%</Typography>
      </CardContent>
    </Card>
  );
}; 