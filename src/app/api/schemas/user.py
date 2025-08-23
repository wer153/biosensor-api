from pydantic import BaseModel, EmailStr


class User(BaseModel):
    name: str
    email: str


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    password: str | None = None
