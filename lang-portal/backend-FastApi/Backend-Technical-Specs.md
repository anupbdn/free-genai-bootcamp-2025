# Backend Server Technical Specs

## Business Goal:

A language learning school wants to build a prototype of learning portal which will act as three things:
- Inventory of possible vocabulary that can be learned
- Act as a  Learning record store (LRS), providing correct and wrong score on practice vocabulary
- A unified launchpad to launch different learning apps

## Technical Requirements

- The backend will be built using Python
- The database will be SQLite3
- The API will be built using FastApi
- Complete Package Management of python will be done using `uv`
- The API will always return JSON
- There will be no need for authentication or authorization
- Everything be treated as a single user

## Directory Structure

```text
backend-FastApi/
├── README.md
├── pyproject.toml          # Project dependencies and metadata
├── uv.lock                 # UV lock file
├── words.db               # SQLite database
│
├── src/                   # Source code directory
│   ├── __init__.py
│   ├── main.py           # FastAPI application entry point
│   │
│   ├── api/              # API route handlers
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── words.py
│   │   ├── groups.py
│   │   ├── study_sessions.py
│   │   └── study_activities.py
│   │
│   ├── models/           # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── word.py
│   │   ├── group.py
│   │   ├── study_session.py
│   │   └── word_review.py
│   │
│   ├── schemas/          # Pydantic models
│   │   ├── __init__.py
│   │   ├── word.py
│   │   ├── group.py
│   │   ├── study_session.py
│   │   └── dashboard.py
│   │
│   ├── core/             # Core application code
│   │   ├── __init__.py
│   │   ├── config.py     # Configuration settings
│   │   ├── database.py   # Database connection
│   │   └── exceptions.py # Custom exceptions
│   │
│   ├── services/         # Business logic
│   │   ├── __init__.py
│   │   ├── word_service.py
│   │   ├── group_service.py
│   │   └── study_service.py
│   │
│   └── utils/            # Utility functions
│       ├── __init__.py
│       └── helpers.py
│
├── migrations/           # Database migrations
│   ├── 0001_init.sql
│   └── 0002_create_words_table.sql
│
├── seeds/                # Seed data files
│   ├── basic_greetings.json
│   └── numbers.json
│
├── scripts/             # Task runner scripts
│   ├── __init__.py
│   ├── init_db.py
│   ├── run_migrations.py
│   └── seed_data.py
│
└── tests/               # Test files
    ├── __init__.py
    ├── conftest.py
    ├── test_api/
    │   ├── test_words.py
    │   └── test_groups.py
    └── test_services/
        ├── test_word_service.py
        └── test_group_service.py
```


## Database Schema

Our database will be a single sqlite database called `words.db` that will be in the root of the project folder of `backend-FastApi`

We have the following tables:
- words - stored vocabulary words
  - id integer
  - japanese string
  - romaji string
  - english string
  - parts json
- words_groups - join table for words and groups many-to-many
  - id integer
  - word_id integer
  - group_id integer
- groups - thematic groups of words
  - id integer
  - name string
- study_sessions - records of study sessions grouping word_review_items
  - id integer
  - group_id integer
  - created_at datetime
  - study_activity_id integer
- study_activities - a specific study activity, linking a study session to group
  - id integer
  - study_session_id integer
  - group_id integer
  - created_at datetime
- word_review_items - a record of word practice, determining if the word was correct or not
  - word_id integer
  - study_session_id integer
  - correct boolean
  - created_at datetime

## API Endpoints

### GET /api/dashboard/last_study_session
Returns information about the most recent study session, including detailed statistics.

#### JSON Response
```json
{
  "id": 123,
  "group_id": 456,
  "created_at": "2025-02-08T17:20:23-05:00",
  "study_activity_id": 789,
  "group_name": "Basic Greetings",
  "stats": {
    "words_reviewed": 20,
    "correct_answers": 15,
    "incorrect_answers": 5,
    "completion_rate": 75.0,
    "duration_minutes": 15
  },
  "activity": {
    "name": "Vocabulary Quiz",
    "type": "flashcards"
  }
}
```

### GET /api/dashboard/study_progress
Returns detailed study progress statistics including historical data.

#### JSON Response
```json
{
  "total_words_studied": 3,
  "total_available_words": 124,
  "progress_details": {
    "daily_progress": {
      "words_learned_today": 10,
      "daily_goal": 20,
      "completion_percentage": 50.0
    },
    "weekly_progress": {
      "words_learned_this_week": 45,
      "weekly_goal": 100,
      "completion_percentage": 45.0
    },
    "monthly_progress": {
      "words_learned_this_month": 150,
      "monthly_goal": 400,
      "completion_percentage": 37.5
    }
  },
  "learning_velocity": {
    "words_per_day": 8.5,
    "estimated_completion_days": 15
  }
}
```

### GET /api/dashboard/quick-stats
Returns comprehensive overview statistics including trends.

