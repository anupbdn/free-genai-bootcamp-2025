import os
import redis
from langchain_community.vectorstores import Redis as LangchainRedis
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

# Initialize the embedding model
print("Initializing embedding model...")
model_name = "BAAI/bge-small-en-v1.5"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': True}
hf_embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

# First, clear any existing data in Redis
print("Clearing existing data in Redis...")
r = redis.Redis(host='localhost', port=6379, decode_responses=False)
for key in r.keys("doc:*"):
    r.delete(key)
for key in r.keys("*:*"):  # LangChain uses a different prefix
    r.delete(key)

# Try to drop existing indices
try:
    r.ft('chatqna_index').dropindex()
    print("Dropped existing chatqna_index")
except:
    print("No chatqna_index to drop")

try:
    r.ft('rag_redis').dropindex()
    print("Dropped existing rag_redis index")
except:
    print("No rag_redis index to drop")

# Create a langchain Redis client with the index name used by the retriever service
print("\nCreating LangChain Redis client...")
redis_url = "redis://localhost:6379"
index_name = "rag_redis"  # Use the default index name from config.py

# Create the Redis vector store
redis_vectorstore = LangchainRedis(
    redis_url=redis_url,
    index_name=index_name,
    embedding=hf_embeddings
)

# Add some test documents
print("\nAdding documents to Redis using LangChain...")
texts = [
    "Python is a high-level programming language known for its simplicity and readability.",
    "Python is widely used in data science, machine learning, and artificial intelligence.",
    "Python has a large ecosystem of libraries including NumPy, Pandas, and TensorFlow.",
    "Python was created by Guido van Rossum and was first released in 1991.",
    "Python's name comes from Monty Python, not from the snake."
]

# Add documents to Redis
ids = redis_vectorstore.add_texts(texts)
print(f"Added {len(ids)} documents with IDs: {ids}")

# Verify the data was added
print("\nVerifying data in Redis...")
print(f"Keys in Redis: {r.keys('*')}")

# Try to get info about the index
try:
    index_info = r.ft(index_name).info()
    print(f"\nIndex info for {index_name}:")
    print(f"Number of docs: {index_info['num_docs']}")
    print(f"Index definition: {index_info['index_definition']}")
except Exception as e:
    print(f"Error getting index info: {e}")

print("\nDone! Now try running the test_retriever_only.py script again.") 