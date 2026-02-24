from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import Response, Request
from .session_crud import create_session, get_session, delete_session

from .database import Base, engine, get_db
from . import crud, schema

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book Management API")

# Allow React dev server on port 5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Session middleware ──

def require_session(request: Request, db: Session = Depends(get_db)):
    """Check for a valid session cookie before allowing access."""
    token = request.cookies.get("session_id")
    if not token:
        raise HTTPException(status_code=401, detail="Not logged in")
    s = get_session(db, token)
    if not s:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    return s


# ── Health check ──

@app.get("/health")
def health():
    return {"status": "ok"}


# ── Book endpoints (CRUD) ──

@app.post("/books", response_model=schema.BookOut)
def add_book(
    payload: schema.BookCreate,
    db: Session = Depends(get_db),
    _session=Depends(require_session),
):
    return crud.create_book(db, payload)


@app.get("/books", response_model=list[schema.BookOut])
def list_books(
    db: Session = Depends(get_db),
    _session=Depends(require_session),
):
    return crud.get_books(db)


@app.get("/books/{book_id}", response_model=schema.BookOut)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    _session=Depends(require_session),
):
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.put("/books/{book_id}", response_model=schema.BookOut)
def edit_book(
    book_id: int,
    payload: schema.BookUpdate,
    db: Session = Depends(get_db),
    _session=Depends(require_session),
):
    book = crud.update_book(db, book_id, payload)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.delete("/books/{book_id}", response_model=schema.BookOut)
def remove_book(
    book_id: int,
    db: Session = Depends(get_db),
    _session=Depends(require_session),
):
    book = crud.delete_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


# ── Auth endpoints ──

@app.post("/auth/register", response_model=schema.UserOut)
def register(payload: schema.UserCreate, db: Session = Depends(get_db)):
    """Register a new user with name, email, and password."""
    try:
        return crud.create_user(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")


@app.post("/auth/login")
def login(payload: schema.LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Authenticate with email + password; sets an HTTP-only session cookie."""
    user = crud.get_user_by_email(db, payload.email)
    if not user or not crud.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    s = create_session(db, user_id=user.id)

    response.set_cookie(
        key="session_id",
        value=s.id,
        httponly=True,
        samesite="lax",
        max_age=30 * 60,
    )
    return {"message": "logged in", "user_id": user.id}


@app.get("/auth/me")
def me(_session=Depends(require_session)):
    return {"logged_in": True, "user_id": _session.user_id}


@app.post("/auth/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("session_id")
    if token:
        delete_session(db, token)
    response.delete_cookie("session_id")
    return {"message": "logged out"}