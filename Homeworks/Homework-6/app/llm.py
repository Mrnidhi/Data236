import requests
import json
import math
from app.config import config

def call_ollama(prompt: str, json_format: bool = False) -> str:
    url = f"{config.OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": config.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    if json_format:
        payload["format"] = "json"
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        print(f"[Ollama Error] {e}")
        return ""

def embed_text(text: str) -> list:
    """Generate embedding vector using local Ollama for cosine similarity search."""
    url = f"{config.OLLAMA_BASE_URL}/api/embeddings"
    payload = {"model": config.OLLAMA_MODEL, "prompt": text}
    try:
        response = requests.post(url, json=payload, timeout=20)
        response.raise_for_status()
        return response.json().get("embedding", [])
    except Exception as e:
        print(f"[Ollama Embedding Error] {e}")
        return []

def cosine_similarity(v1: list, v2: list) -> float:
    """Compare two embedding vectors — used for episodic memory retrieval."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)

def extract_memory_data(user_msg: str, ai_response: str) -> dict:
    """Extract up to 3 structured facts from a student message for episodic storage."""
    extraction_prompt = f"""You are a memory extraction assistant for a study app.
Analyze ONLY the student's message below and extract structured learning data.

Student message: "{user_msg}"
AI response (for context only): "{ai_response}"

Return ONLY a valid JSON object with these exact keys (empty list if nothing found):
{{
  "topics_studied":  ["specific subjects or topics the student said they are studying"],
  "difficult_areas": ["topics the student explicitly said they struggle with"],
  "learning_goals":  ["explicit goals or targets the student mentioned"]
}}

Rules:
- Extract from the STUDENT message only
- Be specific: "Linked Lists" not "programming"
- Return [] for any field with nothing to extract
- Return ONLY valid JSON
"""
    raw = call_ollama(extraction_prompt, json_format=True)
    try:
        if raw:
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()
            return json.loads(raw)
    except json.JSONDecodeError:
        pass
    return {"topics_studied": [], "difficult_areas": [], "learning_goals": []}
