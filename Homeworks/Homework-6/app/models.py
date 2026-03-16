from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime

# ---- Part 1: Task Management ----

class TaskBase(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = None
    status: Literal['pending', 'in-progress', 'completed'] = 'pending'
    priority: Literal['low', 'medium', 'high'] = 'medium'
    dueDate: datetime
    category: Literal['Work', 'Personal', 'Shopping', 'Health', 'Other']

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    status: Optional[Literal['pending', 'in-progress', 'completed']] = None
    priority: Optional[Literal['low', 'medium', 'high']] = None
    dueDate: Optional[datetime] = None
    category: Optional[Literal['Work', 'Personal', 'Shopping', 'Health', 'Other']] = None

class TaskOut(TaskBase):
    id: str
    created_at: datetime
    updated_at: datetime

# ---- Part 2: AI Memory ----

class ChatRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    message: str

class ProfileUpdateReq(BaseModel):
    student_id: str
    field: str
    value: str

class ExtractedMemory(BaseModel):
    topics_studied: List[str] = []
    difficult_areas: List[str] = []
    learning_goals: List[str] = []
