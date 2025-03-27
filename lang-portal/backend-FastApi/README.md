# Language Learning Portal Backend

A FastAPI-based backend service for a language learning portal that serves as:
- Vocabulary inventory management
- Learning Record Store (LRS)
- Unified launchpad for learning apps

## Quick Start



### Starting the Application

1. **Install Dependencies**:
   ```bash
   uv pip install -e .
   ```

2. **Initialize Database and Seed Data** (Optional - only if starting fresh):
   ```bash
   ./setup.sh
   ```

3. **Start the FastAPI Server**:

We can use uv environment 'language-learning-api' , Make sure you go to path : '/Users/anupb/gen-ai-bootcamp-2025/free-genai-bootcamp-2025/lang-portal/backend-FastApi'

   ```bash
   PYTHONPATH=. uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`

Interactive API documentation (Swagger UI) is available at `http://localhost:8000/docs`

## API Endpoints

You can refer more about API endpoints in [Backend Technical Specifications](Backend-Technical-Specs.md)
