import sqlite3
import redis
import json
import time
from typing import Optional, List, Dict

class DatabaseWithCache:
    def __init__(self, db_name="demo.db", redis_host="localhost", redis_port=6379):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        try:
            self.redis_client.ping()
            print("Connected to Redis")
        except redis.ConnectionError:
            print("Failed to connect to Redis")
            raise

        self._setup_database()

    def _setup_database(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                city TEXT NOT NULL,
                age INTEGER,
                views INTEGER DEFAULT 0
            )
        """)

        self.cursor.execute("SELECT COUNT(*) FROM users")
        count = self.cursor.fetchone()[0]

        if count == 0:
            print("Populating database with sample data...")
            sample_users = [
                (1, "Alice Johnson", "alice@example.com", "New York", 28),
                (2, "Bob Smith", "bob@example.com", "Los Angeles", 34),
                (3, "Carol White", "carol@example.com", "Chicago", 25),
                (4, "David Brown", "david@example.com", "Houston", 31),
                (5, "Eve Davis", "eve@example.com", "Phoenix", 29),
                (6, "Frank Wilson", "frank@example.com", "New York", 27),
                (7, "Grace Lee", "grace@example.com", "San Francisco", 33),
                (8, "Henry Martinez", "henry@example.com", "Seattle", 30),
                (9, "Iris Taylor", "iris@example.com", "Boston", 26),
                (10, "Jack Anderson", "jack@example.com", "Austin", 35),
            ]
            self.cursor.executemany(
                "INSERT INTO users (id, name, email, city, age) VALUES (?, ?, ?, ?, ?)",
                sample_users
            )
            self.conn.commit()
            print(f"Inserted {len(sample_users)} users")

    def get_user_by_id_no_cache(self, user_id):
        time.sleep(0.1)
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = self.cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_user_by_id_with_cache(self, user_id, ttl=300):
        cache_key = f"user:{user_id}"
        cached_data = self.redis_client.get(cache_key)

        if cached_data:
            print(f"  CACHE HIT for user {user_id}")
            return json.loads(cached_data)

        print(f"  CACHE MISS for user {user_id} - querying database")
        time.sleep(0.1)
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = self.cursor.fetchone()

        if row:
            user_data = dict(row)
            self.redis_client.setex(cache_key, ttl, json.dumps(user_data))
            print(f"  Cached user {user_id} for {ttl} seconds")
            return user_data

        return None

    def get_users_by_city(self, city, use_cache=True, ttl=300):
        cache_key = f"users:city:{city}"

        if use_cache:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                print(f"  CACHE HIT for city '{city}'")
                return json.loads(cached_data)
            print(f"  CACHE MISS for city '{city}'")

        time.sleep(0.15)
        self.cursor.execute("SELECT * FROM users WHERE city = ?", (city,))
        rows = self.cursor.fetchall()
        users = [dict(row) for row in rows]

        if use_cache:
            self.redis_client.setex(cache_key, ttl, json.dumps(users))
            print(f"  Cached {len(users)} users for city '{city}'")

        return users

    def invalidate_user_cache(self, user_id):
        cache_key = f"user:{user_id}"
        result = self.redis_client.delete(cache_key)
        if result:
            print(f"Invalidated cache for user {user_id}")
        else:
            print(f"No cache entry found for user {user_id}")

    def clear_all_cache(self):
        self.redis_client.flushdb()
        print("Cleared all cache data")

    def increment_post_views(self, post_id):
        key = f"views:post:{post_id}"
        views = self.redis_client.incr(key)

        if views % 10 == 0:
            self.cursor.execute("UPDATE users SET views = ? WHERE id = ?", (views, post_id))
            self.conn.commit()
            print("Synced views to database")

        return views

    def get_cache_stats(self):
        info = self.redis_client.info('stats')
        keys = self.redis_client.dbsize()
        print(f"\nCache Statistics:")
        print(f"  Cached keys: {keys}")
        print(f"  Total connections: {info.get('total_connections_received', 'N/A')}")
        print(f"  Commands processed: {info.get('total_commands_processed', 'N/A')}")

    def close(self):
        self.conn.close()
        self.redis_client.close()


def run_demo():
    print("=" * 60)
    print("REDIS CACHING DEMO")
    print("=" * 60 + "\n")

    db = DatabaseWithCache()

    print("\n" + "=" * 60)
    print("DEMO 1: Single User Query Performance")
    print("=" * 60)

    print("\n[Without Cache]")
    start = time.time()
    for i in range(3):
        user = db.get_user_by_id_no_cache(1)
        print(f"Query {i+1}: {user['name']}")
    no_cache_time = time.time() - start
    print(f"Total time: {no_cache_time:.3f} seconds")

    print("\n[With Cache]")
    db.clear_all_cache()
    start = time.time()
    for i in range(3):
        user = db.get_user_by_id_with_cache(1)
        print(f"Query {i+1}: {user['name']}")
    cache_time = time.time() - start
    print(f"Total time: {cache_time:.3f} seconds")
    print(f"\nSpeedup: {no_cache_time/cache_time:.1f}x faster with cache")

    print("\n" + "=" * 60)
    print("DEMO 2: Multiple Different Users")
    print("=" * 60)

    db.clear_all_cache()
    user_ids = [1, 2, 3, 4, 5]

    print("\n[First access - all cache misses]")
    start = time.time()
    for uid in user_ids:
        user = db.get_user_by_id_with_cache(uid)
    first_time = time.time() - start
    print(f"Time: {first_time:.3f} seconds")

    print("\n[Second access - all cache hits]")
    start = time.time()
    for uid in user_ids:
        user = db.get_user_by_id_with_cache(uid)
    second_time = time.time() - start
    print(f"Time: {second_time:.3f} seconds")
    print(f"\nSecond run was {first_time/second_time:.1f}x faster")

    print("\n" + "=" * 60)
    print("DEMO 3: Complex Query - Users by City")
    print("=" * 60)

    db.clear_all_cache()
    city = "New York"

    print(f"\n[First query for '{city}']")
    start = time.time()
    users = db.get_users_by_city(city)
    first_query = time.time() - start
    print(f"Found {len(users)} users in {first_query:.3f} seconds")

    print(f"\n[Second query for '{city}' (cached)]")
    start = time.time()
    users = db.get_users_by_city(city)
    second_query = time.time() - start
    print(f"Found {len(users)} users in {second_query:.3f} seconds")
    print(f"\n{first_query/second_query:.1f}x faster with cache")

    print("\n" + "=" * 60)
    print("DEMO 4: Cache Invalidation")
    print("=" * 60)

    print("\n[Access user 1 to cache it]")
    user = db.get_user_by_id_with_cache(1)

    print("\n[Invalidate user 1 cache]")
    db.invalidate_user_cache(1)

    print("\n[Access user 1 again - should be cache miss]")
    user = db.get_user_by_id_with_cache(1)

    db.get_cache_stats()

    print("\n" + "=" * 60)
    print("DEMO 5: Testing View Counter")
    print("=" * 60)

    db.clear_all_cache()
    print("=== Testing View Counter ===")
    for i in range(1, 26):
        total_views = db.increment_post_views(1)
        if i <= 3 or (i >= 10 and i <= 11) or (i >= 20 and i <= 21) or i == 25:
            print(f"View #{i}: Total views = {total_views}")
        elif i == 4 or i == 12 or i == 22:
            print("...")

    print("\n" + "=" * 60)
    db.close()
    print("Demo completed successfully!")


if __name__ == "__main__":
    run_demo()