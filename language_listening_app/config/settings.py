import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Ollama Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_OLLAMA_MODEL = "mistral:latest"

# Vector Store Configuration
CHROMA_PERSIST_DIR = "data/chroma"
CHROMA_COLLECTION_NAME = "language_learning"
VECTOR_STORE_DIR = CHROMA_PERSIST_DIR
COLLECTION_NAME = CHROMA_COLLECTION_NAME

# Text Processing Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

# Question Generation Configuration
QUESTION_TYPES = ["comprehension", "detail", "inference"]
DEFAULT_NUM_QUESTIONS = 5
SIMILARITY_THRESHOLD = 0.8

# Model Configuration
DEFAULT_MODEL = "mistral:latest"  # For Ollama
BEDROCK_MODEL = "amazon.nova-micro-v1:0"  # For AWS Bedrock
DEFAULT_BEDROCK_MODEL = BEDROCK_MODEL  # Add this line to match the import in llm_manager.py

# Supported Languages
SUPPORTED_LANGUAGES = ["ja", "en", "ko", "zh"]

# Configuration dictionary
_config = {
    "aws": {
        "access_key_id": AWS_ACCESS_KEY_ID,
        "secret_access_key": AWS_SECRET_ACCESS_KEY,
        "region": AWS_REGION
    },
    "ollama": {
        "api_url": OLLAMA_API_URL,
        "default_model": DEFAULT_OLLAMA_MODEL
    },
    "vector_store": {
        "persist_dir": CHROMA_PERSIST_DIR,
        "collection_name": CHROMA_COLLECTION_NAME
    },
    "text_processing": {
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP
    },
    "question_generation": {
        "types": QUESTION_TYPES,
        "default_num": DEFAULT_NUM_QUESTIONS,
        "similarity_threshold": SIMILARITY_THRESHOLD
    },
    "models": {
        "default": DEFAULT_MODEL,
        "bedrock": BEDROCK_MODEL,
        "default_bedrock": DEFAULT_BEDROCK_MODEL
    },
    "languages": SUPPORTED_LANGUAGES
}

def load_config():
    """Load and return the configuration"""
    return _config

def get_config():
    """Get the current configuration"""
    return _config 