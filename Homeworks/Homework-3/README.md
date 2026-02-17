# DATA-236 Homework 3

## Part 1: FastAPI User Authentication System

A simple FastAPI application implementing session-based user authentication with Jinja2 templates and Bootstrap styling.

### Features
- Session-based authentication with hardcoded credentials
- Protected dashboard route
- Bootstrap-styled UI templates
- Login/logout functionality

### Running Part 1

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python3 main.py
# OR
uvicorn main:app --reload
```

Access the application at: `http://127.0.0.1:8000`

### Test Credentials
- Username: `admin`, Password: `password123`
- Username: `student`, Password: `sjsu2024`

### File Structure
```
├── main.py              # FastAPI application entry point
├── routers/
│   └── auth.py          # Authentication routes
├── templates/           # Jinja2 HTML templates
│   ├── home.html
│   ├── login.html
│   └── dashboard.html
└── requirements.txt
```

## Part 2: LlamaIndex Chunking Comparison

Compares three chunking techniques (Token-based, Semantic, and Sentence-Window) on the Tiny Shakespeare dataset using LlamaIndex with HuggingFace embeddings.

### Chunking Techniques Compared
1. **Token-based**: Fixed-size chunks using `TokenTextSplitter`
2. **Semantic**: Embedding-based boundary detection using `SemanticSplitterNodeParser`
3. **Sentence-window**: Single-sentence nodes with context using `SentenceWindowNodeParser`

### Running Part 2

```bash
# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run the comparison script
python3 chunking_comparison.py
```

The script will:
- Download the Tiny Shakespeare dataset
- Build indexes using all three techniques
- Perform retrieval for the primary query: "Who are the two feuding houses?"
- Run optional queries for additional comparison
- Generate a comparison report table

### Output
The comparison report includes:
- Top-1 cosine similarity scores
- Mean@k cosine similarity
- Total number of chunks produced
- Average chunk length
- Retrieval latency

## Requirements

See `requirements.txt` for all dependencies.

Main dependencies:
- fastapi
- uvicorn
- jinja2
- llama-index
- sentence-transformers
- pandas
