"""Seed test users with hashed passwords directly into MySQL."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.security import get_password_hash
from app.db.database import Base, SessionLocal, engine
from app.models.user import User

Base.metadata.create_all(bind=engine)

db = SessionLocal()

users_to_create = [
    {"username": "alice", "password": "alice123", "role": "reader"},
    {"username": "bob", "password": "bob123", "role": "writer"},
    {"username": "carol", "password": "carol123", "role": "moderator"},
]

for u in users_to_create:
    existing = db.query(User).filter(User.username == u["username"]).first()
    if not existing:
        db_user = User(
            username=u["username"],
            hashed_password=get_password_hash(u["password"]),
            role=u["role"],
        )
        db.add(db_user)
        print(f"Created user: {u['username']} ({u['role']})")
    else:
        print(f"User already exists: {u['username']}")

db.commit()
db.close()
print("Done seeding users.")
