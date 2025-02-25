import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Home from './pages/Home';
import Words from './pages/Words';
import Dashboard from './pages/Dashboard';
import Launchpad from './pages/Launchpad';
import WordShow from './pages/WordShow';
import Groups from './pages/Groups';
import GroupShow from './pages/GroupShow';
import StudyActivities from './pages/StudyActivities';
import StudyActivityShow from './pages/StudyActivityShow';
import StudyActivityLaunch from './pages/StudyActivityLaunch';
import StudySessions from './pages/StudySessions';
import StudySessionShow from './pages/StudySessionShow';
import Settings from './pages/Settings';
import { AppBar, Toolbar, Typography, Button, Container, Box, useTheme } from '@mui/material';
import { ThemeProvider } from './contexts/ThemeContext';
import { CssBaseline } from '@mui/material';

const App: React.FC = () => {
  const theme = useTheme();
  
  return (
    <ThemeProvider>
      <CssBaseline />
      <Router>
        <AppBar 
          position="static" 
          elevation={0}
          sx={{
            backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
            borderBottom: `1px solid ${theme.palette.divider}`,
          }}
        >
          <Container>
            <Toolbar disableGutters>
              <Typography 
                variant="h6" 
                component="div"
                sx={{ 
                  flexGrow: 1,
                  color: theme.palette.mode === 'dark' ? '#fff' : '#1A2027',
                  fontWeight: 700
                }}
              >
                Language Learning Portal
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                {[
                  { label: 'Home', path: '/' },
                  { label: 'Dashboard', path: '/dashboard' },
                  { label: 'Words', path: '/words' },
                  { label: 'Groups', path: '/groups' },
                  { label: 'Study', path: '/study_activities' },
                  { label: 'Sessions', path: '/study_sessions' },
                  { label: 'Settings', path: '/settings' }
                ].map((item) => (
                  <Button 
                    key={item.label}
                    color="primary"
                    component={Link} 
                    to={item.path}
                    sx={{ 
                      borderRadius: 2,
                      color: theme.palette.mode === 'dark' ? '#fff' : '#1976d2',
                      '&:hover': {
                        backgroundColor: theme.palette.mode === 'dark' 
                          ? 'rgba(255,255,255,0.1)' 
                          : 'rgba(25,118,210,0.1)',
                      },
                      fontWeight: 500
                    }}
                  >
                    {item.label}
                  </Button>
                ))}
              </Box>
            </Toolbar>
          </Container>
        </AppBar>
        <Container style={{ marginTop: '20px' }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/words" element={<Words />} />
            <Route path="/words/:id" element={<WordShow />} />
            <Route path="/groups" element={<Groups />} />
            <Route path="/groups/:id" element={<GroupShow />} />
            <Route path="/study_activities" element={<StudyActivities />} />
            <Route path="/study_activities/:id" element={<StudyActivityShow />} />
            <Route path="/study_activities/:id/launch" element={<StudyActivityLaunch />} />
            <Route path="/study_sessions" element={<StudySessions />} />
            <Route path="/study_sessions/:id" element={<StudySessionShow />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Container>
      </Router>
    </ThemeProvider>
  );
};

export default App;
// import './App.css'

// function App() {
//   return (
//     <div className="min-h-screen bg-gray-100">
//       <header className="bg-white shadow">
//         <nav className="container mx-auto px-4 py-4">
//           <h1 className="text-2xl font-bold text-gray-900">Language Learning Portal</h1>
//         </nav>
//       </header>

//       <main className="container mx-auto px-4 py-8">
//         <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
//           {/* Word Groups */}
//           <div className="bg-white p-6 rounded-lg shadow">
//             <h2 className="text-xl font-semibold mb-4">Word Groups</h2>
//             <ul className="space-y-2">
//               <li>Basic Greetings</li>
//               <li>Numbers</li>
//               <li>Colors</li>
//             </ul>
//           </div>

//           {/* Study Progress */}
//           <div className="bg-white p-6 rounded-lg shadow">
//             <h2 className="text-xl font-semibold mb-4">Study Progress</h2>
//             <div className="text-gray-600">
//               <p>Words Learned: 15</p>
//               <p>Success Rate: 80%</p>
//             </div>
//           </div>

//           {/* Recent Activity */}
//           <div className="bg-white p-6 rounded-lg shadow">
//             <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
//             <div className="text-gray-600">
//               <p>Last Study Session: Basic Greetings</p>
//               <p>Score: 8/10</p>
//             </div>
//           </div>
//         </div>
//       </main>
//     </div>
//   )
// }

// export default App
