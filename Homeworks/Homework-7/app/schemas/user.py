from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str
    role: str = "reader"


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserBase):
    id: int
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)
