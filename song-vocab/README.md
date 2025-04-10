# Song Vocabulary Assistant

An AI-powered application that helps users learn vocabulary from songs in different languages. The application fetches lyrics, analyzes them, and provides detailed vocabulary explanations, phrase meanings, and cultural context.

## What is this App?

This application combines several powerful features:
- Automated lyrics fetching from various online sources
- Language detection and validation
- Vocabulary analysis using AI
- Cultural context extraction
- RESTful API interface
- Interactive CLI interface

Perfect for:
- Language learners using music as a learning tool
- Teachers preparing song-based lessons
- Music enthusiasts interested in understanding lyrics
- Anyone wanting to explore songs in different languages

## Capabilities

### 1. Lyrics Search and Retrieval
- Searches multiple sources for song lyrics
- Validates language authenticity
- Handles multiple versions and translations
- Supports various languages (e.g., Japanese, English, Spanish)

### 2. Vocabulary Analysis
- Extracts key vocabulary words
- Provides definitions and meanings
- Includes pronunciation (romaji for Japanese)
- Shows usage examples in context

### 3. Cultural Context
- Identifies cultural references
- Explains idioms and phrases
- Provides historical context
- Highlights cultural significance

### 4. Interactive Features
- Conversation memory for follow-up questions
- Multiple query formats supported
- Error handling and suggestions
- Progress tracking

## Tech Stack

### Core Technologies
- **Python 3.x**: Primary programming language
- **FastAPI**: Modern web framework for building APIs
- **LangChain**: Framework for building LLM applications
- **Ollama**: Local LLM integration (using Mistral model)

### Key Libraries
- **langdetect**: Language detection
- **BeautifulSoup4**: Web scraping
- **requests**: HTTP client
- **Pydantic**: Data validation
- **uvicorn**: ASGI server

### AI/ML Components
- **Mistral**: Large Language Model (via Ollama)
- **LangChain Agents**: For orchestrating AI tasks
- **ReAct Framework**: For reasoning and action

## How to Use and Run the App

### Prerequisites
1. Install Python 3.x
2. Install Ollama and the Mistral model
3. Clone this repository

### Installation

1. We are using uv to manage the project:
```bash
uv sync --active
source .venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install required packages:
```bash
cat pyproject.toml
```

3. Start Ollama with Mistral model:
```bash
ollama run mistral
```

### Running the Application

#### CLI Interface
Run the interactive CLI:
```bash
python song_agent.py
```

Example usage:
```
Your request: Find vocabulary from Sukiyaki by Kyu Sakamoto in Japanese
```

#### API Server
Start the FastAPI server:
```bash
python api_server.py
```

The API will be available at:
- API Endpoint: http://localhost:8000/api/agent
- Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### API Usage

Make a POST request to `/api/agent`:
```bash
curl -X POST "http://localhost:8000/api/agent" \
     -H "Content-Type: application/json" \
     -d '{"message_request": "Find vocabulary from Sukiyaki by Kyu Sakamoto in Japanese"}'
```

Example Response:
```json
{
    "lyrics": "上を向いて歩こう...",
    "vocabulary": [
        {
            "word": "上",
            "romaji": "ue",
            "meaning": "up, above",
            "example": "上を向いて (ue wo muite)"
        }
    ],
    "phrases": [
        {
            "phrase": "上を向いて歩こう",
            "meaning": "Let's walk looking up"
        }
    ],
    "cultural_references": [
        {
            "reference": "Cultural Note",
            "explanation": "The song title 'Sukiyaki' was chosen..."
        }
    ]
}
```
