import axios from 'axios';
import { Word, StudySession, StudyActivity, QuickStats, StudyProgress, Group } from '../types';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api', // Your FastAPI backend
  headers: { 'Content-Type': 'application/json' },
});

export const getWords = () => api.get<Word[]>('/words');
export const getLastStudySession = () => api.get<StudySession>('/dashboard/last_study_session');
export const getDashboardStats = () => api.get<QuickStats>('/dashboard/quick-stats');
export const getStudyProgress = () => api.get<StudyProgress>('/dashboard/study_progress');
export const getStudyActivities = () => api.get<StudyActivity[]>('/study_activities');
export const getStudyActivity = (id: number) => api.get<StudyActivity>(`/study_activities/${id}`);
export const launchStudyActivity = (id: number, data: LaunchData) => 
  api.post<StudySession>(`/study_activities/${id}/launch`, data);
export const getGroups = () => api.get<Group[]>('/groups');
export const getGroup = (id: number) => api.get<Group>(`/groups/${id}`);
export const getGroupWords = (id: number) => api.get<Word[]>(`/groups/${id}/words`);
export const getStudySessions = () => api.get<StudySession[]>('/study_sessions');
export const getStudySession = (id: number) => api.get<StudySession>(`/study_sessions/${id}`);
export const getWord = (id: number) => api.get<Word>(`/words/${id}`);
export const getGroupStudySessions = (id: number) => 
  api.get<StudySession[]>(`/groups/${id}/study_sessions`);
export const resetHistory = () => api.post('/reset_history');
export const fullReset = () => api.post('/full_reset');