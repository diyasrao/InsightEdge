from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    firstname: str
    lastname: str 
    username: str
    email: EmailStr
    password: str

class SocialSignupResponse(BaseModel):
    id: str
    firstname: str
    lastname: str
    username: str
    email: str
    created_at: datetime

class UpdateUsername(BaseModel):
    new_username: str

class UpdateAbout(BaseModel):
    new_about: str

class UpdateName(BaseModel):
    first_name: str
    last_name: str

class UserOut(BaseModel):
    id: str   # changed it to str
    firstname: str
    lastname: str
    username: str
    email:  EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: str
    password: str


class UserAllOut(BaseModel):
    id: str # changed to str
    email: EmailStr

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None

class VerifyOTP(BaseModel):
    otp: str
    email: str

class EmailSchema(BaseModel):
    email: EmailStr = Field(...)

class ResetPasswordRequest(BaseModel):
    otp: str
    new_password: str
    email: str