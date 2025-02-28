import os
import redis
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import Redis as LangchainRedis
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

# Initialize the embedding model
model_name = "BAAI/bge-small-en-v1.5"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': True}
hf_embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

# Connect to Redis directly to check data
r = redis.Redis(host='localhost', port=6379, decode_responses=False)
print(f"Direct Redis connection: {r.ping()}")
print(f"Keys in Redis: {r.keys('*')}")

# Create a langchain Redis client
redis_url = "redis://localhost:6379"
index_name = "chatqna_index"

# Create the Redis vector store
redis_vectorstore = LangchainRedis(
    redis_url=redis_url,
    index_name=index_name,
    embedding=hf_embeddings
)

# Add some test documents
print("\nAdding documents to Redis using langchain...")
texts = [
    "Python is a high-level programming language known for its simplicity and readability.",
    "Python is widely used in data science, machine learning, and artificial intelligence.",
    "Python has a large ecosystem of libraries including NumPy, Pandas, and TensorFlow.",
    "Python was created by Guido van Rossum and was first released in 1991.",
    "Python's name comes from Monty Python, not from the snake."
]

# Add documents to Redis
redis_vectorstore.add_texts(texts)

# Search for documents
print("\nSearching for documents...")
query = "What is Python programming?"
results = redis_vectorstore.similarity_search(query, k=4)

# Print results
print("\nSearch results:")
for i, doc in enumerate(results):
    print(f"{i+1}. {doc.page_content}")

# Now test the retriever service with the same data
import requests
import json

# Get embedding for the query
print("\nTesting retriever service...")
query_text = "What is Python?"
st_model = SentenceTransformer('BAAI/bge-small-en-v1.5')
query_embedding = st_model.encode(query_text).tolist()

# Simple request with minimal parameters
simple_payload = {
    "input": query_text,
    "text": query_text,
    "search_type": "similarity",
    "k": 4,
    "request_type": "retrieval",
    "embedding": query_embedding,
    "retriever_type": "redis",
    "redis_config": {
        "redis_url": "redis://redis:6379",
        "index_name": "chatqna_index"
    }
}

print(f"Sending request to retriever service...")
try:
    response = requests.post(
        "http://localhost:7001/v1/retrieval",
        json=simple_payload,
        timeout=30
    )
    
    print(f"Status code: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Parse the response if it's valid JSON
    if response.status_code == 200:
        try:
            result = response.json()
            if "retrieved_docs" in result and result["retrieved_docs"]:
                print("\nRetrieved documents:")
                for i, doc in enumerate(result["retrieved_docs"]):
                    print(f"{i+1}. Text: {doc.get('text', 'N/A')}")
            else:
                print("\nNo documents retrieved from the service.")
        except json.JSONDecodeError:
            print("Response is not valid JSON")
except Exception as e:
    print(f"Error making request to retriever service: {e}") 