#### JSON Response
```json
{
  "success_rate": 80.0,
  "total_study_sessions": 4,
  "total_active_groups": 3,
  "study_streak_days": 4,
  "detailed_stats": {
    "today": {
      "words_studied": 20,
      "correct_answers": 16,
      "study_time_minutes": 45
    },
    "this_week": {
      "total_sessions": 12,
      "average_score": 85.5,
      "most_studied_group": "Basic Greetings"
    },
    "trends": {
      "success_rate_trend": [75.0, 78.0, 80.0, 82.0, 80.0],
      "study_time_trend": [30, 45, 40, 45, 45]
    }
  },
  "achievements": {
    "current_level": "Intermediate",
    "points": 1250,
    "next_milestone": 1500
  }
}
```

### GET /api/study_activities/:id
Returns detailed information about a specific study activity.

#### JSON Response
```json
{
  "id": 1,
  "name": "Vocabulary Quiz",
  "type": "flashcards",
  "thumbnail_url": "https://example.com/thumbnail.jpg",
  "description": "Practice your vocabulary with flashcards",
  "details": {
    "difficulty_level": "beginner",
    "estimated_duration_minutes": 15,
    "recommended_group_size": 20,
    "instructions": "Review each card and mark whether you know the word or not"
  },
  "statistics": {
    "times_completed": 45,
    "average_success_rate": 82.5,
    "average_completion_time": 12
  },
  "requirements": {
    "minimum_words_needed": 10,
    "recommended_prior_knowledge": ["Basic Hiragana", "Basic Greetings"]
  }
}
```

### GET /api/study_activities/:id/study_sessions

- pagination with 100 items per page

```json
{
  "items": [
    {
      "id": 123,
      "activity_name": "Vocabulary Quiz",
      "group_name": "Basic Greetings",
      "start_time": "2025-02-08T17:20:23-05:00",
      "end_time": "2025-02-08T17:30:23-05:00",
      "review_items_count": 20
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 100,
    "items_per_page": 20
  }
}
```

### POST /api/study_activities

#### Request Params
- group_id integer
- study_activity_id integer

#### JSON Response
```json
{
  "id": 124,
  "group_id": 123
}
```

### GET /api/words

- pagination with 100 items per page

#### JSON Response
```json
{
  "items": [
    {
      "japanese": "こんにちは",
      "romaji": "konnichiwa",
      "english": "hello",
      "correct_count": 5,
      "wrong_count": 2
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 500,
    "items_per_page": 100
  }
}
```

### GET /api/words/:id
Returns comprehensive information about a specific word.

#### JSON Response
```json
{
  "id": 123,
  "japanese": "こんにちは",
  "romaji": "konnichiwa",
  "english": "hello",
  "parts": {
    "kanji": [],
    "hiragana": ["こ", "ん", "に", "ち", "は"]
  },
  "stats": {
    "correct_count": 5,
    "wrong_count": 2,
    "success_rate": 71.4,
    "last_reviewed": "2025-02-08T17:20:23-05:00",
    "mastery_level": "intermediate"
  },
  "groups": [
    {
      "id": 1,
      "name": "Basic Greetings",
      "progress_in_group": 85.0
    }
  ],
  "usage_examples": [
    {
      "japanese": "こんにちは、元気ですか？",
      "romaji": "konnichiwa, genki desu ka?",
      "english": "Hello, how are you?"
    }
  ],
  "study_history": {
    "last_5_attempts": [
      {
        "date": "2025-02-08T17:20:23-05:00",
        "correct": true,
        "study_session_id": 123
      }
    ],
    "learning_curve": {
      "initial_success_rate": 60.0,
      "current_success_rate": 85.0,
      "improvement_rate": 25.0
    }
  }
}
```

### GET /api/groups
- pagination with 100 items per page
#### JSON Response
```json
{
  "items": [
    {
      "id": 1,
      "name": "Basic Greetings",
      "word_count": 20
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "total_items": 10,
    "items_per_page": 100
  }
}
```

### GET /api/groups/:id
Returns detailed information about a specific group including learning progress.

#### JSON Response
```json
{
  "id": 1,
  "name": "Basic Greetings",
  "description": "Essential greeting phrases for everyday conversation",
  "difficulty_level": "beginner",
  "stats": {
    "total_word_count": 20,
    "mastered_words": 15,
    "learning_words": 3,
    "not_started_words": 2,
    "group_mastery": 75.0,
    "average_success_rate": 82.5
  },
  "learning_progress": {
    "started_date": "2025-01-01T00:00:00-05:00",
    "last_study_date": "2025-02-08T17:20:23-05:00",
    "study_sessions_count": 12,
    "total_study_time_minutes": 180
  },
  "recommended_activities": [
    {
      "id": 1,
      "name": "Vocabulary Quiz",
      "suitability_score": 95
    }
  ],
  "prerequisites": {
    "required_groups": [],
    "recommended_groups": ["Hiragana Basics"]
  }
}
```

### GET /api/groups/:id/words
#### JSON Response
```json
{
  "items": [
    {
      "japanese": "こんにちは",
      "romaji": "konnichiwa",
      "english": "hello",
      "correct_count": 5,
      "wrong_count": 2
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "total_items": 20,
    "items_per_page": 100
  }
}
```

