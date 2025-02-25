import React from 'react';
import { 
  Container, Typography, Grid, Card, Box, Button,
  Avatar, LinearProgress, Chip, Paper
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '@mui/material/styles';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import LocalFireDepartmentIcon from '@mui/icons-material/LocalFireDepartment';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();

  const learningPaths = [
    {
      title: 'Basics',
      description: 'Start with fundamental Japanese phrases',
      progress: 80,
      completed: true,
      icon: '🎌'
    },
    {
      title: 'Greetings',
      description: 'Learn everyday Japanese greetings',
      progress: 60,
      current: true,
      icon: '👋'
    },
    {
      title: 'Numbers',
      description: 'Master Japanese numbers and counting',
      progress: 0,
      locked: true,
      icon: '🔢'
    },
    {
      title: 'Colors',
      description: 'Learn color names in Japanese',
      progress: 0,
      locked: true,
      icon: '🎨'
    }
  ];

  return (
    <Box 
      sx={{ 
        minHeight: '100vh',
        width: '100%',
        maxWidth: '100%',
        overflowX: 'hidden',  // Prevent horizontal scroll
        bgcolor: 'background.default'
      }}
    >
      {/* Hero Section */}
      <Box
        sx={{
          position: 'relative',
          height: '500px',
          width: '100%',
          overflow: 'hidden',
          mb: 6
        }}
      >
        {/* Background Image Container */}
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            overflow: 'hidden',
          }}
        >
          <img 
            src="/Itachi.jpg"
            alt="Background"
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              objectPosition: 'center',
            }}
          />
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'linear-gradient(90deg, rgba(255,255,255,0.7) 0%, rgba(255,255,255,0.5) 100%)',
              zIndex: 1
            }}
          />
        </Box>

        {/* Hero Content */}
        <Container 
          maxWidth="xl"  // Changed to xl for wider content
          sx={{ 
            height: '100%', 
            display: 'flex', 
            alignItems: 'center',
            position: 'relative',
            zIndex: 2
          }}
        >
          <Grid container alignItems="center" spacing={4}>
            {/* Text Content */}
            <Grid item xs={12} md={6}>
              <Typography 
                variant="h1" 
                sx={{ 
                  color: '#1976d2',
                  fontWeight: 700,
                  mb: 2,
                  fontSize: { xs: '2.5rem', md: '3.5rem' },
                  textShadow: 'none'
                }}
              >
                Learn Japanese
              </Typography>
              <Typography 
                variant="h5" 
                sx={{ 
                  color: '#2196f3',
                  mb: 4,
                  textShadow: 'none'
                }}
              >
                Your journey to mastery begins here
              </Typography>
              <Button 
                variant="contained" 
                size="large"
                onClick={() => navigate('/study_activities')}
                sx={{ 
                  px: 4, 
                  py: 1.5,
                  fontSize: '1.1rem',
                  backgroundColor: 'primary.main',
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  }
                }}
              >
                Get Started
              </Button>
            </Grid>

            {/* Optional: Add a floating image or element on the right */}
            <Grid item xs={12} md={6} sx={{ display: { xs: 'none', md: 'block' } }}>
              <Box
                component="img"
                src="/Itachi.jpg"
                alt="Japanese Learning"
                sx={{
                  width: '100%',
                  maxWidth: 400,
                  height: 'auto',
                  borderRadius: 2,
                  boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
                  transform: 'rotate(-3deg)',
                }}
              />
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Main Content */}
      <Container 
        maxWidth="xl"  // Changed to xl for wider content
        sx={{
          px: { xs: 2, sm: 3, md: 4 },  // Responsive padding
        }}
      >
        <Grid 
          container 
          spacing={4}
          sx={{ 
            maxWidth: '100%',
            mx: 'auto'
          }}
        >
          {/* Left Column - Learning Content */}
          <Grid item xs={12} md={7}>
            {/* User Stats Section */}
            <Paper elevation={2} sx={{ p: 3, mb: 4, borderRadius: 2 }}>
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Avatar sx={{ width: 60, height: 60, bgcolor: theme.palette.primary.main }}>
                    👤
                  </Avatar>
                  <Box>
                    <Typography variant="h6">Welcome back!</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Keep up your daily streak
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ display: 'flex', gap: 3 }}>
                  <Box sx={{ textAlign: 'center' }}>
                    <LocalFireDepartmentIcon color="error" />
                    <Typography variant="body2">5 Day Streak</Typography>
                  </Box>
                  <Box sx={{ textAlign: 'center' }}>
                    <EmojiEventsIcon color="warning" />
                    <Typography variant="body2">250 XP</Typography>
                  </Box>
                </Box>
              </Box>
            </Paper>

            {/* Daily Goal Progress */}
            <Paper elevation={2} sx={{ p: 3, mb: 4, borderRadius: 2 }}>
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="h6">Daily Goal</Typography>
                  <Typography color="primary">15/20 XP</Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={75} 
                  sx={{ height: 10, borderRadius: 5 }}
                />
              </Box>
            </Paper>

            {/* Learning Paths */}
            <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
              <Typography variant="h5" gutterBottom>
                Learning Path
              </Typography>
              <Grid container spacing={3}>
                {learningPaths.map((path, index) => (
                  <Grid item xs={12} key={path.title}>
                    <Card 
                      sx={{ 
                        p: 2,
                        display: 'flex',
                        alignItems: 'center',
                        opacity: path.locked ? 0.7 : 1,
                        position: 'relative',
                        '&:hover': {
                          transform: !path.locked ? 'translateY(-2px)' : 'none',
                          boxShadow: !path.locked ? theme.shadows[4] : theme.shadows[1],
                        },
                        transition: 'all 0.2s'
                      }}
                    >
                      {/* Connector Line */}
                      {index < learningPaths.length - 1 && (
                        <Box sx={{
                          position: 'absolute',
                          left: '2.5rem',
                          bottom: '-1.5rem',
                          width: '2px',
                          height: '1.5rem',
                          bgcolor: path.locked ? 'grey.300' : 'primary.main',
                          zIndex: 1
                        }} />
                      )}

                      {/* Content */}
                      <Avatar 
                        sx={{ 
                          width: 50, 
                          height: 50,
                          bgcolor: path.locked ? 'grey.300' : 'primary.light',
                          fontSize: '1.5rem'
                        }}
                      >
                        {path.icon}
                      </Avatar>
                      <Box sx={{ ml: 2, flexGrow: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="h6">{path.title}</Typography>
                          {path.completed && <CheckCircleIcon color="success" />}
                          {path.current && (
                            <Chip 
                              label="Current" 
                              size="small" 
                              color="primary" 
                              sx={{ ml: 1 }}
                            />
                          )}
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {path.description}
                        </Typography>
                        {path.progress > 0 && (
                          <LinearProgress 
                            variant="determinate" 
                            value={path.progress} 
                            sx={{ mt: 1, height: 6, borderRadius: 3 }}
                          />
                        )}
                      </Box>
                      <Button 
                        variant={path.locked ? "outlined" : "contained"}
                        disabled={path.locked}
                        onClick={() => navigate('/study_activities')}
                        sx={{ ml: 2 }}
                      >
                        {path.completed ? 'Practice' : path.locked ? 'Locked' : 'Continue'}
                      </Button>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Paper>
          </Grid>

          {/* Right Column - Japanese Culture Elements */}
          <Grid item xs={12} md={5}>
            <Box sx={{ 
              position: 'sticky', 
              top: 24,
              width: '100%'  // Ensure full width
            }}>
              {/* Japanese Culture Card */}
              <Paper 
                elevation={2} 
                sx={{ 
                  p: 3, 
                  mb: 4, 
                  borderRadius: 2,
                  background: '#ffffff',
                  position: 'relative',
                  overflow: 'hidden'
                }}
              >
                <Typography 
                  variant="h5" 
                  gutterBottom
                  sx={{ 
                    color: '#1976d2',
                    position: 'relative',
                    zIndex: 1
                  }}
                >
                  Japanese Culture Tip
                </Typography>
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 2, 
                  mb: 2,
                  position: 'relative',
                  zIndex: 1
                }}>
                  <Avatar 
                    sx={{ 
                      width: 80,
                      height: 80,
                      bgcolor: '#ff4040',
                      boxShadow: '0 0 15px rgba(255, 0, 0, 0.2)'
                    }}
                  >
                    🗻
                  </Avatar>
                  <Typography 
                    variant="h6"
                    sx={{ 
                      color: '#1565c0'
                    }}
                  >
                    Did you know?
                  </Typography>
                </Box>
                <Typography 
                  paragraph
                  sx={{ 
                    color: '#2196f3',
                    position: 'relative',
                    zIndex: 1
                  }}
                >
                  Mount Fuji, Japan's tallest peak at 3,776 meters, is considered 
                  sacred in Japanese culture and has inspired artists and poets 
                  for centuries.
                </Typography>

                {/* Optional: Add subtle decorative elements */}
                <Box 
                  sx={{
                    position: 'absolute',
                    top: -50,
                    right: -50,
                    width: 100,
                    height: 100,
                    background: '#ff404020',
                    borderRadius: '50%',
                    opacity: 0.1
                  }}
                />
              </Paper>

              {/* Daily Challenge Card */}
              <Paper elevation={2} sx={{ p: 3, mb: 4, borderRadius: 2 }}>
                <Typography variant="h5" gutterBottom>
                  Daily Challenge
                </Typography>
                <Box sx={{ textAlign: 'center', py: 2 }}>
                  <Avatar 
                    sx={{ 
                      width: 80, 
                      height: 80, 
                      margin: '0 auto', 
                      mb: 2,
                      bgcolor: 'primary.light' 
                    }}
                  >
                    🎯
                  </Avatar>
                  <Typography variant="h6" gutterBottom>
                    Master Greetings
                  </Typography>
                  <Typography color="text.secondary" paragraph>
                    Practice 5 different Japanese greetings today
                  </Typography>
                  <Button 
                    variant="contained" 
                    fullWidth
                    onClick={() => navigate('/study_activities')}
                  >
                    Start Challenge
                  </Button>
                </Box>
              </Paper>

              {/* Quick Actions */}
              <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
                <Typography variant="h5" gutterBottom>
                  Quick Actions
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Button 
                      fullWidth 
                      variant="outlined"
                      size="large"
                      onClick={() => navigate('/words')}
                      startIcon={'📚'}
                    >
                      Review Vocabulary
                    </Button>
                  </Grid>
                  <Grid item xs={6}>
                    <Button 
                      fullWidth 
                      variant="outlined"
                      size="large"
                      onClick={() => navigate('/dashboard')}
                      startIcon={'📊'}
                    >
                      View Progress
                    </Button>
                  </Grid>
                </Grid>
              </Paper>
            </Box>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Home;