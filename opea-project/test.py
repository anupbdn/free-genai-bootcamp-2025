import requests
import json
import redis
import numpy as np
from redis.commands.search.field import VectorField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from sentence_transformers import SentenceTransformer

def init_redis_index():
    """Initialize Redis with proper index"""
    # Connect to Redis - use localhost since the container port is mapped
    r = redis.Redis(host='localhost', port=6379, decode_responses=False)
    
    # Delete existing index if it exists
    try:
        r.ft('chatqna_index').dropindex()
        print("Dropped existing index")
    except:
        pass
    
    # Create new index with metadata field
    schema = (
        TextField("text"),
        TextField("metadata"),  # Add metadata field
        TextField("distance"),  # Add distance field
        VectorField("embedding", 
                   "FLAT", 
                   {
                       "TYPE": "FLOAT32",
                       "DIM": 384,
                       "DISTANCE_METRIC": "COSINE"
                   })
    )
    
    # Create the index
    r.ft('chatqna_index').create_index(
        schema,
        definition=IndexDefinition(prefix=["doc:"], index_type=IndexType.HASH)
    )
    print("Created new index")
    return r

def get_embedding(text):
    """
    Get embedding for the given text using the BAAI/bge-small-en-v1.5 model.
    This model produces 384-dimensional embeddings which match the Redis index configuration.
    """
    # Initialize the model
    model = SentenceTransformer('BAAI/bge-small-en-v1.5')
    
    # Get the embedding
    embedding = model.encode(text).tolist()
    
    return embedding

def add_document(r, text, embedding, doc_id):
    """Add document directly to Redis"""
    # Convert embedding to numpy array and then to bytes
    embedding_array = np.array(embedding, dtype=np.float32)
    embedding_bytes = embedding_array.tobytes()
    
    # Store document in Redis
    try:
        r.hset(
            f"doc:{doc_id}",
            mapping={
                "text": text.encode('utf-8') if isinstance(text, str) else text,
                "embedding": embedding_bytes,
                "distance": "0.0".encode('utf-8'),  # Add default distance
                "metadata": "{}".encode('utf-8')  # Add empty metadata
            }
        )
        print(f"Added document {doc_id}: {text}")
    except Exception as e:
        print(f"Error adding document {doc_id}: {e}")

def search_documents(r, query_text, k=4):
    """Search for documents using Redis directly"""
    # Get embedding for query
    query_embedding = get_embedding(query_text)
    query_vector = np.array(query_embedding, dtype=np.float32).tobytes()
    
    # Prepare vector search query
    q = Query(
        f"*=>[KNN {k} @embedding $vec_param AS score]"
    ).dialect(2)
    
    # Execute search
    try:
        results = r.ft('chatqna_index').search(
            q,
            query_params={
                "vec_param": query_vector
            }
        )
        
        # Format results
        docs = []
        for doc in results.docs:
            docs.append({
                "text": doc.text.decode('utf-8') if isinstance(doc.text, bytes) else doc.text,
                "score": float(doc.score) if hasattr(doc, 'score') else 0.0
            })
        
        return docs
    except Exception as e:
        print(f"Search error: {e}")
        return []

def test_retriever_service(redis_client, index_name):
    """Test the retriever service."""
    print("\nTesting retriever service...\n")
    
    # Get embedding for the query
    query_text = "What is Python?"
    query_embedding = get_embedding(query_text)
    
    # Simple request with minimal parameters
    simple_payload = {
        "input": query_text,
        "text": query_text,  # Add text field explicitly
        "search_type": "similarity",
        "k": 4,
        "request_type": "retrieval",
        "embedding": query_embedding,
        "retriever_type": "redis",  # Add retriever_type back
        "redis_config": {
            "redis_url": "redis://chatqna-redis-1:6379",  # Use the full container name
            "index_name": "chatqna_index"
        }
    }
    
    print(f"Trying simple request: {json.dumps(simple_payload, indent=2)}")
    
    # Make the request to the retriever service
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
                        print(f"{i+1}. Score: {doc.get('score', 'N/A')} | Text: {doc.get('text', 'N/A')}")
                else:
                    print("\nNo documents retrieved from the service.")
                    
                    # Try a direct Redis search as a comparison
                    print("\nComparing with direct Redis search:")
                    direct_results = search_documents(redis_client, query_text)
                    if direct_results:
                        print("Direct Redis search found results:")
                        for i, result in enumerate(direct_results):
                            print(f"{i+1}. Score: {result['score']:.4f} | Text: {result['text']}")
                    else:
                        print("Direct Redis search also found no results.")
            except json.JSONDecodeError:
                print("Response is not valid JSON")
    except Exception as e:
        print(f"Error making request to retriever service: {e}")
    
    # Verify that Redis has the data we expect
    print("\nVerifying Redis data:")
    print(f"1. Index exists: {redis_client.ft(index_name).info() is not None}")
    print(f"2. Number of docs: {len(redis_client.keys('doc:*'))}")
    
    # Check the structure of a document
    if redis_client.keys('doc:*'):
        doc_key = redis_client.keys('doc:*')[0]
        doc = redis_client.hgetall(doc_key)
        print(f"3. Document structure: {dict((k, type(v)) for k, v in doc.items())}")
        
        # Try to verify the embedding dimensions
        if b'embedding' in doc:
            embedding_bytes = doc[b'embedding']
            embedding_array = np.frombuffer(embedding_bytes, dtype=np.float32)
            print(f"4. Embedding dimensions: {embedding_array.shape}")
            
    # Try another approach with a different Redis URL
    print("\nTrying alternative Redis URL...")
    alternative_payload = simple_payload.copy()
    alternative_payload["redis_config"]["redis_url"] = "redis://redis:6379"
    
    try:
        response = requests.post(
            "http://localhost:7001/v1/retrieval",
            json=alternative_payload,
            timeout=30
        )
        
        print(f"Status code: {response.status_code}")
        print(f"Response body: {response.text[:200]}...")  # Show just the beginning
    except Exception as e:
        print(f"Error with alternative URL: {e}")

if __name__ == "__main__":
    # Initialize Redis connection and index
    print("Initializing Redis...")
    redis_client = init_redis_index()
    
    # Add test documents
    test_docs = [
    "Python is a high-level programming language known for its simplicity and readability.",
    "Python is widely used in data science, machine learning, and artificial intelligence.",
    "Python has a large ecosystem of libraries including NumPy, Pandas, and TensorFlow.",
    "Python was created by Guido van Rossum and was first released in 1991.",
    "Python's name comes from Monty Python, not from the snake."
    ]
    
    print("\nAdding documents...")
    for i, doc in enumerate(test_docs):
        embedding = get_embedding(doc)
        add_document(redis_client, doc, embedding, i)
    
    # Test search
    print("\nTesting search...")
    query = "What is Python programming?"
    results = search_documents(redis_client, query)
    
    # Print results with better formatting
    print("\nSearch results:")
    if results:
        for result in results:
            print(f"Score: {result['score']:.4f} | Text: {result['text']}")
    else:
        print("No results found")
    
    # Verify Redis contents
    print("\nRedis keys:", redis_client.keys("doc:*"))
    
    # Add test for retriever service
    print("\nTesting retriever service...")
    test_retriever_service(redis_client, "chatqna_index")