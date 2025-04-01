from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from sentence_transformers import SentenceTransformer
import requests
import numpy as np
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Pydantic models for requests
class QueryRequest(BaseModel):
    question: str

class IngestRequest(BaseModel):
    url: str

# Initialize embedding model and SQLite database
model = SentenceTransformer('all-MiniLM-L6-v2')
conn = sqlite3.connect('/app/data/text_data.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS chunks (id INTEGER PRIMARY KEY, text TEXT, embedding BLOB)')

# Constants
OLLAMA_MODEL = "llama3.2"

def embed_text(text):
    """Generate embedding for a text chunk."""
    return model.encode(text).tobytes()

def check_ollama_connection():
    """Check if Ollama is accessible and log the result."""
    ollama_url = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get("models", [])
        model_names = [m.get("name") for m in models]
        logger.info(f"Successfully connected to Ollama at {ollama_url}")
        logger.info(f"Available models: {model_names}")
        if OLLAMA_MODEL not in model_names:
            logger.warning(f"Warning: {OLLAMA_MODEL} not found in available models: {model_names}")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Ollama at {ollama_url}: {str(e)}")
        return False

@app.post("/v1/dataprep/ingest")
async def ingest_text(request: IngestRequest):
    """Ingest text from a URL and store chunks with embeddings."""
    try:
        logger.info(f"Ingesting from URL: {request.url}")
        response = requests.get(request.url)
        text = response.text
        # Simple chunking: split into 500-character segments
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]
        for chunk in chunks:
            embedding = embed_text(chunk)
            cursor.execute('INSERT INTO chunks (text, embedding) VALUES (?, ?)', (chunk, embedding))
        conn.commit()
        return {"status": "success", "message": f"Ingested {len(chunks)} chunks"}
    except Exception as e:
        logger.error(f"Ingestion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/v1/chatqna")
async def query_text(request: QueryRequest):
    """Answer a question based on ingested text using Ollama."""
    try:
        # Log the incoming question
        logger.info(f"Received question: {request.question}")
        
        # Check Ollama connection first
        if not check_ollama_connection():
            raise HTTPException(status_code=503, detail="Ollama service not accessible")
        
        # Embed the question
        question_embedding = embed_text(request.question)
        
        # Fetch all stored chunks
        cursor.execute('SELECT text, embedding FROM chunks')
        rows = cursor.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="No text ingested yet")
        
        # Find the most relevant chunk
        best_match = max(
            rows,
            key=lambda row: np.dot(
                np.frombuffer(row[1], dtype=np.float32),
                np.frombuffer(question_embedding, dtype=np.float32)
            )
        )
        logger.info("Found best matching chunk")
        
        # Query Ollama with the best-matching chunk
        ollama_url = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
        prompt = f"Based on this text: {best_match[0]}\nAnswer this question: {request.question}"
        
        logger.info(f"Sending request to Ollama at {ollama_url}")
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        
        answer = response.json()["response"]
        logger.info(f"Received answer from Ollama: {answer[:100]}...")  # Log first 100 chars
        return {"answer": answer}
        
    except requests.exceptions.RequestException as e:
        error_detail = {
            "error": str(e),
            "url": f"{ollama_url}/api/generate",
            "response_status": getattr(getattr(e, 'response', None), 'status_code', None),
            "response_text": getattr(getattr(e, 'response', None), 'text', None)
        }
        logger.error(f"Ollama request failed: {json.dumps(error_detail)}")
        raise HTTPException(status_code=500, detail=f"Ollama query failed: {json.dumps(error_detail)}")
    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.get("/v1/dataprep/get")
async def get_files():
    """Get list of ingested files."""
    try:
        cursor.execute('SELECT COUNT(*) FROM chunks')
        count = cursor.fetchone()[0]
        return {"status": "success", "chunks_count": count}
    except Exception as e:
        logger.error(f"Failed to get files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get files: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint that also checks Ollama connection."""
    ollama_status = "connected" if check_ollama_connection() else "not connected"
    return {
        "status": "healthy",
        "ollama_status": ollama_status,
        "model": OLLAMA_MODEL
    }