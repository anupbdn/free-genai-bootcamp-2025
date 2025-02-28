import redis
import numpy as np
from redis.commands.search.query import Query

# Try to connect to Redis using different URLs
print("Testing Redis connections...")

# Try with redis:6379
try:
    r1 = redis.Redis(host="redis", port=6379, decode_responses=False)
    print(f"Connection to redis:6379: {r1.ping()}")
    print(f"Keys in redis:6379: {r1.keys('doc:*')}")
    print(f"Index exists: {r1.ft('chatqna_index').info() is not None}")
except Exception as e:
    print(f"Error connecting to redis:6379: {e}")

# Try with chatqna-redis-1:6379
try:
    r2 = redis.Redis(host="chatqna-redis-1", port=6379, decode_responses=False)
    print(f"Connection to chatqna-redis-1:6379: {r2.ping()}")
    print(f"Keys in chatqna-redis-1:6379: {r2.keys('doc:*')}")
    print(f"Index exists: {r2.ft('chatqna_index').info() is not None}")
except Exception as e:
    print(f"Error connecting to chatqna-redis-1:6379: {e}")

# Try with localhost:6379
try:
    r3 = redis.Redis(host="localhost", port=6379, decode_responses=False)
    print(f"Connection to localhost:6379: {r3.ping()}")
    print(f"Keys in localhost:6379: {r3.keys('doc:*')}")
    print(f"Index exists: {r3.ft('chatqna_index').info() is not None}")
except Exception as e:
    print(f"Error connecting to localhost:6379: {e}")

# Try with 172.18.0.3:6379 (Redis container IP)
try:
    r4 = redis.Redis(host="172.18.0.3", port=6379, decode_responses=False)
    print(f"Connection to 172.18.0.3:6379: {r4.ping()}")
    print(f"Keys in 172.18.0.3:6379: {r4.keys('doc:*')}")
    print(f"Index exists: {r4.ft('chatqna_index').info() is not None}")
except Exception as e:
    print(f"Error connecting to 172.18.0.3:6379: {e}")

# If any connection worked, try a search
for r, name in [(r1, "redis:6379"), (r2, "chatqna-redis-1:6379"), (r3, "localhost:6379"), (r4, "172.18.0.3:6379")]:
    try:
        # Create a dummy vector for search
        dummy_vector = np.zeros(384, dtype=np.float32).tobytes()
        
        # Prepare vector search query
        q = Query(
            f"*=>[KNN 4 @embedding $vec_param AS score]"
        ).dialect(2)
        
        # Execute search
        results = r.ft("chatqna_index").search(
            q,
            query_params={
                "vec_param": dummy_vector
            }
        )
        
        print(f"Search with {name} found {len(results.docs)} results")
        
        # Break after first successful search
        if len(results.docs) > 0:
            break
    except Exception as e:
        print(f"Search error with {name}: {e}") 