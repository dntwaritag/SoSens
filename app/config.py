import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    
    # App
    APP_NAME = os.getenv('APP_NAME', 'SoSens Rwanda')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    
    # Database - FIXED for production
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        # Render uses postgres:// but newer versions need postgresql://
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY')
    ALGORITHM = os.getenv('ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 1440))
    
    # Services
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_FROM = os.getenv('MAIL_FROM')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    OPENWEATHER_BASE_URL = os.getenv('OPENWEATHER_BASE_URL', 'https://api.openweathermap.org/data/2.5')
    
    # ML Models
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/rwanda_soil_model_random_forest.pkl')
    SCALER_PATH = os.getenv('SCALER_PATH', 'models/feature_scaler.pkl')
    ENCODER_PATH = os.getenv('ENCODER_PATH', 'models/label_encoder.pkl')
    FEATURES_PATH = os.getenv('FEATURES_PATH', 'models/feature_names.pkl')
    METADATA_PATH = os.getenv('METADATA_PATH', 'models/model_metadata.json')
    
    # Notifications
    NOTIFICATION_TIME = os.getenv('NOTIFICATION_TIME', '06:00')
    TIMEZONE = os.getenv('TIMEZONE', 'Africa/Kigali')

settings = Settings()