#!/usr/bin/env python3
'''
Database Initialization Script
Run this to create tables and seed initial data
'''

from app import create_app
from models import db, Farmer
from datetime import datetime

def init_database():
    '''Initialize database with tables and sample data'''
    
    app = create_app('development')
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Tables created successfully")
        
        # Check if we need to seed data
        if Farmer.query.count() == 0:
            print("\nSeeding sample data...")
            
            # Sample farmers for testing
            sample_farmers = [
                {
                    'name': 'Jean Baptiste Mukiza',
                    'phone_number': '+250788123456',
                    'district': 'Kamonyi',
                    'sector': 'Musambira',
                    'cell': 'Cyeza',
                    'village': 'Nyarusange',
                    'farm_size': 0.5
                },
                {
                    'name': 'Marie Claire Uwase',
                    'phone_number': '+250788234567',
                    'district': 'Rwamagana',
                    'sector': 'Muhazi',
                    'cell': 'Gashoki',
                    'village': 'Kabuga',
                    'farm_size': 0.8
                },
                {
                    'name': 'Pierre Nkurunziza',
                    'phone_number': '+250788345678',
                    'district': 'Kamonyi',
                    'sector': 'Rukoma',
                    'cell': 'Nyamabuye',
                    'village': 'Gikoro',
                    'farm_size': 1.2
                }
            ]
            
            for farmer_data in sample_farmers:
                farmer = Farmer(**farmer_data)
                db.session.add(farmer)
            
            db.session.commit()
            print(f"✓ Added {len(sample_farmers)} sample farmers")
        
        print("\n" + "="*80)
        print("DATABASE INITIALIZATION COMPLETE")
        print("="*80)
        print(f"Total farmers: {Farmer.query.count()}")
        print("="*80)

if __name__ == '__main__':
    init_database()