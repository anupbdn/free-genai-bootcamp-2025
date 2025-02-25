import React, { useEffect, useState } from 'react';
import { 
  Container, Typography, Paper, Table, TableBody, TableCell, 
  TableContainer, TableHead, TableRow, CircularProgress 
} from '@mui/material';
import { getWords } from '../services/api';
import { Word } from '../types';

const Words: React.FC = () => {
  const [words, setWords] = useState<Word[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getWords()
      .then(response => {
        console.log('API Response:', response.data);
        setWords(Array.isArray(response.data) ? response.data : []); // Ensure we're handling array
        setLoading(false);
      })
      .catch(error => {
        console.error('Error details:', error.response || error);
        setError(error.message);
        setLoading(false);
      });
  }, []);

  if (loading) return (
    <Container sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
      <CircularProgress />
    </Container>
  );
  
  if (error) return (
    <Container>
      <Typography color="error">{error}</Typography>
    </Container>
  );

  return (
    <Container>
      <Typography variant="h4" gutterBottom sx={{ mt: 4 }}>
        Japanese Vocabulary ({words.length} words)
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Japanese</TableCell>
              <TableCell>Romaji</TableCell>
              <TableCell>English</TableCell>
              <TableCell>Parts</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {words.map((word) => (
              <TableRow key={word.id}>
                <TableCell>{word.japanese}</TableCell>
                <TableCell>{word.romaji}</TableCell>
                <TableCell>{word.english}</TableCell>
                <TableCell>
                  {word.parts?.kanji && `Kanji: ${Array.isArray(word.parts.kanji) ? word.parts.kanji.join(', ') : word.parts.kanji}`}
                  {word.parts?.hiragana && ` Hiragana: ${word.parts.hiragana.join('')}`}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default Words;