from pydantic import BaseModel
from typing import Optional


class BasePost(BaseModel):
    text: str


class CreatePost(BasePost):
    ...


class UpdatePost(BasePost):
    ...

    class Config:
        orm_mode = True


class Posts(BasePost):
    id: int
    user: Optional[str]  # TODO сделать обязательным

    class Config:
        orm_mode = True
