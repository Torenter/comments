from pydantic import BaseModel, Field, validator
from passlib.context import CryptContext
from typing import Optional


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthUser(BaseModel):
    login: str
    password: str

class CreateUser(BaseModel):
    name: str
    login: str
    password_hash: str = Field(..., alias="password")

    @validator("password_hash")
    def get_password_hash(password_hash):
        return pwd_context.hash(password_hash)

class User(BaseModel):
    id: int
    name: str
    login: str
    password_hash: str
    disabled: Optional[bool]

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str


if __name__=="__main__":
    data = {
        "name":"test",
        "login":"test",
        "password":"123aaa"
    }
    a = CreateUser(**data)
    print()