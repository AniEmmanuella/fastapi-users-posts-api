from typing import List

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150, examples=["My first post"])
    content: str = Field(min_length=1, examples=["Hello world"])


class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    user_id: int


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, examples=["ada"])
    email: EmailStr = Field(examples=["ada@example.com"])


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr


class UserWithPosts(UserRead):
    posts: List[PostRead] = []


class ErrorResponse(BaseModel):
    detail: str
