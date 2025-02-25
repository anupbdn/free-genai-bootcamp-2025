import React, { useEffect, useState } from 'react';
import {
  Container, Typography, Paper, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow,
  CircularProgress, Alert, Link as MuiLink,
  TablePagination
} from '@mui/material';
import { Link } from 'react-router-dom';
import { getStudySessions } from '../services/api';
import { StudySession } from '../types';

const StudySessions: React.FC = () => {
  const [sessions, setSessions] = useState<StudySession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    getStudySessions()
      .then(response => {
        setSessions(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching sessions:', error);
        setError('Failed to load study sessions');
        setLoading(false);
      });
  }, []);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
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
        Study Sessions
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Activity</TableCell>
              <TableCell>Group</TableCell>
              <TableCell>Words Reviewed</TableCell>
              <TableCell>Completion Rate</TableCell>
              <TableCell>Correct/Incorrect</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sessions
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((session) => (
                <TableRow key={session.id}>
                  <TableCell>
                    <MuiLink component={Link} to={`/study_sessions/${session.id}`}>
                      {session.id}
                    </MuiLink>
                  </TableCell>
                  <TableCell>{session.activity?.name || 'N/A'}</TableCell>
                  <TableCell>{session.group_name || 'N/A'}</TableCell>
                  <TableCell>{session.stats?.words_reviewed || 0}</TableCell>
                  <TableCell>{session.stats?.completion_rate || 0}%</TableCell>
                  <TableCell>
                    {session.stats?.correct_answers || 0}/{session.stats?.incorrect_answers || 0}
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={sessions.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>
    </Container>
  );
};

export default StudySessions; 