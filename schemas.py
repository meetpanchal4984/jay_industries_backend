from pydantic import BaseModel, EmailStr, field_validator
from typing import List
import re

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    mobile: str
    password: str
    confirm_password: str

    @field_validator('mobile')
    def validate_mobile(cls, v):
        if not re.match(r'^\d{10}$', v):
            raise ValueError('Mobile number must be exactly 10 digits')
        return v

    @field_validator('confirm_password')
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    mobile: str
    is_registered: bool
    is_logged_in: bool
    is_admin: bool

    class Config:
        from_attributes = True

class ProductImageResponse(BaseModel):
    id: int
    image_url: str

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str
    description: str
    image_url: str

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    image_url: str
    is_published: bool
    sub_images: List[ProductImageResponse] = []

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_users: int
    logged_in_users: int
    active_users: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class ContactCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    subject: str
    message: str
