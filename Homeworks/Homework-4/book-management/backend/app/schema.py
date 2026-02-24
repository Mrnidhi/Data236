from pydantic import BaseModel, Field, EmailStr


# --- Book schemas ---

class BookCreate(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)

class BookUpdate(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)

class BookOut(BaseModel):
    id: int
    title: str
    author: str

    class Config:
        from_attributes = True


# --- User / Auth schemas ---

class UserCreate(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=4)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True