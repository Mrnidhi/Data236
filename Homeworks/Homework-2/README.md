# Homework 2 — DATA-236

## Part 1 & 2: Artist Liberty + FastAPI Book Management

**Folder:** `book-management/`

A FastAPI-based Book Management System with Artist Liberty styling.

### Features
1. **Add Book** — Enter title and author, auto-assigns ID
2. **Update Book ID 1** — Updates to "Harry Potter" by "J.K Rowling"
3. **Delete Highest ID** — Removes the book with the max ID
4. **Search** — Filter books by title

### Run
```bash
cd book-management
pip install -r requirements.txt
python main.py
# Open http://localhost:8080
```

---

## Part 3: Stateful Agent Graph (LangGraph)

**Folder:** `agent_graph/`

A LangGraph implementation using the **Supervisor pattern** with Planner/Reviewer agents.

### Architecture
```
Supervisor → Planner → Supervisor → Reviewer → Supervisor → END
                                      ↓ (has issues)
                              ← Planner (correction loop)
```

- **AgentState**: Shared memory (title, content, email, strict, task, llm, planner_proposal, reviewer_feedback, turn_count)
- **Planner Node**: Creates proposals, revises based on feedback
- **Reviewer Node**: Evaluates proposals, reports issues
- **Supervisor**: Routes between agents, prevents infinite loops with turn counter

### Run Tests
```bash
pip install langgraph langchain
python test_graph.py
```
