# ChatQNA with Ollama

A simple question-answering system that uses semantic search and Ollama LLM to answer questions based on ingested documents. This proof-of-concept demonstrates the integration of OPEA (Open Enterprise AI) components for document processing and question answering.

## Overview

This application allows users to:
1. Ingest documents (via URLs)
2. Process and chunk the documents
3. Generate embeddings for semantic search
4. Ask questions about the ingested content
5. Get AI-powered answers using Ollama LLM

## OPEA Components Used

1. **Document Processing**
   - Sentence Transformers for text embeddings
   - SQLite for document storage
   - Text chunking for better context management

2. **LLM Integration**
   - Ollama integration for local LLM inference
   - Model: llama3.2

3. **UI Components**
   - OPEA ChatQNA UI for user interaction
   - FastAPI backend for API endpoints

## Prerequisites

- Docker and Docker Compose
- Ollama running locally with llama3.2 model
  ```bash
  # Install Ollama and run the model
  ollama run llama3.2
  ```

## Setup and Running

1. Start Ollama locally (make sure it's running on port 11434)

2. Build and run the application:
   ```bash
   docker-compose up -d
   ```

3. The services will be available at:
   - UI: http://localhost:8080
   - Backend API: http://localhost:8080/v1/
   - Health Check: http://localhost:8080/health

## Testing the Backend (API Only)

1. Check if the service is healthy:
   ```bash
   curl http://localhost:8080/health
   ```

2. Ingest a document:
   ```bash
   curl -X POST http://localhost:8080/v1/dataprep/ingest \
     -H "Content-Type: application/json" \
     -d '{"url": "https://raw.githubusercontent.com/ollama/ollama/main/README.md"}'
   ```

3. Check ingested documents:
   ```bash
   curl http://localhost:8080/v1/dataprep/get
   ```

4. Ask a question:
   ```bash
   curl -X POST http://localhost:8080/v1/chatqna \
     -H "Content-Type: application/json" \
     -d '{"question": "What is Ollama?"}'
   ```

## Testing with UI

1. Open http://localhost:8080 in your browser

2. Ingest a document:
   - Click on the "Upload" or "Ingest" button
   - Provide a URL to ingest (e.g., Ollama's README)

3. Ask questions:
   - Type your question in the chat input
   - Press enter or click send
   - The UI will display the answer from the LLM

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   ChatQNA   │     │   FastAPI    │     │   Ollama    │
│     UI      │────▶│   Backend    │────▶│    LLM      │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                    ┌──────┴───────┐
                    │   SQLite DB  │
                    │  (Vectors)   │
                    └──────────────┘
```

## API Endpoints

- `POST /v1/dataprep/ingest`: Ingest documents
- `GET /v1/dataprep/get`: List ingested documents
- `POST /v1/chatqna`: Ask questions
- `GET /health`: Service health check

## Troubleshooting

1. If Ollama is not accessible:
   - Ensure Ollama is running: `ollama list`
   - Check if llama3.2 is installed: `ollama pull llama3.2`

2. If the UI can't connect to the backend:
   - Check if all containers are running: `docker ps`
   - Check container logs: `docker logs simple-backend`
