from pydantic import (
    BaseModel,
    EmailStr,
    Field
)
from datetime import datetime

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=1,
        max_length=500
    )

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class MessageResponse(BaseModel):
    message: str