import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    '''Base configuration'''
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///rwanda_soil.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # Model Paths
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/rwanda_soil_model_random_forest.pkl')
    SCALER_PATH = os.getenv('SCALER_PATH', 'models/feature_scaler.pkl')
    ENCODER_PATH = os.getenv('ENCODER_PATH', 'models/label_encoder.pkl')
    FEATURES_PATH = os.getenv('FEATURES_PATH', 'models/feature_names.pkl')
    METADATA_PATH = os.getenv('METADATA_PATH', 'models/model_metadata.json')
    
    # API Settings
    API_PORT = int(os.getenv('API_PORT', 5000))
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    
    # Pagination
    DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', 20))
    MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', 100))
    
    # Weather API
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    WEATHER_API_URL = os.getenv('WEATHER_API_URL')

class DevelopmentConfig(Config):
    '''Development configuration'''
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    '''Production configuration'''
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    '''Testing configuration'''
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}