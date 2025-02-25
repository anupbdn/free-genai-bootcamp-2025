import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { 
  Container, Typography, Grid, Paper, Table, TableBody, 
  TableCell, TableContainer, TableHead, TableRow, CircularProgress,
  Link as MuiLink, Tabs, Tab, Box
} from '@mui/material';
import { Link } from 'react-router-dom';
import { getGroup, getGroupWords, getGroupStudySessions } from '../services/api';
import { Group, Word, StudySession } from '../types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel = (props: TabPanelProps) => {
  const { children, value, index, ...other } = props;
  return (
    <div hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
};

const GroupShow: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [group, setGroup] = useState<Group | null>(null);
  const [words, setWords] = useState<Word[]>([]);
  const [sessions, setSessions] = useState<StudySession[]>([]);
  const [loading, setLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      Promise.all([
        getGroup(parseInt(id)),
        getGroupWords(parseInt(id)),
        getGroupStudySessions(parseInt(id)).catch(() => [])
      ]).then(([groupRes, wordsRes, sessionsRes]) => {
        setGroup(groupRes.data);
        setWords(wordsRes.data);
        setSessions(sessionsRes.data || []);
        setLoading(false);
      }).catch(error => {
        console.error('Error fetching group data:', error);
        setError('Failed to load group data');
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

  if (!group) {
    return (
      <Container>
        <Typography color="error">Group not found</Typography>
      </Container>
    );
  }

  return (
    <Container>
      <Typography variant="h4" gutterBottom sx={{ mt: 4 }}>
        {group.name}
      </Typography>
      <Typography variant="subtitle1" gutterBottom>
        Total Words: {group.word_count}
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mt: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="Words" />
          <Tab label="Study Sessions" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
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
                  <TableCell>
                    <MuiLink component={Link} to={`/words/${word.id}`}>
                      {word.japanese}
                    </MuiLink>
                  </TableCell>
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
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Activity</TableCell>
                <TableCell>Words Reviewed</TableCell>
                <TableCell>Completion Rate</TableCell>
                <TableCell>Correct/Incorrect</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sessions.map((session) => (
                <TableRow key={session.id}>
                  <TableCell>
                    <MuiLink component={Link} to={`/study_sessions/${session.id}`}>
                      {session.id}
                    </MuiLink>
                  </TableCell>
                  <TableCell>{session.activity.name}</TableCell>
                  <TableCell>{session.stats.words_reviewed}</TableCell>
                  <TableCell>{session.stats.completion_rate}%</TableCell>
                  <TableCell>
                    {session.stats.correct_answers}/{session.stats.incorrect_answers}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>
    </Container>
  );
};

export default GroupShow; 