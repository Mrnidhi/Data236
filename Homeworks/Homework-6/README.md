# Homework 6: Task Management System & AI Memory System

This repository contains the code for Homework 6 of the DATA-236 Distributed Systems course. It consists of two main parts:

## Part 1: Task Management System (10 Points)

A REST API for managing tasks with categories and priority levels.

- **Backend** (`/long-term-memory/app/routes/tasks.py`): Built with FastAPI and PyMongo. Implements full CRUD for tasks with Pydantic validation (required fields, enums, max-length constraints, timestamps).
- **Database** (`/long-term-memory/app/database.py`): MongoDB connection via PyMongo. Uses the `tasks` collection.
- **Models** (`/long-term-memory/app/models.py`): Pydantic schemas — `TaskCreate`, `TaskUpdate`, `TaskOut`.

### Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tasks` | Create a new task (201) |
| GET | `/api/tasks` | Get all tasks |
| GET | `/api/tasks/:id` | Get a single task by ID |
| PUT | `/api/tasks/:id` | Update a task (partial) |
| DELETE | `/api/tasks/:id` | Delete a task (204) |

## Part 2: AI Memory System (10 Points)

A multi-session AI study tutor with short-term, long-term, and episodic memory backed by MongoDB and a local Ollama LLM.

- **Chat Endpoint** (`/api/chat`): Saves messages, builds prompts using all three memory types, and generates responses via Ollama (`llama3.2:3b-instruct-q4_K_S`).
- **Memory Endpoint** (`/api/memory/{user_id}`): Returns a snapshot of stored messages, session summaries, and episodic facts.
- **Aggregate Endpoint** (`/api/aggregate/{user_id}`): MongoDB aggregation pipeline computing daily message counts and recent summaries.

### MongoDB Collections
| Collection | Purpose |
|------------|---------|
| `tasks` | Part 1 task documents |
| `messages` | Chat history (user & assistant turns) |
| `summaries` | Session-level and lifetime user summaries |
| `episodes` | Extracted facts with embeddings for cosine similarity search |

### Memory Architecture
- **Short-term**: Sliding window of last N messages from the current session
- **Long-term**: Session summaries (every 5 messages) + lifetime user profile (updated on each new fact)
- **Episodic**: Facts extracted per message, embedded via Ollama, retrieved by cosine similarity

## Files

```
long-term-memory/
├── app/
│   ├── config.py          # Environment config (Mongo URI, Ollama URL/model)
│   ├── database.py        # PyMongo client + collection handles
│   ├── models.py          # Pydantic schemas (Task + Memory)
│   ├── main.py            # FastAPI app setup with CORS
│   ├── llm.py             # Ollama helpers: call_ollama, embed_text, cosine_similarity
│   └── routes/
│       ├── tasks.py       # Task CRUD API
│       └── memory.py      # AI Memory endpoints
├── docker-compose.yml     # MongoDB container
├── requirements.txt       # Python dependencies
└── index.html             # Frontend UI
```

## Setup

```bash
# 1. Start MongoDB
docker-compose up -d

# 2. Install dependencies
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 4. Open API docs
open http://localhost:8000/docs
```

> **Note**: Requires [Ollama](https://ollama.ai) running locally with `llama3.2:3b-instruct-q4_K_S` pulled.
