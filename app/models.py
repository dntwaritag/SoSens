"""
SQLAlchemy models for SoSens database
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
import enum

# ============================================================================
# ENUMS
# ============================================================================

class UserRole(str, enum.Enum):
    """User role enumeration"""
    FARMER = "farmer"
    ADMIN = "admin"

# ============================================================================
# USER MODEL
# ============================================================================

class User(Base):
    """User model for farmers and admins"""
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Contact information
    email = Column(String, unique=True, index=True, nullable=True)
    phone_number = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, index=True, nullable=False)
    
    # Authentication
    hashed_password = Column(String, nullable=False)
    
    # Profile information
    role = Column(Enum(UserRole), default=UserRole.FARMER, nullable=False)
    district = Column(String, index=True, nullable=False)
    sector = Column(String, nullable=True)
    village = Column(String, nullable=True)
    farm_size = Column(Float, nullable=True)  # In hectares
    
    # Notification preferences
    preferred_contact = Column(String, default="sms")  # "sms" or "email"
    receive_notifications = Column(Boolean, default=True)
    
    # Account status
    is_active = Column(Boolean, default=True, index=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Password reset tokens
    reset_token = Column(String, nullable=True, unique=True)
    reset_token_expires = Column(DateTime, nullable=True)
    
    # Relationships
    soil_readings = relationship("SoilReading", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("NotificationLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"

# ============================================================================
# SOIL READING MODEL
# ============================================================================

class SoilReading(Base):
    """Soil reading data from farmers"""
    __tablename__ = "soil_readings"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Soil parameters
    ph = Column(Float, nullable=False)
    nitrogen = Column(Float, nullable=False)
    phosphorus = Column(Float, nullable=False)
    potassium = Column(Float, nullable=False)
    zinc = Column(Float, nullable=True, default=5.0)
    sulfur = Column(Float, nullable=True, default=15.0)
    
    # Metadata
    reading_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="soil_readings")
    recommendations = relationship("Recommendation", back_populates="soil_reading", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SoilReading id={self.id} user_id={self.user_id} ph={self.ph}>"

# ============================================================================
# RECOMMENDATION MODEL
# ============================================================================

class Recommendation(Base):
    """Crop recommendations based on soil analysis"""
    __tablename__ = "recommendations"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    soil_reading_id = Column(Integer, ForeignKey("soil_readings.id"), nullable=True)
    
    # Prediction results
    recommended_crop = Column(String, nullable=False, index=True)
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0
    alternative_crops = Column(JSON, nullable=True)  # List of alternatives
    
    # Soil health assessment
    soil_health_status = Column(String, nullable=False)  # "Good", "Fair", "Poor"
    soil_issues = Column(JSON, nullable=True)  # List of issues
    
    # Recommendations
    fertilizer_recommendation = Column(Text, nullable=False)
    planting_season = Column(String, nullable=False)
    weather_advice = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="recommendations")
    soil_reading = relationship("SoilReading", back_populates="recommendations")
    
    def __repr__(self):
        return f"<Recommendation id={self.id} crop={self.recommended_crop} confidence={self.confidence_score}>"

# ============================================================================
# NOTIFICATION LOG MODEL
# ============================================================================

class NotificationLog(Base):
    """Log of all notifications sent to users"""
    __tablename__ = "notifications"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Notification details
    notification_type = Column(String, nullable=False, index=True)  # "sms", "email", "welcome", "prediction", etc.
    channel = Column(String, nullable=False)  # "sms" or "email"
    message = Column(Text, nullable=False)
    
    # Status
    is_sent = Column(Boolean, default=False, nullable=False, index=True)
    sent_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<NotificationLog id={self.id} type={self.notification_type} sent={self.is_sent}>"

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'User',
    'SoilReading', 
    'Recommendation',
    'NotificationLog',
    'UserRole'
]