from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    FARMER = "farmer"
    ADMIN = "admin"

class User(Base):
    '''User model - handles authentication for both farmers and admins'''
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.FARMER, nullable=False)
    
    # Profile information
    district = Column(String(50))
    sector = Column(String(50))
    village = Column(String(50))
    farm_size = Column(Float)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Password reset
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    
    # Preferences
    receive_notifications = Column(Boolean, default=True)
    preferred_contact = Column(String(10), default='sms')  # 'sms' or 'email'
    
    # Relationships
    soil_readings = relationship('SoilReading', back_populates='user', cascade='all, delete-orphan')
    recommendations = relationship('Recommendation', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email or self.phone_number} - {self.role}>'

class SoilReading(Base):
    '''Soil Reading model'''
    __tablename__ = 'soil_readings'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Soil parameters
    ph = Column(Float, nullable=False)
    nitrogen = Column(Float, nullable=False)
    phosphorus = Column(Float, nullable=False)
    potassium = Column(Float, nullable=False)
    zinc = Column(Float)
    sulfur = Column(Float)
    
    # Location
    location_lat = Column(Float)
    location_lon = Column(Float)
    
    # Metadata
    reading_date = Column(DateTime, default=datetime.utcnow, index=True)
    reading_source = Column(String(20), default='manual')
    notes = Column(Text)
    
    # Relationship
    user = relationship('User', back_populates='soil_readings')

class Recommendation(Base):
    '''Crop Recommendation model'''
    __tablename__ = 'recommendations'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    soil_reading_id = Column(Integer, ForeignKey('soil_readings.id'))
    
    # Recommendation details
    recommended_crop = Column(String(50), nullable=False)
    confidence_score = Column(Float)
    alternative_crops = Column(JSON)
    
    # Soil health
    soil_health_status = Column(String(20))
    soil_issues = Column(JSON)
    
    # Advice
    fertilizer_recommendation = Column(Text)
    planting_season = Column(String(100))
    weather_advice = Column(Text)
    
    # Delivery
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    
    # Relationship
    user = relationship('User', back_populates='recommendations')

class WeatherData(Base):
    '''Weather data cache'''
    __tablename__ = 'weather_data'
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(100), nullable=False, index=True)
    
    # Weather info
    temperature = Column(Float)
    humidity = Column(Float)
    rainfall = Column(Float)
    wind_speed = Column(Float)
    description = Column(String(100))
    weather_data = Column(JSON)
    
    # Timestamp
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Weather {self.location} - {self.recorded_at}>'

class NotificationLog(Base):
    '''Track sent notifications'''
    __tablename__ = 'notification_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    notification_type = Column(String(50))  # 'daily', 'recommendation', 'alert'
    channel = Column(String(20))  # 'sms', 'email'
    message = Column(Text)
    
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)