#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models
from auth import get_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

def init_database():
    DATABASE_URL = os.getenv('DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    
    # Create tables
    print("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    print(" Tables created")
    
    # Seed data
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if admin exists
        admin = db.query(models.User).filter(models.User.role == models.UserRole.ADMIN).first()
        
        if not admin:
            print("\nCreating admin user...")
            admin = models.User(
                email="admin@rwandasoil.com",
                phone_number="+250788000000",
                hashed_password=get_password_hash("Admin@2024"),
                full_name="System Administrator",
                role=models.UserRole.ADMIN,
                district="Kigali",
                is_active=True,
                is_verified=True
            )
            db.add(admin)
            print(" Admin created")
            print("  Email: admin@rwandasoil.com")
            print("  Password: Admin@2024")
        
        # Check if sample farmers exist
        farmer_count = db.query(models.User).filter(models.User.role == models.UserRole.FARMER).count()
        
        if farmer_count == 0:
            print("\nCreating sample farmers...")
            
            farmers = [
                models.User(
                    email="jean@example.com",
                    phone_number="+250788111111",
                    hashed_password=get_password_hash("Farmer@123"),
                    full_name="Jean Baptiste Mukiza",
                    role=models.UserRole.FARMER,
                    district="Kamonyi",
                    sector="Musambira",
                    village="Nyarusange",
                    farm_size=0.5,
                    is_active=True
                ),
                models.User(
                    phone_number="+250788222222",
                    hashed_password=get_password_hash("Farmer@123"),
                    full_name="Marie Claire Uwase",
                    role=models.UserRole.FARMER,
                    district="Rwamagana",
                    sector="Muhazi",
                    village="Kabuga",
                    farm_size=0.8,
                    is_active=True
                )
            ]
            
            for farmer in farmers:
                db.add(farmer)
            
            print(f" Added {len(farmers)} sample farmers")
        
        db.commit()
        
        print("\n" + "="*80)
        print(" DATABASE INITIALIZATION COMPLETE")
        print("="*80)
        print(f"Total users: {db.query(models.User).count()}")
        print("="*80)
        
    finally:
        db.close()

if __name__ == '__main__':
    init_database()