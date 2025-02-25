export interface Word {
    id: number;
    japanese: string;
    romaji: string;
    english: string;
    parts?: { kanji?: string[]; hiragana?: string[] };
  }
  
  export interface StudySession {
    id: number;
    group_name: string;
    activity: {
      name: string;
    };
    stats: {
      words_reviewed: number;
      correct_answers: number;
      incorrect_answers: number;
      completion_rate: number;
    };
  }
  
  export interface StudyActivity {
    id: number;
    name: string;
    type: string;
    thumbnail_url?: string;
    description?: string;
  }

export interface QuickStats {
  success_rate: number;
  total_study_sessions: number;
  total_active_groups: number;
  study_streak_days: number;
}

export interface StudyProgress {
  total_words_studied: number;
  total_available_words: number;
  mastery_percentage: number;
}

export interface LastSessionCardProps {
  session: StudySession | null;
}

export interface StudyProgressCardProps {
  progress: StudyProgress | null;
}

export interface QuickStatsCardProps {
  stats: QuickStats | null;
}

export interface LaunchData {
  group_id: number;
}

export interface Group {
  id: number;
  name: string;
  word_count: number;
}