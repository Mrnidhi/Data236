from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="Book Management API", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")


class Book(BaseModel):
    id: int
    title: str
    author: str


class BookCreate(BaseModel):
    title: str
    author: str


books: List[Book] = []


@app.get("/")
async def read_root():
    return FileResponse("static/index.html")


@app.get("/api/books", response_model=List[Book])
async def get_books(q: Optional[str] = None):
    """Get all books, optionally filtered by title search."""
    if q:
        return [b for b in books if q.lower() in b.title.lower()]
    return books


@app.post("/api/books", response_model=Book, status_code=201)
async def create_book(book_data: BookCreate):
    """Add a new book with auto-incremented ID."""
    if not book_data.title.strip() or not book_data.author.strip():
        raise HTTPException(status_code=400, detail="Title and author are required")

    new_id = max([b.id for b in books], default=0) + 1
    new_book = Book(id=new_id, title=book_data.title, author=book_data.author)
    books.append(new_book)
    return new_book


@app.put("/api/books/1", response_model=Book)
async def update_book_one():
    """Update Book ID 1 to 'Harry Potter' by 'J.K Rowling'."""
    book = next((b for b in books if b.id == 1), None)
    if not book:
        raise HTTPException(status_code=404, detail="Book with ID 1 not found")

    book.title = "Harry Potter"
    book.author = "J.K Rowling"
    return book


@app.delete("/api/books/max", status_code=204)
async def delete_max_book():
    """Delete the book with the highest ID."""
    global books
    if not books:
        raise HTTPException(status_code=404, detail="No books to delete")

    max_id = max(b.id for b in books)
    books = [b for b in books if b.id != max_id]
    return None


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
