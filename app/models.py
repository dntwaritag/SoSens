from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()

class Farmer(db.Model):
    '''Farmer model - stores farmer information'''
    __tablename__ = 'farmers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    district = db.Column(db.String(50), nullable=False)
    sector = db.Column(db.String(50))
    cell = db.Column(db.String(50))
    village = db.Column(db.String(50))
    farm_size = db.Column(db.Float)  # in hectares
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    soil_readings = db.relationship('SoilReading', backref='farmer', lazy='dynamic', cascade='all, delete-orphan')
    recommendations = db.relationship('Recommendation', backref='farmer', lazy='dynamic', cascade='all, delete-orphan')
    feedback = db.relationship('Feedback', backref='farmer', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Farmer {self.name} - {self.phone_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone_number': self.phone_number,
            'district': self.district,
            'sector': self.sector,
            'cell': self.cell,
            'village': self.village,
            'farm_size': self.farm_size,
            'registered_at': self.registered_at.isoformat() if self.registered_at else None,
            'is_active': self.is_active
        }

class SoilReading(db.Model):
    '''Soil Reading model - stores soil sensor/manual readings'''
    __tablename__ = 'soil_readings'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False, index=True)
    
    # Soil Parameters
    ph = db.Column(db.Float, nullable=False)
    nitrogen = db.Column(db.Float, nullable=False)  # N
    phosphorus = db.Column(db.Float, nullable=False)  # P
    potassium = db.Column(db.Float, nullable=False)  # K
    zinc = db.Column(db.Float)  # Zn
    sulfur = db.Column(db.Float)  # S
    
    # Environmental Data (stored as JSON for flexibility)
    environmental_data = db.Column(JSON)  # Temperature, humidity, rainfall, etc.
    
    # Metadata
    reading_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    reading_source = db.Column(db.String(20))  # 'sensor', 'manual', 'lab'
    location_lat = db.Column(db.Float)
    location_lon = db.Column(db.Float)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<SoilReading {self.id} - Farmer {self.farmer_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'farmer_id': self.farmer_id,
            'ph': self.ph,
            'nitrogen': self.nitrogen,
            'phosphorus': self.phosphorus,
            'potassium': self.potassium,
            'zinc': self.zinc,
            'sulfur': self.sulfur,
            'environmental_data': self.environmental_data,
            'reading_date': self.reading_date.isoformat() if self.reading_date else None,
            'reading_source': self.reading_source,
            'location_lat': self.location_lat,
            'location_lon': self.location_lon,
            'notes': self.notes
        }

class Recommendation(db.Model):
    '''Recommendation model - stores crop recommendations'''
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False, index=True)
    soil_reading_id = db.Column(db.Integer, db.ForeignKey('soil_readings.id'), index=True)
    
    # Recommendation Details
    recommended_crop = db.Column(db.String(50), nullable=False)
    confidence_score = db.Column(db.Float)
    alternative_crops = db.Column(JSON)  # List of alternative crop options
    
    # Soil Health Assessment
    soil_health_status = db.Column(db.String(20))  # Good, Fair, Poor
    soil_issues = db.Column(JSON)  # List of identified issues
    
    # Actionable Advice
    fertilizer_recommendation = db.Column(db.Text)
    planting_season = db.Column(db.String(100))
    spacing_recommendation = db.Column(db.String(100))
    additional_tips = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    delivered_via = db.Column(db.String(20))  # 'sms', 'app', 'web'
    is_delivered = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Recommendation {self.id} - {self.recommended_crop}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'farmer_id': self.farmer_id,
            'soil_reading_id': self.soil_reading_id,
            'recommended_crop': self.recommended_crop,
            'confidence_score': self.confidence_score,
            'alternative_crops': self.alternative_crops,
            'soil_health_status': self.soil_health_status,
            'soil_issues': self.soil_issues,
            'fertilizer_recommendation': self.fertilizer_recommendation,
            'planting_season': self.planting_season,
            'spacing_recommendation': self.spacing_recommendation,
            'additional_tips': self.additional_tips,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'delivered_via': self.delivered_via,
            'is_delivered': self.is_delivered
        }

class Feedback(db.Model):
    '''Feedback model - stores farmer feedback on recommendations'''
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False, index=True)
    recommendation_id = db.Column(db.Integer, db.ForeignKey('recommendations.id'), index=True)
    
    # Feedback Details
    action_taken = db.Column(db.Boolean)  # Did farmer follow recommendation?
    crop_planted = db.Column(db.String(50))
    yield_achieved = db.Column(db.Float)  # in kg or tonnes
    satisfaction_rating = db.Column(db.Integer)  # 1-5 scale
    comments = db.Column(db.Text)
    
    # Metadata
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    harvest_date = db.Column(db.Date)
    
    def __repr__(self):
        return f'<Feedback {self.id} - Recommendation {self.recommendation_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'farmer_id': self.farmer_id,
            'recommendation_id': self.recommendation_id,
            'action_taken': self.action_taken,
            'crop_planted': self.crop_planted,
            'yield_achieved': self.yield_achieved,
            'satisfaction_rating': self.satisfaction_rating,
            'comments': self.comments,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'harvest_date': self.harvest_date.isoformat() if self.harvest_date else None
        }

class SystemLog(db.Model):
    '''System Log model - tracks API usage and errors'''
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    log_type = db.Column(db.String(20))  # 'info', 'warning', 'error'
    endpoint = db.Column(db.String(100))
    method = db.Column(db.String(10))
    status_code = db.Column(db.Integer)
    message = db.Column(db.Text)
    user_id = db.Column(db.Integer)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<SystemLog {self.id} - {self.log_type}>'