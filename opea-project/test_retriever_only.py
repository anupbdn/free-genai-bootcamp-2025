import requests
import json
from sentence_transformers import SentenceTransformer

# Get embedding for the query
print("Testing retriever service...")
query_text = "What is Python?"
st_model = SentenceTransformer('BAAI/bge-small-en-v1.5')
query_embedding = st_model.encode(query_text).tolist()

# Simple request with minimal parameters - using the correct index name and search_type
simple_payload = {
    "input": query_text,
    "text": query_text,
    "search_type": "similarity",  # This is a valid search type
    "k": 4,
    "request_type": "retrieval",
    "embedding": query_embedding,
    "retriever_type": "redis",
    "redis_config": {
        "redis_url": "redis://redis:6379",
        "index_name": "rag_redis"  # This is the default index name from config.py
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
    print(f"Response headers: {response.headers}")
    print(f"Response body: {response.text}")
    
    # Parse the response if it's valid JSON
    if response.status_code == 200:
        try:
            result = response.json()
            if "retrieved_docs" in result and result["retrieved_docs"]:
                print("\nRetrieved documents:")
                for i, doc in enumerate(result["retrieved_docs"]):
                    print(f"{i+1}. Text: {doc.get('text', 'N/A')}")
                    print(f"   Score: {doc.get('score', 'N/A')}")
                    print(f"   Metadata: {doc.get('metadata', 'N/A')}")
                    print("---")
            else:
                print("\nNo documents retrieved from the service.")
        except json.JSONDecodeError:
            print("Response is not valid JSON")
except Exception as e:
    print(f"Error making request to retriever service: {e}") 