from fastapi import FastAPI

from app.db.database import Base, engine
from app.routers import auth, posts, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Blog Management System - JWT Authentication & Authorization",
    version="1.0.0",
    description="FastAPI Demo for Auth, Authorization, Linting, and CI Pipeline.",
)


@app.get("/")
def root():
    return {
        "message": "FastAPI JWT Auth Demo is running",
        "docs": "/docs",
    }


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
