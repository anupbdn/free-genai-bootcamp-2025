# Language Listening Comprehension App

A language learning application that generates comprehension questions from YouTube videos using AI.

## Features

- YouTube transcript extraction
- AI-powered question generation
- Support for multiple languages
- Vector store for question management
- Integration with Ollama and AWS Bedrock
- Text-To-Speech using gTTS and Google.Cloud.Text-To-Speech

## Prerequisites

- Python 3.9 or higher
- uv package manager
- Ollama (for local model support)
- AWS Account (for Bedrock support)

## Installation

1. Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:
```bash
git clone <repository-url>
cd language-listening-app
```

3. Create and activate a virtual environment using uv:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

4. Install dependencies:
```bash
uv pip install -e .
```

5. Create a `.env` file in the project root:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
```

## Usage

1. Start the application:
run the below command from directory `language-listening-app/`
```bash
streamlit run frontend/app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Enter a YouTube URL and select your preferred model (Ollama or Bedrock)

4. Generate questions and practice your listening comprehension

## Project Structure

```
language-listening-app/
├── frontend/           # Streamlit UI components
├── backend/           # Core processing logic
├── config/           # Configuration files
├── models/           # Data models
├── utils/            # Utility functions
└── data/             # Vector store data
```

## Development

- Use `uv pip install -e ".[dev]"` to install development dependencies
- Run tests with `pytest`
- Format code with `ruff format .`
- Lint code with `ruff check .`

## License

MIT License 