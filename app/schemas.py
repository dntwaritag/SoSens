from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class UserRole(str, Enum):
    FARMER = "farmer"
    ADMIN = "admin"

class ContactMethod(str, Enum):
    EMAIL = "email"
    SMS = "sms"

# Auth schemas
class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, pattern=r'^\+?250\d{9}$')
    district: str = Field(..., min_length=2)
    sector: Optional[str] = None
    village: Optional[str] = None
    farm_size: Optional[float] = Field(None, gt=0)
    role: UserRole = UserRole.FARMER
    preferred_contact: ContactMethod = ContactMethod.SMS
    receive_notifications: bool = True

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: Optional[str]
    phone_number: Optional[str]
    full_name: str
    role: UserRole
    district: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class PasswordReset(BaseModel):
    username: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

# Soil & Prediction schemas
class SoilReadingCreate(BaseModel):
    ph: float = Field(..., ge=3.0, le=10.0)
    nitrogen: float = Field(..., ge=0, le=200)
    phosphorus: float = Field(..., ge=0, le=150)
    potassium: float = Field(..., ge=0, le=600)
    zinc: Optional[float] = None
    sulfur: Optional[float] = None
    notes: Optional[str] = None

class PredictionRequest(BaseModel):
    ph: float = Field(..., ge=3.0, le=10.0)
    nitrogen: float = Field(..., ge=0, le=200)
    phosphorus: float = Field(..., ge=0, le=150)
    potassium: float = Field(..., ge=0, le=600)
    zinc: Optional[float] = None
    sulfur: Optional[float] = None
    include_weather: bool = True

class PredictionResponse(BaseModel):
    success: bool
    crop: str
    confidence: float
    soil_health: str
    fertilizer_advice: str
    planting_season: str
    weather_advice: Optional[str] = None
    alternatives: List[dict]

# Weather schema
class WeatherResponse(BaseModel):
    location: str
    temperature: float
    humidity: float
    description: str
    rainfall_forecast: Optional[float]
    advice: str