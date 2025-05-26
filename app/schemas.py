from sqlmodel import SQLModel
from pydantic import EmailStr
from datetime import datetime
from typing import Optional, Literal


class UserCreate(SQLModel):
    email: EmailStr
    password: str

class UserRead(SQLModel):
    id: int
    email: str
    created_at: datetime
    updated_at: datetime


class PostBase(SQLModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class PostRead(PostBase):
    id: int
    owner_id: int
    owner: Optional["UserRead"] = None

class PostReadWithVotes(PostRead):
    votes: int

class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    id: Optional[int] = None

class Vote(SQLModel):
    post_id: int
    dir : Literal[0, 1]