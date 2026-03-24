from pydantic import BaseModel, ConfigDict


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    author_id: int

    model_config = ConfigDict(from_attributes=True)
