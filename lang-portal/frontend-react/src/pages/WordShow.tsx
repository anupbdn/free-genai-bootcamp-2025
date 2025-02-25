import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Container, Typography, Card, CardContent, Chip, Stack, CircularProgress } from '@mui/material';
import { Word } from '../types';
import { getWord } from '../services/api';

const WordShow: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [word, setWord] = useState<Word | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      getWord(parseInt(id))
        .then(response => {
          setWord(response.data);
          setLoading(false);
        })
        .catch(error => {
          console.error('Error fetching word:', error);
          setLoading(false);
        });
    }
  }, [id]);

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  if (!word) {
    return (
      <Container>
        <Typography color="error">Word not found</Typography>
      </Container>
    );
  }

  return (
    <Container>
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h4" gutterBottom>
            {word.japanese}
          </Typography>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {word.romaji}
          </Typography>
          <Typography variant="h5" gutterBottom>
            {word.english}
          </Typography>
          {word.parts && (
            <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
              {word.parts.kanji && (
                <Chip label={`Kanji: ${word.parts.kanji}`} color="primary" />
              )}
              {word.parts.hiragana && (
                <Chip label={`Hiragana: ${word.parts.hiragana.join('')}`} color="secondary" />
              )}
            </Stack>
          )}
        </CardContent>
      </Card>
    </Container>
  );
};

export default WordShow; 