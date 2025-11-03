from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date

# ============================================================================
# FARMER SCHEMAS
# ============================================================================

class FarmerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone_number: str = Field(..., pattern=r'^\+?250\d{9}$')
    district: str = Field(..., min_length=2, max_length=50)
    sector: Optional[str] = Field(None, max_length=50)
    cell: Optional[str] = Field(None, max_length=50)
    village: Optional[str] = Field(None, max_length=50)
    farm_size: Optional[float] = Field(None, gt=0, description="Farm size in hectares")

class FarmerCreate(FarmerBase):
    pass

class FarmerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    district: Optional[str] = Field(None, min_length=2, max_length=50)
    sector: Optional[str] = None
    cell: Optional[str] = None
    village: Optional[str] = None
    farm_size: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None

class FarmerResponse(FarmerBase):
    id: int
    registered_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

# ============================================================================
# SOIL READING SCHEMAS
# ============================================================================

class SoilReadingBase(BaseModel):
    ph: float = Field(..., ge=3.0, le=10.0, description="Soil pH (3.0-10.0)")
    nitrogen: float = Field(..., ge=0, le=200, description="Nitrogen in kg/ha")
    phosphorus: float = Field(..., ge=0, le=150, description="Phosphorus in kg/ha")
    potassium: float = Field(..., ge=0, le=600, description="Potassium in kg/ha")
    zinc: Optional[float] = Field(None, ge=0, le=100)
    sulfur: Optional[float] = Field(None, ge=0, le=100)
    environmental_data: Optional[Dict[str, Any]] = None
    reading_source: Optional[str] = Field("manual", pattern=r'^(manual|sensor|lab)$')
    location_lat: Optional[float] = Field(None, ge=-90, le=90)
    location_lon: Optional[float] = Field(None, ge=-180, le=180)
    notes: Optional[str] = None

class SoilReadingCreate(SoilReadingBase):
    farmer_id: int

class SoilReadingResponse(SoilReadingBase):
    id: int
    farmer_id: int
    reading_date: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# PREDICTION SCHEMAS
# ============================================================================

class PredictionRequest(BaseModel):
    farmer_id: Optional[int] = None
    ph: float = Field(..., alias="Ph", ge=3.0, le=10.0)
    nitrogen: float = Field(..., alias="N", ge=0, le=200)
    phosphorus: float = Field(..., alias="P", ge=0, le=150)
    potassium: float = Field(..., alias="K", ge=0, le=600)
    zinc: Optional[float] = Field(None, alias="Zn", ge=0, le=100)
    sulfur: Optional[float] = Field(None, alias="S", ge=0, le=100)
    send_sms: Optional[bool] = False
    
    class Config:
        populate_by_name = True

class AlternativeCrop(BaseModel):
    crop: str
    confidence: float
    confidence_percent: str

class SoilHealthInfo(BaseModel):
    status: str
    ph: float
    nitrogen: float
    phosphorus: float
    potassium: float
    issues: List[str]

class CropRecommendations(BaseModel):
    fertilizer: str
    base_fertilizer: str
    planting_season: str
    spacing: str
    planting_depth: str
    maturity_days: str
    water_requirement: str
    tips: List[str]
    common_pests: List[str]

class PredictionResponse(BaseModel):
    success: bool
    prediction: Dict[str, Any]
    alternatives: List[AlternativeCrop]
    soil_health: SoilHealthInfo
    recommendations: CropRecommendations
    next_steps: List[str]
    recommendation_id: Optional[int] = None
    reading_id: Optional[int] = None

# ============================================================================
# RECOMMENDATION SCHEMAS
# ============================================================================

class RecommendationResponse(BaseModel):
    id: int
    farmer_id: int
    soil_reading_id: Optional[int]
    recommended_crop: str
    confidence_score: Optional[float]
    alternative_crops: Optional[List[Dict[str, Any]]]
    soil_health_status: Optional[str]
    soil_issues: Optional[List[str]]
    fertilizer_recommendation: Optional[str]
    planting_season: Optional[str]
    spacing_recommendation: Optional[str]
    additional_tips: Optional[str]
    created_at: datetime
    delivered_via: Optional[str]
    is_delivered: bool
    
    class Config:
        from_attributes = True

# ============================================================================
# FEEDBACK SCHEMAS
# ============================================================================

class FeedbackCreate(BaseModel):
    farmer_id: int
    recommendation_id: int
    action_taken: Optional[bool] = None
    crop_planted: Optional[str] = None
    yield_achieved: Optional[float] = Field(None, ge=0)
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)
    comments: Optional[str] = None
    harvest_date: Optional[date] = None

class FeedbackResponse(BaseModel):
    id: int
    farmer_id: int
    recommendation_id: int
    action_taken: Optional[bool]
    crop_planted: Optional[str]
    yield_achieved: Optional[float]
    satisfaction_rating: Optional[int]
    comments: Optional[str]
    submitted_at: datetime
    harvest_date: Optional[date]
    
    class Config:
        from_attributes = True

# ============================================================================
# ANALYTICS SCHEMAS
# ============================================================================

class DashboardSummary(BaseModel):
    total_farmers: int
    active_farmers: int
    total_soil_readings: int
    total_recommendations: int
    total_feedback: int
    average_satisfaction: float

class DistrictStats(BaseModel):
    district: str
    farmers: int

class CropStats(BaseModel):
    crop: str
    count: int

class SoilHealthStats(BaseModel):
    status: str
    count: int

class DashboardResponse(BaseModel):
    success: bool
    summary: DashboardSummary
    districts: List[DistrictStats]
    top_crops: List[CropStats]
    soil_health: List[SoilHealthStats]

# ============================================================================
# PAGINATION
# ============================================================================

class PaginatedResponse(BaseModel):
    success: bool
    items: List[Any]
    total: int
    page: int
    pages: int
    per_page: int