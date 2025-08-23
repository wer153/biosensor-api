from pydantic import BaseModel


class User(BaseModel):
    name: str
    email: str


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
