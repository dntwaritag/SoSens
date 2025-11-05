from pydantic import BaseModel, Field, EmailStr, model_validator, ValidationError, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ============================================================================
# ENUMS
# ============================================================================

class UserRole(str, Enum):
    FARMER = "farmer"
    ADMIN = "admin"

class ContactMethod(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    BOTH = "both"

# ============================================================================
# AUTH SCHEMAS
# ============================================================================

# ...existing code...

class UserRegister(BaseModel):
    # Required
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name of the user")
    password: str = Field(..., min_length=8, max_length=100, description="Password must be at least 8 characters")
    
    # Contact (at least one required)
    email: Optional[EmailStr] = Field(None, description="Valid email address")
    phone_number: Optional[str] = Field(
        None, 
        pattern=r'^\+250[7][2389]\d{7}$',
        description="Rwanda phone number in format: +250xxxxxxxxx"
    )
    
    # Profile
    district: str = Field(..., min_length=2, description="District name in Rwanda")
    sector: Optional[str] = Field(None, min_length=2, description="Sector name")
    village: Optional[str] = Field(None, min_length=2, description="Village name")
    farm_size: Optional[float] = Field(None, gt=0, description="Farm size in hectares")
    
    # Role and Preferences
    role: UserRole = Field(default=UserRole.FARMER, description="User role (farmer or admin)")
    preferred_contact: ContactMethod = Field(
        default=ContactMethod.PHONE,
        description="Preferred contact method"
    )
    receive_notifications: bool = Field(default=True, description="Receive notifications flag")

    @model_validator(mode='after')
    def validate_contact_info(self) -> 'UserRegister':
        email, phone = self.email, self.phone_number
        if not email and not phone:
            raise ValueError('Either email or phone number must be provided')
        if self.preferred_contact == ContactMethod.EMAIL and not email:
            raise ValueError('Email is required when email is the preferred contact method')
        if self.preferred_contact == ContactMethod.PHONE and not phone:
            raise ValueError('Phone number is required when phone is the preferred contact method')
        return self

class UserLogin(BaseModel):
    username: str  # Can be email or phone
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: 'UserResponse'

class PasswordReset(BaseModel):
    username: str  # Email or phone

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    email: Optional[str]
    phone_number: Optional[str]
    full_name: str
    role: UserRole
    district: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe",
                "password": "strongpass123",
                "email": "john.doe@example.com",
                "phone_number": "+250722123456",
                "district": "Kicukiro",
                "sector": "Gahanga",
                "village": "Murindi",
                "farm_size": 2.5,
                "role": "farmer",
                "preferred_contact": "phone",
                "receive_notifications": True
            }
        }

# ============================================================================
# SOIL & PREDICTION SCHEMAS
# ============================================================================

class SoilReadingCreate(BaseModel):
    ph: float = Field(..., ge=3.0, le=10.0)
    nitrogen: float = Field(..., ge=0, le=200)
    phosphorus: float = Field(..., ge=0, le=150)
    potassium: float = Field(..., ge=0, le=600)
    zinc: Optional[float] = Field(None, ge=0)
    sulfur: Optional[float] = Field(None, ge=0)
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None
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

# ============================================================================
# WEATHER SCHEMAS
# ============================================================================

class WeatherResponse(BaseModel):
    location: str
    temperature: float
    humidity: float
    description: str
    rainfall_forecast: Optional[float] = None
    advice: str

# ============================================================================
# NOTIFICATION SCHEMAS
# ============================================================================

class NotificationPreferences(BaseModel):
    receive_notifications: bool
    preferred_contact: ContactMethod