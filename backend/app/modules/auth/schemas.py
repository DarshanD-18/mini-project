from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of student")
    email: EmailStr = Field(..., description="Valid student email address")
    password: str = Field(..., min_length=6, max_length=128, description="Secure account password")


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered student email")
    password: str = Field(..., description="Account password")


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    message: str
