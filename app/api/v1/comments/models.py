from pydantic import BaseModel
from typing import Optional


class BaseComment(BaseModel):
    text: str


class AddComment(BaseComment):
    post_id: int


class UpdateComment(BaseComment):
    ...

    class Config:
        orm_mode = True


class Comment(BaseComment):
    id: int

    class Config:
        orm_mode = True