### GET /api/groups/:id/study_sessions
#### JSON Response
```json
{
  "items": [
    {
      "id": 123,
      "activity_name": "Vocabulary Quiz",
      "group_name": "Basic Greetings",
      "start_time": "2025-02-08T17:20:23-05:00",
      "end_time": "2025-02-08T17:30:23-05:00",
      "review_items_count": 20
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "total_items": 5,
    "items_per_page": 100
  }
}
```

### GET /api/study_sessions
- pagination with 100 items per page
#### JSON Response
```json
{
  "items": [
    {
      "id": 123,
      "activity_name": "Vocabulary Quiz",
      "group_name": "Basic Greetings",
      "start_time": "2025-02-08T17:20:23-05:00",
      "end_time": "2025-02-08T17:30:23-05:00",
      "review_items_count": 20
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 100,
    "items_per_page": 100
  }
}
```

### GET /api/study_sessions/:id
Returns comprehensive information about a specific study session.

#### JSON Response
```json
{
  "id": 123,
  "activity_name": "Vocabulary Quiz",
  "activity_type": "flashcards",
  "group_name": "Basic Greetings",
  "start_time": "2025-02-08T17:20:23-05:00",
  "end_time": "2025-02-08T17:30:23-05:00",
  "duration_minutes": 10,
  "review_items_count": 20,
  "performance_stats": {
    "correct_answers": 15,
    "incorrect_answers": 5,
    "success_rate": 75.0,
    "average_response_time_seconds": 3.5
  },
  "progress": {
    "completed_items": 20,
    "total_items": 20,
    "completion_rate": 100.0
  },
  "difficulty_analysis": {
    "easiest_words": [
      {
        "japanese": "はい",
        "romaji": "hai",
        "success_rate": 100.0
      }
    ],
    "hardest_words": [
      {
        "japanese": "さようなら",
        "romaji": "sayounara",
        "success_rate": 40.0
      }
    ]
  },
  "recommendations": {
    "suggested_review_words": [
      {
        "word_id": 456,
        "japanese": "さようなら",
        "reason": "low_success_rate"
      }
    ],
    "next_study_session": {
      "recommended_time": "2025-02-09T17:20:23-05:00",
      "focus_areas": ["Challenging Words", "New Vocabulary"]
    }
  }
}
```

### GET /api/study_sessions/:id/words
- pagination with 100 items per page
#### JSON Response
```json
{
  "items": [
    {
      "japanese": "こんにちは",
      "romaji": "konnichiwa",
      "english": "hello",
      "correct_count": 5,
      "wrong_count": 2
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "total_items": 20,
    "items_per_page": 100
  }
}
```

### POST /api/reset_history
#### JSON Response
```json
{
  "success": true,
  "message": "Study history has been reset"
}
```

### POST /api/full_reset
#### JSON Response
```json
{
  "success": true,
  "message": "System has been fully reset"
}
```

### POST /api/study_sessions/:id/words/:word_id/review
#### Request Params
- id (study_session_id) integer
- word_id integer
- correct boolean

#### Request Payload
```json
{
  "correct": true
}
```

#### JSON Response
```json
{
  "success": true,
  "word_id": 1,
  "study_session_id": 123,
  "correct": true,
  "created_at": "2025-02-08T17:33:07-05:00"
}
```

## Task Runner Tasks

Lets list out possible tasks we need for our lang portal.

### Initialize Database
This task will initialize the sqlite database called `words.db

### Migrate Database
This task will run a series of migrations sql files on the database

Migrations live in the `migrations` folder.
The migration files will be run in order of their file name.
The file names should look like this:

```sql
0001_init.sql
0002_create_words_table.sql
```

### Seed Data
This task will import json files and transform them into target data for our database.

All seed files live in the `seeds` folder.

In our task we should have DSL to specific each seed file and its expected group word name.

```json
[
  {
    "kanji": "払う",
    "romaji": "harau",
    "english": "to pay",
  },
  ...
]
```

### Use pytest for Unit testing

This task will create test cases which will run and give you a PASS or FAILURE message. This comprehensive test cases will ensure that the API endpoint and services are working as expected.

```text
tests/test_api/test_dashboard.py::test_get_dashboard_stats PASSED                                                     [ 11%]
tests/test_api/test_dashboard.py::test_get_study_progress PASSED                                                      [ 22%]
tests/test_api/test_groups.py::test_create_group PASSED                                                               [ 33%]
tests/test_api/test_groups.py::test_get_groups PASSED                                                                 [ 44%]
tests/test_api/test_groups.py::test_get_group_words PASSED                                                            [ 55%]
tests/test_api/test_words.py::test_read_words PASSED                                                                  [ 66%]
tests/test_api/test_words.py::test_create_word PASSED                                                                 [ 77%]
tests/test_api/test_words.py::test_get_words PASSED                                                                   [ 88%]
tests/test_api/test_words.py::test_get_word PASSED   

```
