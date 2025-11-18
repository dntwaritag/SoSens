"""
Initialize SoSens database with tables and admin user
"""

from .database import engine, SessionLocal
from . import models
from auth import get_password_hash
from datetime import datetime

def init_database():
    """Create all tables and admin user"""
    
    print("Creating database tables...")
    
    # Create all tables
    models.Base.metadata.create_all(bind=engine)
    print("✓ Tables created")
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(models.User).filter(
            models.User.email == "notifications.sosens@gmail.com"
        ).first()
        
        if existing_admin:
            print("Admin user already exists, skipping...")
            return
        
        print("Creating admin user...")
        
        # Create admin user with correct fields
        admin = models.User(
            email="notifications.sosens@gmail.com",
            phone_number="+250783074086",
            full_name="SoSens Administrator",
            hashed_password=get_password_hash("Admin@2025"),
            role=models.UserRole.ADMIN,
            district="Kigali",
            sector="Gasabo",
            village="Bumbogo",
            farm_size=0.0,
            preferred_contact="email",
            receive_notifications=True,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print(" Admin user created")
        print(f"  ID: {admin.id}")
        print(f"  Email: {admin.email}")
        print(f"  Phone: {admin.phone_number}")
        print(f"  Password: Admin@123456")
        print()
        print("=" * 60)
        print(" ADMIN CREDENTIALS")
        print("=" * 60)
        print(f"Email:    notifications.sosens@gmail.com")
        print(f"Password: Admin@2025")
        print(f"Role:     Administrator")
        print("=" * 60)
        print()
        print("  IMPORTANT: Change this password in production!")
        print()
        
    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_sample_farmer():
    """Create a sample farmer for testing"""
    
    db = SessionLocal()
    
    try:
        # Check if sample farmer already exists
        existing_farmer = db.query(models.User).filter(
            models.User.email == "farmer@gmail.com"
        ).first()
        
        if existing_farmer:
            print("⚠ Sample farmer already exists, skipping...")
            return
        
        print("Creating sample farmer user...")
        
        farmer = models.User(
            email="farmer@gmail.com",
            phone_number="+250788111111",
            full_name="John Farmer",
            hashed_password=get_password_hash("Farmer@123456"),
            role=models.UserRole.FARMER,
            district="Kigali",
            sector="Gasabo",
            village="Kimironko",
            farm_size=0.5,
            preferred_contact="email",
            receive_notifications=True,
            is_active=True
        )
        
        db.add(farmer)
        db.commit()
        db.refresh(farmer)
        
        print(" Sample farmer created")
        print(f"  ID: {farmer.id}")
        print(f"  Email: {farmer.email}")
        print(f"  Phone: {farmer.phone_number}")
        print(f"  District: {farmer.district}")
        print()
        print("=" * 60)
        print(" SAMPLE FARMER CREDENTIALS")
        print("=" * 60)
        print(f"Email:    farmer@gmail.com")
        print(f"Password: Farmer@2025")
        print(f"Role:     Farmer")
        print("=" * 60)
        print()
        
    except Exception as e:
        print(f" Error creating sample farmer: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def verify_database():
    """Verify database is set up correctly"""
    
    db = SessionLocal()
    
    try:
        print("Verifying database...")
        
        user_count = db.query(models.User).count()
        reading_count = db.query(models.SoilReading).count()
        rec_count = db.query(models.Recommendation).count()
        notif_count = db.query(models.NotificationLog).count()
        
        print(f" Database verification:")
        print(f"  - Users: {user_count}")
        print(f"  - Soil Readings: {reading_count}")
        print(f"  - Recommendations: {rec_count}")
        print(f"  - Notifications: {notif_count}")
        print()
        
    except Exception as e:
        print(f"✗ Database verification failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print()
    print("=" * 60)
    print(" SOSENS DATABASE INITIALIZATION")
    print("=" * 60)
    print()
    
    try:
        # Initialize database
        init_database()
        
        # Create sample farmer (optional)
        create_sample_farmer()
        
        # Verify
        verify_database()
        
        print("=" * 60)
        print("  DATABASE INITIALIZATION COMPLETE")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Start the API: uvicorn app:app --reload")
        print("2. Visit: http://localhost:8000/docs")
        print("3. Login with admin credentials above")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print(" INITIALIZATION FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        raise