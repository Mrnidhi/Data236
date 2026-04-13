import redis
import time
import json
import numpy as np
import ollama
from sentence_transformers import SentenceTransformer

class LLMCache:
    def __init__(self, host='localhost', port=6379, sim_threshold=0.85):
        self.r = redis.Redis(host=host, port=port, decode_responses=False)
        self.r.ping()
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.threshold = sim_threshold
        self.cache_key = "semantic_cache_entries"

    def _embed(self, text):
        return self.encoder.encode(text, convert_to_numpy=True).astype(np.float32)

    def _cosine_sim(self, a, b):
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def search_cache(self, query):
        emb = self._embed(query)
        raw = self.r.get(self.cache_key)
        if not raw:
            return None, 0.0

        entries = json.loads(raw)
        best_sim, best_ans = 0.0, None
        for entry in entries:
            cached_emb = np.array(entry["emb"], dtype=np.float32)
            sim = self._cosine_sim(emb, cached_emb)
            if sim > best_sim:
                best_sim = sim
                best_ans = entry["ans"]

        if best_sim >= self.threshold:
            return best_ans, best_sim
        return None, best_sim

    def add_to_cache(self, query, ans):
        emb = self._embed(query).tolist()
        raw = self.r.get(self.cache_key)
        entries = json.loads(raw) if raw else []
        entries.append({"q": query, "emb": emb, "ans": ans})
        self.r.set(self.cache_key, json.dumps(entries))


def run_query(query, cache):
    t0 = time.time()
    ans, sim = cache.search_cache(query)

    if ans:
        cached = True
        print(f"CACHE HIT! sim={sim:.3f}")
    else:
        cached = False
        print(f"CACHE MISS! sim={sim:.3f}, calling ollama...")
        try:
            res = ollama.chat(model='llama3.2', messages=[{"role": "user", "content": query}])
            ans = res['message']['content']
        except Exception as e:
            ans = f"err: {e}"
            return ans, cached, time.time() - t0
        cache.add_to_cache(query, ans)

    return ans, cached, time.time() - t0


if __name__ == "__main__":
    cache = LLMCache()
    cache.r.delete("semantic_cache_entries")

    tests = [
        "What is the capital of Japan?",
        "What is the capital of Japan?",
        "Tell me the capital city of Japan.",
        "How large is the sun?",
        "What is the size of our sun?",
        "What is 2 + 2?",
        "Translate 'hello' to French.",
        "How do you say 'hello' in French?",
        "Who wrote the play Romeo and Juliet?",
        "Who is the author of Romeo and Juliet?"
    ]

    stats = {"hit": 0, "miss": 0, "hit_time": 0.0, "miss_time": 0.0}

    for i, q in enumerate(tests):
        print(f"\n--- Q{i+1}: {q} ---")
        out, hit, t = run_query(q, cache)
        print(f"took {t:.3f}s")

        if hit:
            stats["hit"] += 1
            stats["hit_time"] += t
        else:
            stats["miss"] += 1
            stats["miss_time"] += t

    print("\n=== SUMMARY METRICS ===")
    total = stats["hit"] + stats["miss"]
    print(f"Total Queries: {total}")
    if total > 0:
        print(f"Cache Hit Rate: {(stats['hit']/total)*100:.1f}%")
    avg_hit = stats["hit_time"] / stats["hit"] if stats["hit"] else 0
    avg_miss = stats["miss_time"] / stats["miss"] if stats["miss"] else 0
    print(f"Avg Cache time: {avg_hit:.4f}s")
    print(f"Avg Ollama time: {avg_miss:.4f}s")
    if avg_hit > 0:
        print(f"Speedup: {avg_miss/avg_hit:.1f}x")
