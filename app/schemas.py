from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

# User Schemas
class UserAuth(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v or "@" not in v or not v.strip():
            raise ValueError("Invalid email address format.")
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v or len(v) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        return v

class UserResponse(BaseModel):
    id: int
    email: str

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

# Task Schemas
class TaskCreate(BaseModel):
    title: str = Field(..., description="Task title")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title must not be empty or whitespace-only.")
        return v.strip()

class TaskUpdate(BaseModel):
    title: str = Field(..., description="Task title")
    done: bool = Field(..., description="Task completion status")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title must not be empty or whitespace-only.")
        return v.strip()

class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool
    user_id: int
