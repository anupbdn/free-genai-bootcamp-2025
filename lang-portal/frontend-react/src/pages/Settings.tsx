import React, { useState } from 'react';
import { 
  Container, Typography, Card, CardContent, FormControl, 
  FormLabel, RadioGroup, FormControlLabel, Radio, Button, 
  Stack, Dialog, DialogTitle, DialogContent, DialogActions,
  DialogContentText, Alert, Snackbar
} from '@mui/material';
import { resetHistory, fullReset } from '../services/api';
import { useTheme } from '../contexts/ThemeContext';

type Theme = 'light' | 'dark' | 'system';

const Settings: React.FC = () => {
  const { mode, setMode } = useTheme();
  const [resetDialog, setResetDialog] = useState<'history' | 'full' | null>(null);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  }>({
    open: false,
    message: '',
    severity: 'success'
  });

  const handleThemeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newTheme = event.target.value as Theme;
    setMode(newTheme);
  };

  const handleReset = async () => {
    setLoading(true);
    try {
      if (resetDialog === 'history') {
        await resetHistory();
        showSnackbar('Study history has been reset successfully', 'success');
      } else if (resetDialog === 'full') {
        await fullReset();
        showSnackbar('Full system reset completed successfully', 'success');
      }
    } catch (error) {
      console.error('Reset error:', error);
      showSnackbar('Failed to perform reset operation', 'error');
    } finally {
      setLoading(false);
      setResetDialog(null);
    }
  };

  const showSnackbar = (message: string, severity: 'success' | 'error') => {
    setSnackbar({ open: true, message, severity });
  };

  return (
    <Container>
      <Typography variant="h4" gutterBottom sx={{ mt: 4 }}>
        Settings
      </Typography>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <FormControl component="fieldset">
            <FormLabel component="legend">Theme</FormLabel>
            <RadioGroup value={mode} onChange={handleThemeChange}>
              <FormControlLabel 
                value="light" 
                control={<Radio />} 
                label="Light Theme" 
              />
              <FormControlLabel 
                value="dark" 
                control={<Radio />} 
                label="Dark Theme" 
              />
              <FormControlLabel 
                value="system" 
                control={<Radio />} 
                label="System Default" 
              />
            </RadioGroup>
          </FormControl>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Reset Options
          </Typography>
          <Stack spacing={2}>
            <Button 
              variant="outlined" 
              color="warning"
              onClick={() => setResetDialog('history')}
            >
              Reset Study History
            </Button>
            <Button 
              variant="outlined" 
              color="error"
              onClick={() => setResetDialog('full')}
            >
              Full System Reset
            </Button>
          </Stack>
        </CardContent>
      </Card>

      {/* Reset Confirmation Dialog */}
      <Dialog
        open={resetDialog !== null}
        onClose={() => setResetDialog(null)}
      >
        <DialogTitle>
          {resetDialog === 'history' ? 'Reset Study History?' : 'Full System Reset?'}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            {resetDialog === 'history' 
              ? 'This will delete all study sessions and word review items. This action cannot be undone.'
              : 'This will reset the entire system to its initial state with seed data. All progress will be lost. This action cannot be undone.'
            }
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setResetDialog(null)} 
            disabled={loading}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleReset} 
            color="error" 
            disabled={loading}
            autoFocus
          >
            {loading ? 'Resetting...' : 'Confirm Reset'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success/Error Snackbar */}
      <Snackbar 
        open={snackbar.open} 
        autoHideDuration={6000} 
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Settings; 