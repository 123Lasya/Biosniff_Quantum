from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserRole


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    role: UserRole = UserRole.FARMER
    
    # Farmer specific details
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    profile_image_url: Optional[str] = None

    # Farm specific onboarding details
    farm_name: Optional[str] = None
    crop: Optional[str] = None
    crop_variety: Optional[str] = None
    area: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    boundary_geojson: Optional[str] = None


class UserLogin(BaseModel):
    # Allows logging in with either username or email
    username_or_email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    farmer_id: Optional[int] = None
    username: str
    email: str
    full_name: Optional[str] = None
    profile_image_url: Optional[str] = None


class UserOut(BaseModel):
    user_id: int
    username: str
    email: str
    role: str
    is_active: bool
    farmer_id: Optional[int] = None
    full_name: Optional[str] = None
    profile_image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None
