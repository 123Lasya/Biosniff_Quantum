from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class FarmerBase(BaseModel):
    full_name: str
    phone: str
    email: EmailStr
    address: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    profile_image: Optional[str] = None


class FarmerCreate(FarmerBase):
    user_id: int


class FarmerUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    profile_image: Optional[str] = None


class FarmerOut(FarmerBase):
    farmer_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
