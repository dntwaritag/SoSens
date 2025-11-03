#!/usr/bin/env python3
'''
Database Initialization Script for FastAPI
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def init_database():
    '''Initialize database with tables and sample data'''
    
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./rwanda_soil.db')
    
    # Create engine
    if DATABASE_URL.startswith('sqlite'):
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(DATABASE_URL)
    
    # Create all tables
    print("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if we need to seed data
        farmer_count = db.query(models.Farmer).count()
        
        if farmer_count == 0:
            print("\nSeeding sample data...")
            
            # Sample farmers for testing
            sample_farmers = [
                models.Farmer(
                    name='Jean Baptiste Mukiza',
                    phone_number='+250788123456',
                    district='Kamonyi',
                    sector='Musambira',
                    cell='Cyeza',
                    village='Nyarusange',
                    farm_size=0.5,
                    registered_at=datetime.utcnow(),
                    is_active=True
                ),
                models.Farmer(
                    name='Marie Claire Uwase',
                    phone_number='+250788234567',
                    district='Rwamagana',
                    sector='Muhazi',
                    cell='Gashoki',
                    village='Kabuga',
                    farm_size=0.8,
                    registered_at=datetime.utcnow(),
                    is_active=True
                ),
                models.Farmer(
                    name='Pierre Nkurunziza',
                    phone_number='+250788345678',
                    district='Kamonyi',
                    sector='Rukoma',
                    cell='Nyamabuye',
                    village='Gikoro',
                    farm_size=1.2,
                    registered_at=datetime.utcnow(),
                    is_active=True
                )
            ]
            
            for farmer in sample_farmers:
                db.add(farmer)
            
            db.commit()
            print(f"✓ Added {len(sample_farmers)} sample farmers")
        else:
            print(f"\nDatabase already contains {farmer_count} farmers")
        
        print("\n" + "="*80)
        print("DATABASE INITIALIZATION COMPLETE")
        print("="*80)
        print(f"Database URL: {DATABASE_URL}")
        print(f"Total farmers: {db.query(models.Farmer).count()}")
        print("="*80)
        
    finally:
        db.close()

if __name__ == '__main__':
    init_database()