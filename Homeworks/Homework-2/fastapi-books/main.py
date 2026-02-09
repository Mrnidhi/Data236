from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

BOOKS = []

@app.get("/")
def home(request: Request, q: Optional[str] = None):
    """
    Renders the home page with a list of books.
    If 'q' is provided, filters books by title (case-insensitive).
    """
    if q:
        filtered_books = [b for b in BOOKS if q.lower() in b["title"].lower()]
    else:
        filtered_books = BOOKS
        

    has_id_one = any(b["id"] == 1 for b in BOOKS)
    
    return templates.TemplateResponse("home.html", {
        "request": request, 
        "books": filtered_books, 
        "query": q,
        "has_id_one": has_id_one
    })

@app.get("/add")
def add_form(request: Request):
    """Renders the form to add a new book."""
    return templates.TemplateResponse("add.html", {"request": request})

@app.post("/add")
def add_book(title: str = Form(...), author: str = Form(...)):
    """
    Adds a new book with the next available ID.
    Redirects to home.
    """
    new_id = 1
    if BOOKS:
        new_id = max(b["id"] for b in BOOKS) + 1
        
    BOOKS.append({"id": new_id, "title": title, "author": author})
    return RedirectResponse(url="/", status_code=303)

@app.get("/update/1")
def update_form(request: Request):
    """
    Renders the update form for Book ID 1.
    If Book 1 doesn't exist, redirects home to avoid confusion.
    """
    book = next((b for b in BOOKS if b["id"] == 1), None)
    if not book:
        return RedirectResponse(url="/", status_code=303)
        
    return templates.TemplateResponse("update.html", {"request": request, "book": book})

@app.post("/update/1")
def update_book_one():
    """
    Updates Book ID 1 to 'Harry Potter' by 'J.K Rowling'.
    Redirects home.
    """
    for book in BOOKS:
        if book["id"] == 1:
            book["title"] = "Harry Potter"
            book["author"] = "J.K Rowling"
            break
            
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete/max")
def delete_max_book():
    """
    Deletes the book with the highest ID.
    Redirects home.
    Handles empty list gracefully.
    """
    if BOOKS:
        max_id = max(b["id"] for b in BOOKS)
        for i, book in enumerate(BOOKS):
            if book["id"] == max_id:
                del BOOKS[i]
                break
                
    return RedirectResponse(url="/", status_code=303)
