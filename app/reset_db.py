# reset_db.py
from sqlalchemy import text
from database import engine
import models

def reset_database():
    print("Dropping all tables with CASCADE...")
    
    # Drop all tables with CASCADE to handle dependencies
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS feedback CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS recommendations CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS soil_readings CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS notifications CASCADE"))
        conn.commit()
    
    print("Creating all tables...")
    models.Base.metadata.create_all(bind=engine)
    
    print("Database reset complete!")

if __name__ == "__main__":
    reset_database()