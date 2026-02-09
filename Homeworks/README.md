# HW1 Part 2 - Agentic AI Demo

## What This Project Does

This project demonstrates how to build a simple multi-agent AI system using a local LLM. The idea is to have two "agents" that work together to analyze blog content and produce useful metadata.

**Input:** A blog title and content  
**Output:** 3 relevant tags + a short summary (as JSON)

## How It Works

I built this using a **Planner → Reviewer → Finalizer** flow:

### 1. Planner Agent
The Planner reads the blog content and comes up with:
- 3 topic tags (like "distributed systems", "vector clocks")
- A one-sentence summary

Think of it as the first draft.

### 2. Reviewer Agent
The Reviewer looks at what the Planner produced and checks:
- Are the tags actually relevant?
- Is the summary accurate and complete?

If something's off, the Reviewer can fix it. Otherwise, it just approves.

### 3. Finalizer
This is the cleanup step. It makes sure:
- Exactly 3 tags in the output
- Summary is 25 words or less
- Output is valid JSON

## Tech Stack

- **Python 3.11+**
- **Ollama** - runs the LLM locally on my machine
- **smollm:1.7b** - a small but capable local language model
- **langchain-ollama** - makes it easy to call Ollama from Python

## Setup Steps

### 1. Install Ollama
Download from [ollama.ai](https://ollama.ai) and install.

### 2. Pull the model
```bash
ollama pull smollm:1.7b
```

### 3. Create virtual environment
```bash
cd HW-1/Part-B
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install langchain-ollama
```

### 5. Run the script
```bash
python3 agents_demo.py
```

## Sample Output

```json
{
  "title": "Understanding Vector Clocks in Distributed Systems",
  "tags": ["vector clocks", "distributed systems", "event ordering"],
  "summary": "Vector clocks track causality and partial ordering of events across distributed system nodes."
}
```

## Why This Approach?

The multi-agent pattern is useful because:
1. **Separation of concerns** - Each agent has one job
2. **Error correction** - Reviewer can catch Planner's mistakes
3. **Quality control** - Finalizer ensures the output format is correct

In real systems, this is how you'd build more complex AI pipelines where one model's output feeds into another.

## Files

- `agents_demo.py` - Main script with all three agents
- `venv/` - Python virtual environment (not committed to git)

## Author
Srinidhi Gowda  
DATA-236 Distributed Systems
