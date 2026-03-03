# DATA-236 Homework 5

## Part 1: Library Management System (Full-Stack)

A full-stack Library Management app with a FastAPI backend and a React/Redux/Vite frontend.

**Folder:** `library-management/`

### Features
- Manage **Authors** (create, list, update, delete)
- Manage **Books** (create, list, update, delete, filter by author)
- React frontend with Redux Toolkit for state management
- MySQL database via SQLAlchemy

### Run Backend
```bash
cd library-management/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8006
# API available at http://localhost:8006
```

### Run Frontend
```bash
cd library-management/frontend
npm install
npm run dev
# UI available at http://localhost:3006
```

---

## Part 2: MCP Meals Server

An MCP (Model Context Protocol) server that wraps [TheMealDB](https://www.themealdb.com/) public API so AI assistants can search and look up meal recipes.

**Folder:** `mcp-server/`

### Tools Provided
- `search_meals_by_name` — Search meals by name
- `meals_by_ingredient` — Filter meals by a main ingredient
- `meal_details` — Get full recipe details (ingredients, instructions, YouTube link) by meal ID
- `random_meal` — Fetch a random meal

### Run
```bash
cd mcp-server
pip install fastmcp httpx
python meals_server.py
```

---
Srinidhi Gowda | DATA-236 Distributed Systems
