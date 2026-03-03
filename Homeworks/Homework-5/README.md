# Homework 5: Library Management System & MCP Server

This repository contains the code for Homework 5 of the DATA-236 Distributed Systems course. It consists of two main parts:

## Part 1: Library Management System
A web application to manage authors and their books.
*   **Backend (`/library-management/backend`)**: Built with FastAPI and MySQL. Provides RESTful API endpoints for creating, reading, updating, and deleting Authors and Books. It includes data validation (e.g., unique emails, valid ISBNs) and relational integrity.
*   **Frontend (`/library-management/frontend`)**: Built with React and Redux Toolkit. A user interface that connects to the backend API, allowing users to view the book catalog, add new books, update existing ones, and delete them.

## Part 2: MCP Server for TheMealDB
*   **Server (`/mcp-server/meals_server.py`)**: A Model Context Protocol (MCP) server built with FastMCP. It exposes 4 tools that interact with the public TheMealDB API, allowing AI assistants (like Claude) to directly search for meals, get recipe details, filter by ingredients, and fetch random meals.

## Files
*   **`library-management/`**: Contains the full source code for the FastAPI backend and React frontend.
*   **`mcp-server/`**: Contains the standalone Python MCP server script.
*   **`Jayaramegowda_HW5.pdf`**: The detailed homework report with testing screenshots and explanations.
