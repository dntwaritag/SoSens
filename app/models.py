from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Farmer(Base):
    '''Farmer model - stores farmer information'''
    __tablename__ = 'farmers'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    district = Column(String(50), nullable=False)
    sector = Column(String(50))
    cell = Column(String(50))
    village = Column(String(50))
    farm_size = Column(Float)
    registered_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    soil_readings = relationship('SoilReading', back_populates='farmer', cascade='all, delete-orphan')
    recommendations = relationship('Recommendation', back_populates='farmer', cascade='all, delete-orphan')
    feedback = relationship('Feedback', back_populates='farmer', cascade='all, delete-orphan')

class SoilReading(Base):
    '''Soil Reading model'''
    __tablename__ = 'soil_readings'
    
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey('farmers.id'), nullable=False, index=True)
    
    ph = Column(Float, nullable=False)
    nitrogen = Column(Float, nullable=False)
    phosphorus = Column(Float, nullable=False)
    potassium = Column(Float, nullable=False)
    zinc = Column(Float)
    sulfur = Column(Float)
    
    environmental_data = Column(JSON)
    reading_date = Column(DateTime, default=datetime.utcnow, index=True)
    reading_source = Column(String(20))
    location_lat = Column(Float)
    location_lon = Column(Float)
    notes = Column(Text)
    
    # Relationship
    farmer = relationship('Farmer', back_populates='soil_readings')

class Recommendation(Base):
    '''Recommendation model'''
    __tablename__ = 'recommendations'
    
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey('farmers.id'), nullable=False, index=True)
    soil_reading_id = Column(Integer, ForeignKey('soil_readings.id'), index=True)
    
    recommended_crop = Column(String(50), nullable=False)
    confidence_score = Column(Float)
    alternative_crops = Column(JSON)
    
    soil_health_status = Column(String(20))
    soil_issues = Column(JSON)
    
    fertilizer_recommendation = Column(Text)
    planting_season = Column(String(100))
    spacing_recommendation = Column(String(100))
    additional_tips = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    delivered_via = Column(String(20))
    is_delivered = Column(Boolean, default=False)
    
    # Relationship
    farmer = relationship('Farmer', back_populates='recommendations')

class Feedback(Base):
    '''Feedback model'''
    __tablename__ = 'feedback'
    
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey('farmers.id'), nullable=False, index=True)
    recommendation_id = Column(Integer, ForeignKey('recommendations.id'), index=True)
    
    action_taken = Column(Boolean)
    crop_planted = Column(String(50))
    yield_achieved = Column(Float)
    satisfaction_rating = Column(Integer)
    comments = Column(Text)
    
    submitted_at = Column(DateTime, default=datetime.utcnow)
    harvest_date = Column(DateTime)
    
    # Relationship
    farmer = relationship('Farmer', back_populates='feedback')

class SystemLog(Base):
    '''System Log model'''
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    log_type = Column(String(20))
    endpoint = Column(String(100))
    method = Column(String(10))
    status_code = Column(Integer)
    message = Column(Text)
    user_id = Column(Integer)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)