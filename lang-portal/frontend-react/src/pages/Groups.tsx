import React, { useEffect, useState } from 'react';
import { 
  Container, Typography, Table, TableBody, TableCell, 
  TableContainer, TableHead, TableRow, Paper, CircularProgress,
  Link as MuiLink 
} from '@mui/material';
import { Link } from 'react-router-dom';
import { getGroups } from '../services/api';
import { Group } from '../types';

const Groups: React.FC = () => {
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getGroups()
      .then(response => {
        setGroups(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching groups:', error);
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
        Word Groups
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Group Name</TableCell>
              <TableCell align="right">Word Count</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {groups.map((group) => (
              <TableRow key={group.id}>
                <TableCell>
                  <MuiLink component={Link} to={`/groups/${group.id}`}>
                    {group.name}
                  </MuiLink>
                </TableCell>
                <TableCell align="right">{group.word_count}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default Groups; 