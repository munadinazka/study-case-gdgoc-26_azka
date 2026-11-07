
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str
    email: EmailStr
    created_at: datetime


class TokenResponse(BaseModel):
    token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    token: str
    user: UserResponse
