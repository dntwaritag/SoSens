
# from fastapi import FastAPI, Depends, HTTPException, status, Request, Query
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from sqlalchemy.orm import Session
# from typing import List, Optional
# import os
# from datetime import datetime

# # Import database and models
# # NOTE: These imports (database, models, schemas, services, etc.) are assumed to exist
# # in your project structure for the code to run correctly.
# from database import get_db, engine
# import models
# import schemas

# # Import services
# from ml_service import MLPredictionService
# from sms_service import SMSService
# from preprocess import clean_phone_number, validate_location

# # Load environment variables
# from dotenv import load_dotenv
# load_dotenv()

# # Create database tables
# models.Base.metadata.create_all(bind=engine)

# # Initialize FastAPI app
# app = FastAPI(
#     title="Rwanda Soil Quality Monitoring API",
#     description="Machine Learning-powered soil quality monitoring and crop recommendation system for smallholder farmers in Rwanda",
#     version="1.0.0",
#     # ----------------------------------------
#     # SECURITY UPDATE: DISABLE DEFAULT DOCUMENTATION PAGES IN PRODUCTION
#     # Uncomment these lines in a production environment:
#     # docs_url=None,    
#     # redoc_url=None
#     # ----------------------------------------
# )

# # CORS Middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # In production, specify actual origins
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ============================================================================
# # INITIALIZE SERVICES
# # ============================================================================

# # Initialize ML Service
# ml_service = MLPredictionService(
#     model_path=os.getenv('MODEL_PATH', 'models/rwanda_soil_model_random_forest.pkl'),
#     scaler_path=os.getenv('SCALER_PATH', 'models/feature_scaler.pkl'),
#     encoder_path=os.getenv('ENCODER_PATH', 'models/label_encoder.pkl'),
#     features_path=os.getenv('FEATURES_PATH', 'models/feature_names.pkl'),
#     metadata_path=os.getenv('METADATA_PATH', 'models/model_metadata.json')
# )

# # Initialize SMS Service
# sms_service = None
# if os.getenv('TWILIO_ACCOUNT_SID') and os.getenv('TWILIO_AUTH_TOKEN'):
#     sms_service = SMSService(
#         account_sid=os.getenv('TWILIO_ACCOUNT_SID'),
#         auth_token=os.getenv('TWILIO_AUTH_TOKEN'),
#         phone_number=os.getenv('TWILIO_PHONE_NUMBER')
#     )
#     print("✓ SMS Service initialized")
# else:
#     print("⚠ SMS Service not configured")

# # ============================================================================
# # MIDDLEWARE FOR LOGGING
# # ============================================================================

# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     """Log all requests"""
#     start_time = datetime.utcnow()
#     response = await call_next(request)
#     process_time = (datetime.utcnow() - start_time).total_seconds()
    
#     # Log to database (optional)
    
#     response.headers["X-Process-Time"] = str(process_time)
#     return response

# # ============================================================================
# # ROOT & HEALTH ENDPOINTS
# # ============================================================================

# @app.get("/", tags=["Root"])
# async def root():
#     """API root endpoint with information"""
#     return {
#         "project": "Rwanda Soil Quality Monitoring System",
#         "version": "1.0.0",
#         "status": "active",
#         "documentation": "/docs" if app.docs_url else "Disabled",
#         "endpoints": {
#             "health": "/api/health",
#             "farmers": "/api/farmers",
#             "soil_readings": "/api/soil-readings",
#             "predict": "/api/predict",
#             "recommendations": "/api/recommendations",
#             "feedback": "/api/feedback",
#             "crops": "/api/crops",
#             "analytics": "/api/analytics/dashboard"
#         }
#     }

# # SECURITY UPDATE: HIDE HEALTH CHECK FROM DOCUMENTATION
# @app.get("/api/health", tags=["Health"], include_in_schema=False)
# async def health_check():
#     """Health check endpoint"""
#     return {
#         "status": "healthy",
#         "database": "connected",
#         "ml_model": "loaded",
#         "sms_service": "active" if sms_service else "inactive",
#         "timestamp": datetime.utcnow().isoformat()
#     }

# # ============================================================================
# # FARMER ENDPOINTS
# # ============================================================================

# @app.post("/api/farmers", response_model=schemas.FarmerResponse, status_code=status.HTTP_201_CREATED, tags=["Farmers"])
# async def create_farmer(farmer: schemas.FarmerCreate, db: Session = Depends(get_db)):
#     """Register a new farmer"""
    
#     # Clean phone number
#     phone = clean_phone_number(farmer.phone_number)
    
#     # Check if farmer exists
#     existing = db.query(models.Farmer).filter(models.Farmer.phone_number == phone).first()
#     if existing:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Farmer with this phone number already registered"
#         )
    
#     # Validate location
#     if not validate_location(farmer.district):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid district name"
#         )
    
#     # Create farmer
#     db_farmer = models.Farmer(
#         name=farmer.name,
#         phone_number=phone,
#         district=farmer.district,
#         sector=farmer.sector,
#         cell=farmer.cell,
#         village=farmer.village,
#         farm_size=farmer.farm_size
#     )
    
#     db.add(db_farmer)
#     db.commit()
#     db.refresh(db_farmer)
    
#     # Send welcome SMS
#     if sms_service:
#         sms_service.send_sms(
#             phone,
#             f"Welcome {farmer.name}! You are registered with Rwanda Soil Monitoring System. Send HELP for instructions."
#         )
    
#     return db_farmer

# @app.get("/api/farmers", response_model=List[schemas.FarmerResponse], tags=["Farmers"])
# async def list_farmers(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(20, ge=1, le=100),
#     district: Optional[str] = None,
#     db: Session = Depends(get_db)
# ):
#     """Get list of farmers with pagination"""
    
#     query = db.query(models.Farmer)
    
#     if district:
#         query = query.filter(models.Farmer.district == district)
    
#     farmers = query.offset(skip).limit(limit).all()
#     return farmers

# @app.get("/api/farmers/{farmer_id}", response_model=schemas.FarmerResponse, tags=["Farmers"])
# async def get_farmer(farmer_id: int, db: Session = Depends(get_db)):
#     """Get specific farmer details"""
    
#     farmer = db.query(models.Farmer).filter(models.Farmer.id == farmer_id).first()
#     if not farmer:
#         raise HTTPException(status_code=404, detail="Farmer not found")
    
#     return farmer

# @app.put("/api/farmers/{farmer_id}", response_model=schemas.FarmerResponse, tags=["Farmers"])
# async def update_farmer(farmer_id: int, farmer_update: schemas.FarmerUpdate, db: Session = Depends(get_db)):
#     """Update farmer information"""
    
#     farmer = db.query(models.Farmer).filter(models.Farmer.id == farmer_id).first()
#     if not farmer:
#         raise HTTPException(status_code=404, detail="Farmer not found")
    
#     # Update fields
#     update_data = farmer_update.dict(exclude_unset=True)
#     for field, value in update_data.items():
#         setattr(farmer, field, value)
    
#     db.commit()
#     db.refresh(farmer)
    
#     return farmer

# # NOTE: This DELETE endpoint should likely be restricted with authorization,
# # but for documentation simplicity, we'll leave it visible for now.
# @app.delete("/api/farmers/{farmer_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Farmers"])
# async def delete_farmer(farmer_id: int, db: Session = Depends(get_db)):
#     """Delete a farmer"""
    
#     farmer = db.query(models.Farmer).filter(models.Farmer.id == farmer_id).first()
#     if not farmer:
#         raise HTTPException(status_code=404, detail="Farmer not found")
    
#     db.delete(farmer)
#     db.commit()
    
#     return None

# # ============================================================================
# # SOIL READING ENDPOINTS
# # ============================================================================

# @app.post("/api/soil-readings", response_model=schemas.SoilReadingResponse, status_code=status.HTTP_201_CREATED, tags=["Soil Readings"])
# async def create_soil_reading(reading: schemas.SoilReadingCreate, db: Session = Depends(get_db)):
#     """Submit a new soil reading"""
    
#     # Verify farmer exists
#     farmer = db.query(models.Farmer).filter(models.Farmer.id == reading.farmer_id).first()
#     if not farmer:
#         raise HTTPException(status_code=404, detail="Farmer not found")
    
#     # Create soil reading
#     db_reading = models.SoilReading(**reading.dict())
#     db.add(db_reading)
#     db.commit()
#     db.refresh(db_reading)
    
#     return db_reading

# @app.get("/api/soil-readings", response_model=List[schemas.SoilReadingResponse], tags=["Soil Readings"])
# async def list_soil_readings(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(20, ge=1, le=100),
#     farmer_id: Optional[int] = None,
#     db: Session = Depends(get_db)
# ):
#     """Get list of soil readings"""
    
#     query = db.query(models.SoilReading)
    
#     if farmer_id:
#         query = query.filter(models.SoilReading.farmer_id == farmer_id)
    
#     readings = query.order_by(models.SoilReading.reading_date.desc()).offset(skip).limit(limit).all()
#     return readings

# # ============================================================================
# # PREDICTION ENDPOINT
# # ============================================================================

# @app.post("/api/predict", response_model=schemas.PredictionResponse, tags=["Predictions"])
# async def predict_crop(request: schemas.PredictionRequest, db: Session = Depends(get_db)):
#     """Generate crop recommendation based on soil data"""
    
#     # Verify farmer if provided
#     farmer = None
#     if request.farmer_id:
#         farmer = db.query(models.Farmer).filter(models.Farmer.id == request.farmer_id).first()
#         if not farmer:
#             raise HTTPException(status_code=404, detail="Farmer not found")
    
#     # Prepare soil data
#     soil_data = {
#         'Ph': request.ph,
#         'N': request.nitrogen,
#         'P': request.phosphorus,
#         'K': request.potassium,
#         'Zn': request.zinc,
#         'S': request.sulfur
#     }
    
#     # Make prediction
#     result = ml_service.predict(soil_data)
    
#     if not result['success']:
#         raise HTTPException(status_code=400, detail=result.get('error', 'Prediction failed'))
    
#     # Save reading and recommendation if farmer provided
#     if farmer:
#         # Save soil reading
#         db_reading = models.SoilReading(
#             farmer_id=farmer.id,
#             ph=request.ph,
#             nitrogen=request.nitrogen,
#             phosphorus=request.phosphorus,
#             potassium=request.potassium,
#             zinc=request.zinc,
#             sulfur=request.sulfur,
#             reading_source='api'
#         )
#         db.add(db_reading)
#         db.flush()
        
#         # Save recommendation
#         db_recommendation = models.Recommendation(
#             farmer_id=farmer.id,
#             soil_reading_id=db_reading.id,
#             recommended_crop=result['prediction']['crop'],
#             confidence_score=result['prediction']['confidence'],
#             alternative_crops=result['alternatives'],
#             soil_health_status=result['soil_health']['status'],
#             soil_issues=result['soil_health']['issues'],
#             fertilizer_recommendation=result['recommendations']['fertilizer'],
#             planting_season=result['recommendations']['planting_season'],
#             spacing_recommendation=result['recommendations']['spacing'],
#             additional_tips='\n'.join(result['recommendations']['tips']),
#             delivered_via='api'
#         )
#         db.add(db_recommendation)
#         db.commit()
#         db.refresh(db_recommendation)
        
#         result['recommendation_id'] = db_recommendation.id
#         result['reading_id'] = db_reading.id
        
#         # Send SMS if requested
#         if request.send_sms and sms_service:
#             sms_result = sms_service.send_recommendation(farmer.phone_number, result)
#             if sms_result['success']:
#                 db_recommendation.is_delivered = True
#                 db_recommendation.delivered_via = 'sms'
#                 db.commit()
    
#     return result

# # ============================================================================
# # RECOMMENDATION ENDPOINTS
# # ============================================================================

# @app.get("/api/recommendations", response_model=List[schemas.RecommendationResponse], tags=["Recommendations"])
# async def list_recommendations(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(20, ge=1, le=100),
#     farmer_id: Optional[int] = None,
#     db: Session = Depends(get_db)
# ):
#     """Get list of recommendations"""
    
#     query = db.query(models.Recommendation)
    
#     if farmer_id:
#         query = query.filter(models.Recommendation.farmer_id == farmer_id)
    
#     recommendations = query.order_by(models.Recommendation.created_at.desc()).offset(skip).limit(limit).all()
#     return recommendations

# # ============================================================================
# # FEEDBACK ENDPOINTS
# # ============================================================================

# @app.post("/api/feedback", response_model=schemas.FeedbackResponse, status_code=status.HTTP_201_CREATED, tags=["Feedback"])
# async def create_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
#     """Submit farmer feedback"""
    
#     # Verify farmer and recommendation exist
#     farmer = db.query(models.Farmer).filter(models.Farmer.id == feedback.farmer_id).first()
#     if not farmer:
#         raise HTTPException(status_code=404, detail="Farmer not found")
    
#     recommendation = db.query(models.Recommendation).filter(
#         models.Recommendation.id == feedback.recommendation_id
#     ).first()
#     if not recommendation:
#         raise HTTPException(status_code=404, detail="Recommendation not found")
    
#     # Create feedback
#     db_feedback = models.Feedback(**feedback.dict())
#     db.add(db_feedback)
#     db.commit()
#     db.refresh(db_feedback)
    
#     return db_feedback

# @app.get("/api/feedback", response_model=List[schemas.FeedbackResponse], tags=["Feedback"])
# async def list_feedback(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(20, ge=1, le=100),
#     farmer_id: Optional[int] = None,
#     db: Session = Depends(get_db)
# ):
#     """Get list of feedback"""
    
#     query = db.query(models.Feedback)
    
#     if farmer_id:
#         query = query.filter(models.Feedback.farmer_id == farmer_id)
    
#     feedback_list = query.order_by(models.Feedback.submitted_at.desc()).offset(skip).limit(limit).all()
#     return feedback_list

# # ============================================================================
# # SMS WEBHOOK ENDPOINT
# # ============================================================================

# # SECURITY UPDATE: HIDE SMS WEBHOOK FROM DOCUMENTATION
# @app.post("/api/sms/webhook", tags=["SMS"], include_in_schema=False)
# async def sms_webhook(request: Request, db: Session = Depends(get_db)):
#     """Handle incoming SMS from Twilio"""
    
#     if not sms_service:
#         raise HTTPException(status_code=503, detail="SMS service not configured")
    
#     # Get form data from Twilio
#     form_data = await request.form()
#     from_number = form_data.get('From', '')
#     message_body = form_data.get('Body', '')
    
#     # Clean phone number
#     phone = clean_phone_number(from_number)
    
#     # Find farmer
#     farmer = db.query(models.Farmer).filter(models.Farmer.phone_number == phone).first()
    
#     # Handle HELP command
#     if 'HELP' in message_body.upper():
#         sms_service.send_help_message(phone)
#         return {"status": "help_sent"}
    
#     # Parse soil data
#     soil_data = sms_service.parse_incoming_sms(message_body)
    
#     if not soil_data:
#         sms_service.send_sms(
#             phone,
#             "Invalid format. Send: SOIL [pH] [N] [P] [K]\nExample: SOIL 6.5 40 20 200\nOr send HELP"
#         )
#         return {"status": "invalid_format"}
    
#     # Register farmer if not exists
#     if not farmer:
#         farmer = models.Farmer(
#             name=f"Farmer {phone[-4:]}",
#             phone_number=phone,
#             district="Unknown"
#         )
#         db.add(farmer)
#         db.commit()
#         db.refresh(farmer)
    
#     # Make prediction
#     result = ml_service.predict(soil_data)
    
#     if result['success']:
#         # Save soil reading
#         db_reading = models.SoilReading(
#             farmer_id=farmer.id,
#             ph=soil_data['Ph'],
#             nitrogen=soil_data['N'],
#             phosphorus=soil_data['P'],
#             potassium=soil_data['K'],
#             # Assuming Zn and S might be optional/defaulted for SMS input
#             zinc=soil_data.get('Zn'), 
#             sulfur=soil_data.get('S'),
#             reading_source='sms'
#         )
#         db.add(db_reading)
#         db.flush()
        
#         # Save recommendation
#         db_recommendation = models.Recommendation(
#             farmer_id=farmer.id,
#             soil_reading_id=db_reading.id,
#             recommended_crop=result['prediction']['crop'],
#             confidence_score=result['prediction']['confidence'],
#             alternative_crops=result['alternatives'],
#             soil_health_status=result['soil_health']['status'],
#             soil_issues=result['soil_health']['issues'],
#             fertilizer_recommendation=result['recommendations']['fertilizer'],
#             planting_season=result['recommendations']['planting_season'],
#             spacing_recommendation=result['recommendations']['spacing'],
#             delivered_via='sms',
#             is_delivered=False
#         )
#         db.add(db_recommendation)
#         db.commit()
        
#         # Send recommendation via SMS
#         sms_result = sms_service.send_recommendation(phone, result)
        
#         if sms_result['success']:
#             db_recommendation.is_delivered = True
#             db.commit()
        
#         return {"status": "recommendation_sent"}
#     else:
#         sms_service.send_sms(
#             phone,
#             f"Error processing your request: {result.get('error', 'Unknown error')}"
#         )
#         return {"status": "error"}

# # ============================================================================
# # CROPS ENDPOINTS
# # ============================================================================

# @app.get("/api/crops", tags=["Crops"])
# async def list_crops():
#     """List all supported crops"""
#     crops = ml_service.list_supported_crops()
#     return {
#         "success": True,
#         "total_crops": len(crops),
#         "crops": crops
#     }

# @app.get("/api/crops/{crop_name}", tags=["Crops"])
# async def get_crop_info(crop_name: str):
#     """Get detailed information about a specific crop"""
#     result = ml_service.get_crop_info(crop_name)
    
#     if not result['success']:
#         raise HTTPException(status_code=404, detail=f"Crop '{crop_name}' not found")
    
#     return result

# # ============================================================================
# # ANALYTICS ENDPOINTS
# # ============================================================================

# # SECURITY UPDATE: HIDE ANALYTICS DASHBOARD FROM DOCUMENTATION (and ideally secure with Auth)
# @app.get("/api/analytics/dashboard", response_model=schemas.DashboardResponse, tags=["Analytics"], include_in_schema=False)
# async def analytics_dashboard(db: Session = Depends(get_db)):
#     """Get dashboard analytics"""
    
#     from sqlalchemy import func
    
#     # Total counts
#     total_farmers = db.query(func.count(models.Farmer.id)).scalar()
#     active_farmers = db.query(func.count(models.Farmer.id)).filter(
#         models.Farmer.is_active == True
#     ).scalar()
#     total_readings = db.query(func.count(models.SoilReading.id)).scalar()
#     total_recommendations = db.query(func.count(models.Recommendation.id)).scalar()
#     total_feedback = db.query(func.count(models.Feedback.id)).scalar()
    
#     # Average satisfaction
#     avg_satisfaction = db.query(func.avg(models.Feedback.satisfaction_rating)).scalar() or 0.0
    
#     # District distribution
#     district_stats = db.query(
#         models.Farmer.district,
#         func.count(models.Farmer.id)
#     ).group_by(models.Farmer.district).all()
    
#     # Top crops
#     crop_stats = db.query(
#         models.Recommendation.recommended_crop,
#         func.count(models.Recommendation.id)
#     ).group_by(models.Recommendation.recommended_crop).order_by(
#         func.count(models.Recommendation.id).desc()
#     ).limit(10).all()
    
#     # Soil health distribution
#     soil_health_stats = db.query(
#         models.Recommendation.soil_health_status,
#         func.count(models.Recommendation.id)
#     ).group_by(models.Recommendation.soil_health_status).all()
    
#     return {
#         "success": True,
#         "summary": {
#             "total_farmers": total_farmers,
#             "active_farmers": active_farmers,
#             "total_soil_readings": total_readings,
#             "total_recommendations": total_recommendations,
#             "total_feedback": total_feedback,
#             "average_satisfaction": round(avg_satisfaction, 2)
#         },
#         "districts": [
#             {"district": d[0], "farmers": d[1]} 
#             for d in district_stats
#         ],
#         "top_crops": [
#             {"crop": c[0], "count": c[1]} 
#             for c in crop_stats
#         ],
#         "soil_health": [
#             {"status": s[0] or "Unknown", "count": s[1]} 
#             for s in soil_health_stats
#         ]
#     }

# # SECURITY UPDATE: HIDE SOIL TRENDS FROM DOCUMENTATION (and ideally secure with Auth)
# @app.get("/api/analytics/soil-trends", tags=["Analytics"], include_in_schema=False)
# async def soil_trends(
#     farmer_id: Optional[int] = None,
#     district: Optional[str] = None,
#     db: Session = Depends(get_db)
# ):
#     """Get soil parameter trends over time"""
    
#     query = db.query(models.SoilReading)
    
#     if farmer_id:
#         query = query.filter(models.SoilReading.farmer_id == farmer_id)
#     elif district:
#         query = query.join(models.Farmer).filter(models.Farmer.district == district)
    
#     readings = query.order_by(models.SoilReading.reading_date).all()
    
#     return {
#         "success": True,
#         "data": [
#             {
#                 "date": r.reading_date.isoformat(),
#                 "ph": r.ph,
#                 "nitrogen": r.nitrogen,
#                 "phosphorus": r.phosphorus,
#                 "potassium": r.potassium
#             }
#             for r in readings
#         ]
#     }

# # ============================================================================
# # ERROR HANDLERS
# # ============================================================================

# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     """Handle HTTP exceptions"""
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={
#             "success": False,
#             "error": exc.detail,
#             "status_code": exc.status_code
#         }
#     )

# @app.exception_handler(Exception)
# async def general_exception_handler(request: Request, exc: Exception):
#     """Handle general exceptions"""
#     return JSONResponse(
#         status_code=500,
#         content={
#             "success": False,
#             "error": "Internal server error",
#             "detail": str(exc)
#         }
#     )

# # ============================================================================
# # STARTUP & SHUTDOWN EVENTS
# # ============================================================================

# @app.on_event("startup")
# async def startup_event():
#     """Run on application startup"""
#     print("\n" + "="*80)
#     print("RWANDA SOIL QUALITY MONITORING SYSTEM - FASTAPI")
#     print("="*80)
#     print(f"ML Model: Loaded")
#     print(f"SMS Service: {'Active' if sms_service else 'Inactive'}")
#     print(f"Database: Connected")
#     print("="*80)
#     print("\n Server started successfully!")
#     print(f" API Documentation: http://localhost:{os.getenv('API_PORT', 5000)}/docs" if app.docs_url else " API Documentation: Disabled")
#     print(f" ReDoc: http://localhost:{os.getenv('API_PORT', 5000)}/redoc" if app.redoc_url else " ReDoc: Disabled")
#     print("="*80 + "\n")

# @app.on_event("shutdown")
# async def shutdown_event():
#     """Run on application shutdown"""
#     print("\n" + "="*80)
#     print("Shutting down gracefully...")
#     print("="*80 + "\n")

# # ============================================================================
# # MAIN ENTRY POINT
# # ============================================================================

# if __name__ == "__main__":
#     import uvicorn
    
#     port = int(os.getenv('API_PORT', 5000))
#     host = os.getenv('API_HOST', '0.0.0.0')
    
#     uvicorn.run(
#         "app:app",
#         host=host,
#         port=port,
#         reload=True,  # Auto-reload on code changes (development only)
#         log_level="info"
#     )

# --------------------------------------------------------------------
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from datetime import datetime

import os

# Import all modules
from database import get_db, engine
import models
import schemas
from auth import (
    authenticate_user, create_access_token, get_current_user, 
    get_current_admin, get_password_hash, create_reset_token
)
from ml_service import MLPredictionService
from weather_service import WeatherService
from notification_service import notification_service
from scheduler import start_scheduler, stop_scheduler

# Create tables
models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="Rwanda Soil Quality Monitoring API",
    description="ML-powered soil monitoring with authentication and notifications",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ml_service = MLPredictionService(
    model_path=os.getenv('MODEL_PATH'),
    scaler_path=os.getenv('SCALER_PATH'),
    encoder_path=os.getenv('ENCODER_PATH'),
    features_path=os.getenv('FEATURES_PATH'),
    metadata_path=os.getenv('METADATA_PATH')
)
weather_service = WeatherService()

# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    start_scheduler()
    print("="*80)
    print(" SoSens API - STARTED")
    print("="*80)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    stop_scheduler()
    print("Shutting down...")

# ============================================================================
# ROOT & HEALTH
# ============================================================================

@app.get("/")
async def root():
    """API root"""
    return {
        "app": "Rwanda Soil Quality Monitoring API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: schemas.UserRegister, db: Session = Depends(get_db)):
    """Register new user (farmer or admin)"""
    
    # Check if user exists
    if user_data.email:
        existing = db.query(models.User).filter(models.User.email == user_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    if user_data.phone_number:
        existing = db.query(models.User).filter(models.User.phone_number == user_data.phone_number).first()
        if existing:
            raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    
    new_user = models.User(
        email=user_data.email,
        phone_number=user_data.phone_number,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        district=user_data.district,
        sector=user_data.sector,
        village=user_data.village,
        farm_size=user_data.farm_size,
        preferred_contact=user_data.preferred_contact.value,
        receive_notifications=user_data.receive_notifications
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Send welcome notification
    if user_data.preferred_contact == schemas.ContactMethod.SMS and user_data.phone_number:
        await notification_service.send_sms(
            user_data.phone_number,
            f"Welcome {user_data.full_name}! Your SoSens account is ready.",
            db,
            new_user.id
        )
    elif user_data.preferred_contact == schemas.ContactMethod.EMAIL and user_data.email:
        await notification_service.send_email(
            user_data.email,
            "Welcome to SoSens",
            f"<h2>Welcome {user_data.full_name}!</h2><p>Your account has been created successfully.</p>",
            db,
            new_user.id
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": new_user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }

# @app.post("/api/auth/login", response_model=schemas.Token)
# async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     """Login with email or phone"""
    
#     user = authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email/phone or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     # Update last login
#     user.last_login = datetime.utcnow()
#     db.commit()
    
#     # Create access token
#     access_token = create_access_token(data={"sub": user.id})
    
#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "user": user
#     }
@app.post("/api/auth/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/phone or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})  # Ensure it's string
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user  # This should match your Token schema
    }


@app.get("/api/auth/me", response_model=schemas.UserResponse)
async def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """Get current user info"""
    return current_user

@app.post("/api/auth/forgot-password")
async def forgot_password(data: schemas.PasswordReset, db: Session = Depends(get_db)):
    """Request password reset"""
    
    # Find user
    user = db.query(models.User).filter(
        (models.User.email == data.username) | (models.User.phone_number == data.username)
    ).first()
    
    if not user:
        # Don't reveal if user exists
        return {"message": "If account exists, reset instructions have been sent"}
    
    # Generate reset token
    reset_token = create_reset_token()
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    
    # Send reset link
    reset_link = f"https://your-app.com/reset-password?token={reset_token}"
    
    if user.email:
        await notification_service.send_email(
            user.email,
            "Password Reset Request",
            f"<p>Click here to reset your password: <a href='{reset_link}'>{reset_link}</a></p><p>Link expires in 1 hour.</p>",
            db,
            user.id
        )
    elif user.phone_number:
        await notification_service.send_sms(
            user.phone_number,
            f"Password reset code: {reset_token[:8]}. Valid for 1 hour.",
            db,
            user.id
        )
    
    return {"message": "If account exists, reset instructions have been sent"}

@app.post("/api/auth/reset-password")
async def reset_password(data: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password with token"""
    
    user = db.query(models.User).filter(models.User.reset_token == data.token).first()
    
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Update password
    user.hashed_password = get_password_hash(data.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return {"message": "Password reset successful"}

# ============================================================================
# SOIL READING ENDPOINTS
# ============================================================================

@app.post("/api/soil-readings", response_model=dict)
async def create_soil_reading(
    reading: schemas.SoilReadingCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit soil reading"""
    
    new_reading = models.SoilReading(
        user_id=current_user.id,
        **reading.dict()
    )
    
    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)
    
    return {
        "success": True,
        "message": "Soil reading saved",
        "reading_id": new_reading.id
    }

@app.get("/api/soil-readings")
async def get_soil_readings(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's soil readings"""
    
    readings = db.query(models.SoilReading).filter(
        models.SoilReading.user_id == current_user.id
    ).order_by(models.SoilReading.reading_date.desc()).limit(50).all()
    
    return {"readings": readings}

# ============================================================================
# PREDICTION ENDPOINT
# ============================================================================

@app.post("/api/predict", response_model=schemas.PredictionResponse)
async def get_crop_recommendation(
    request: schemas.PredictionRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get crop recommendation with weather integration"""
    
    # Prepare soil data
    soil_data = {
        'Ph': request.ph,
        'N': request.nitrogen,
        'P': request.phosphorus,
        'K': request.potassium,
        'Zn': request.zinc or 5.0,
        'S': request.sulfur or 15.0
    }
    
    # Get prediction
    result = ml_service.predict(soil_data)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    # Get weather if requested
    weather_advice = None
    if request.include_weather and current_user.district:
        weather = weather_service.get_weather(current_user.district, db)
        if weather:
            weather_advice = weather['advice']
    
    # Save reading
    reading = models.SoilReading(
        user_id=current_user.id,
        ph=request.ph,
        nitrogen=request.nitrogen,
        phosphorus=request.phosphorus,
        potassium=request.potassium,
        zinc=request.zinc,
        sulfur=request.sulfur
    )
    db.add(reading)
    db.flush()
    
    # Save recommendation
    recommendation = models.Recommendation(
        user_id=current_user.id,
        soil_reading_id=reading.id,
        recommended_crop=result['prediction']['crop'],
        confidence_score=result['prediction']['confidence'],
        alternative_crops=result['alternatives'],
        soil_health_status=result['soil_health']['status'],
        soil_issues=result['soil_health']['issues'],
        fertilizer_recommendation=result['recommendations']['fertilizer'],
        planting_season=result['recommendations']['planting_season'],
        weather_advice=weather_advice
    )
    db.add(recommendation)
    db.commit()
    
    # Send notification
    message = f""" New Soil Recommendation

Crop: {result['prediction']['crop']}
Confidence: {result['prediction']['confidence_percent']}
Soil: {result['soil_health']['status']}

Fertilizer: {result['recommendations']['fertilizer']}
Season: {result['recommendations']['planting_season']}

{weather_advice or ''}"""
    
    if current_user.preferred_contact == 'sms' and current_user.phone_number:
        await notification_service.send_sms(current_user.phone_number, message, db, current_user.id)
    elif current_user.preferred_contact == 'email' and current_user.email:
        await notification_service.send_email(
            current_user.email,
            "Your Crop Recommendation",
            message.replace('\n', '<br>'),
            db,
            current_user.id
        )
    
    return {
        "success": True,
        "crop": result['prediction']['crop'],
        "confidence": result['prediction']['confidence'],
        "soil_health": result['soil_health']['status'],
        "fertilizer_advice": result['recommendations']['fertilizer'],
        "planting_season": result['recommendations']['planting_season'],
        "weather_advice": weather_advice,
        "alternatives": result['alternatives']
    }

# ============================================================================
# WEATHER ENDPOINT
# ============================================================================

@app.get("/api/weather", response_model=schemas.WeatherResponse)
async def get_weather(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current weather for user's district"""
    
    if not current_user.district:
        raise HTTPException(status_code=400, detail="District not set in profile")
    
    weather = weather_service.get_weather(current_user.district, db)
    
    if not weather:
        raise HTTPException(status_code=503, detail="Weather service unavailable")
    
    return weather

# ============================================================================
# RECOMMENDATION HISTORY
# ============================================================================

@app.get("/api/recommendations")
async def get_recommendations(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's recommendation history"""
    
    recommendations = db.query(models.Recommendation).filter(
        models.Recommendation.user_id == current_user.id
    ).order_by(models.Recommendation.created_at.desc()).limit(20).all()
    
    return {"recommendations": recommendations}

# ============================================================================
# USER PREFERENCES
# ============================================================================

@app.put("/api/preferences")
async def update_preferences(
    preferences: schemas.NotificationPreferences,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update notification preferences"""
    
    current_user.receive_notifications = preferences.receive_notifications
    current_user.preferred_contact = preferences.preferred_contact.value
    
    db.commit()
    
    return {"message": "Preferences updated successfully"}

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.get("/api/admin/users")
async def get_all_users(
    skip: int = 0,
    limit: int = 50,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin: Get all users"""
    
    users = db.query(models.User).offset(skip).limit(limit).all()
    total = db.query(models.User).count()
    
    return {
        "users": users,
        "total": total,
        "page": skip // limit + 1
    }

@app.get("/api/admin/analytics")
async def get_analytics(
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin: Get system analytics"""
    
    from sqlalchemy import func
    
    total_users = db.query(func.count(models.User.id)).scalar()
    active_users = db.query(func.count(models.User.id)).filter(models.User.is_active == True).scalar()
    total_readings = db.query(func.count(models.SoilReading.id)).scalar()
    total_recommendations = db.query(func.count(models.Recommendation.id)).scalar()
    
    # Top crops
    top_crops = db.query(
        models.Recommendation.recommended_crop,
        func.count(models.Recommendation.id).label('count')
    ).group_by(models.Recommendation.recommended_crop).order_by(
        func.count(models.Recommendation.id).desc()
    ).limit(5).all()
    
    # Users by district
    users_by_district = db.query(
        models.User.district,
        func.count(models.User.id).label('count')
    ).group_by(models.User.district).all()
    
    return {
        "summary": {
            "total_users": total_users,
            "active_users": active_users,
            "total_readings": total_readings,
            "total_recommendations": total_recommendations
        },
        "top_crops": [{"crop": c[0], "count": c[1]} for c in top_crops],
        "users_by_district": [{"district": d[0], "count": d[1]} for d in users_by_district]
    }

@app.post("/api/admin/send-notification")
async def send_bulk_notification(
    message: str,
    district: str = None,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin: Send notification to farmers"""
    
    query = db.query(models.User).filter(
        models.User.role == models.UserRole.FARMER,
        models.User.is_active == True,
        models.User.receive_notifications == True
    )
    
    if district:
        query = query.filter(models.User.district == district)
    
    users = query.all()
    
    sent_count = 0
    for user in users:
        if user.preferred_contact == 'sms' and user.phone_number:
            success = await notification_service.send_sms(user.phone_number, message, db, user.id)
            if success:
                sent_count += 1
        elif user.preferred_contact == 'email' and user.email:
            success = await notification_service.send_email(
                user.email,
                "Important Update",
                message,
                db,
                user.id
            )
            if success:
                sent_count += 1
    
    return {
        "message": f"Notification sent to {sent_count} users",
        "total_users": len(users)
    }

# ============================================================================
# CROPS INFO
# ============================================================================

@app.get("/api/crops")
async def list_crops():
    """List supported crops"""
    crops = ml_service.list_supported_crops()
    return {
        "crops": crops,
        "total": len(crops)
    }

@app.get("/api/crops/{crop_name}")
async def get_crop_details(crop_name: str):
    """Get crop details"""
    result = ml_service.get_crop_info(crop_name)
    
    if not result['success']:
        raise HTTPException(status_code=404, detail="Crop not found")
    
    return result

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('API_PORT', 5000))
    host = os.getenv('API_HOST', '0.0.0.0')
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True
    )



# ------------------------------------------------
"""
SoSens API - Production Ready
Fixed and optimized version with all endpoints working
"""

# from fastapi import FastAPI, Depends, HTTPException, status, Body
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.security import OAuth2PasswordRequestForm
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import OperationalError, ProgrammingError
# from sqlalchemy import text      
# from typing import List, Optional
# from datetime import timedelta, datetime
# import os

# # Import all modules
# from database import get_db, engine
# import models
# import schemas
# import auth
# from auth import (
#     authenticate_user, create_access_token, get_current_user, 
#     get_current_admin, get_password_hash, create_reset_token
# )
# from ml_service import MLPredictionService
# from weather_service import WeatherService
# from notification_service import notification_service
# from scheduler import start_scheduler, stop_scheduler

# # Create tables
# models.Base.metadata.create_all(bind=engine)

# # Initialize FastAPI
# app = FastAPI(
#     title="SoSens - Rwanda Soil Quality Monitoring API",
#     description="ML-powered soil monitoring with authentication, weather integration, and automated notifications",
#     version="1.0.0",
#     contact={
#         "name": "SoSens Support",
#         "email": "support@sosens.rw"
#     }
# )

# # CORS - Configure for production
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Change to specific origins in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ============================================================================
# # INITIALIZE SERVICES
# # ============================================================================

# try:
#     ml_service = MLPredictionService(
#         model_path=os.getenv('MODEL_PATH', 'models/rwanda_soil_model_random_forest.pkl'),
#         scaler_path=os.getenv('SCALER_PATH', 'models/feature_scaler.pkl'),
#         encoder_path=os.getenv('ENCODER_PATH', 'models/label_encoder.pkl'),
#         features_path=os.getenv('FEATURES_PATH', 'models/feature_names.pkl'),
#         metadata_path=os.getenv('METADATA_PATH', 'models/model_metadata.json')
#     )
#     print(" ML Service initialized")
# except Exception as e:
#     print(f" ML Service failed to initialize: {e}")
#     ml_service = None

# weather_service = WeatherService()
# print(" Weather Service initialized")

# # ============================================================================
# # STARTUP & SHUTDOWN
# # ============================================================================

# @app.on_event("startup")
# async def startup_event():
#     """Initialize on startup"""
#     try:
#         start_scheduler()
#         print("="*80)
#         print(" SoSens API - STARTED")
#         print("="*80)
#         print(f" Environment: {os.getenv('FLASK_ENV', 'development')}")
#         print(f" ML Model: {'Loaded' if ml_service else 'Not Available'}")
#         print(f" Weather Service: Active")
#         print(f" Notifications: Configured")
#         print("="*80)
#     except Exception as e:
#         print(f" Startup warning: {e}")

# @app.on_event("shutdown")
# async def shutdown_event():
#     """Cleanup on shutdown"""
#     try:
#         stop_scheduler()
#         print("\n Shutting down...")
#     except:
#         pass

# # ============================================================================
# # ROOT & HEALTH
# # ============================================================================

# @app.get("/", tags=["System"])
# async def root():
#     """API root - System information"""
#     return {
#         "app": "SoSens - Rwanda Soil Quality Monitoring",
#         "version": "1.0.0",
#         "status": "operational",
#         "documentation": "/docs",
#         "endpoints": {
#             "auth": "/api/auth/*",
#             "predictions": "/api/predict",
#             "weather": "/api/weather",
#             "crops": "/api/crops",
#             "admin": "/api/admin/*"
#         }
#     }

# @app.get("/api/health", tags=["System"])
# async def health_check(db: Session = Depends(get_db)):
#     """System health check"""
    
#     # Check database
#     db_status = "connected"
#     try:
#         db.execute(text("SELECT 1")) # Use text() for best practice in SQLAlchemy 2.0+
#     except (OperationalError, ProgrammingError) as e: 
#         # OperationalError 
#         # ProgrammingError 
#         print(f"Database check failed: {e}") # Log the error
#         db_status = "disconnected"
#     except Exception as e:
#         # Catch unexpected errors, but ensure they are logged
#         print(f"Unexpected health check error: {e}") 
#         db_status = "error" # Use a different status for non-DB failures
    
#     return {
#         "status": "healthy" if db_status == "connected" else "degraded",
#         "timestamp": datetime.utcnow().isoformat(),
#         "services": {
#             "database": db_status,
#             "ml_model": "loaded" if ml_service else "unavailable",
#             "weather": "active",
#             "notifications": "active"
#         }
#     }

# # ============================================================================
# # AUTHENTICATION ENDPOINTS
# # ============================================================================

# @app.post("/api/auth/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
# async def register(user_data: schemas.UserRegister, db: Session = Depends(get_db)):
#     """
#     Register new user (farmer or admin)
    
#     - **Email OR Phone required** (at least one)
#     - **Password**: Minimum 8 characters
#     - **Role**: farmer or admin
#     """
    
#     # Validate at least one contact method
#     if not user_data.email and not user_data.phone_number:
#         raise HTTPException(
#             status_code=400, 
#             detail="Either email or phone number must be provided"
#         )
    
#     # Check if user exists
#     if user_data.email:
#         existing = db.query(models.User).filter(models.User.email == user_data.email).first()
#         if existing:
#             raise HTTPException(status_code=400, detail="Email already registered")
    
#     if user_data.phone_number:
#         existing = db.query(models.User).filter(models.User.phone_number == user_data.phone_number).first()
#         if existing:
#             raise HTTPException(status_code=400, detail="Phone number already registered")
    
#     # Create user
#     hashed_password = get_password_hash(user_data.password)
    
#     new_user = models.User(
#         email=user_data.email,
#         phone_number=user_data.phone_number,
#         hashed_password=hashed_password,
#         full_name=user_data.full_name,
#         role=user_data.role,
#         district=user_data.district,
#         sector=user_data.sector,
#         village=user_data.village,
#         farm_size=user_data.farm_size,
#         preferred_contact=user_data.preferred_contact.value,
#         receive_notifications=user_data.receive_notifications,
#         is_verified=False  # Require verification
#     )
    
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
    
#     # Send welcome notification
#     try:
#         if user_data.preferred_contact == schemas.ContactMethod.SMS and user_data.phone_number:
#             await notification_service.send_sms(
#                 user_data.phone_number,
#                 f"Welcome to SoSens, {user_data.full_name}! Your account is ready. Login to start monitoring your soil.",
#                 db,
#                 new_user.id
#             )
#         elif user_data.preferred_contact == schemas.ContactMethod.EMAIL and user_data.email:
#             await notification_service.send_email(
#                 user_data.email,
#                 "Welcome to SoSens",
#                 f"<h2>Welcome {user_data.full_name}!</h2><p>Your SoSens account has been created successfully. Start monitoring your soil quality today!</p>",
#                 db,
#                 new_user.id
#             )
#     except Exception as e:
#         print(f" Welcome notification failed: {e}")
    
#     # Create access token
#     access_token = create_access_token(data={"sub": new_user.id})
    
#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "user": new_user
#     }

# @app.post("/api/auth/login", response_model=schemas.Token, tags=["Authentication"])
# async def login(
#     form_data: OAuth2PasswordRequestForm = Depends(), 
#     db: Session = Depends(get_db)
# ):
#     """
#     Login with email or phone number
    
#     - **username**: Email or phone number
#     - **password**: User password
#     """
    
#     user = authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email/phone or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     if not user.is_active:
#         raise HTTPException(status_code=403, detail="Account is deactivated")
    
#     # Update last login
#     user.last_login = datetime.utcnow()
#     db.commit()
    
#     # Create access token
#     access_token = create_access_token(data={"sub": user.id})
    
#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "user": user
#     }

# @app.get("/api/auth/me", response_model=schemas.UserResponse, tags=["Authentication"])
# async def get_current_user_info(current_user: models.User = Depends(get_current_user)):
#     """Get current authenticated user information"""
#     return current_user

# @app.post("/api/auth/forgot-password", tags=["Authentication"])
# async def forgot_password(data: schemas.PasswordReset, db: Session = Depends(get_db)):
#     """
#     Request password reset
    
#     Send reset token via email or SMS
#     """
    
#     # Find user
#     user = db.query(models.User).filter(
#         (models.User.email == data.username) | (models.User.phone_number == data.username)
#     ).first()
    
#     if not user:
#         # Don't reveal if user exists (security best practice)
#         return {"message": "If account exists, reset instructions have been sent"}
    
#     # Generate reset token
#     reset_token = create_reset_token()
#     user.reset_token = reset_token
#     user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
#     db.commit()
    
#     try:
#         # Send reset link
#         if user.email:
#             reset_link = f"https://sosens.rw/reset-password?token={reset_token}"
#             await notification_service.send_email(
#                 user.email,
#                 "Password Reset Request - SoSens",
#                 f"<h3>Password Reset Request</h3><p>Click the link below to reset your password:</p><p><a href='{reset_link}'>Reset Password</a></p><p>This link expires in 1 hour.</p><p>If you didn't request this, please ignore this email.</p>",
#                 db,
#                 user.id
#             )
#         elif user.phone_number:
#             await notification_service.send_sms(
#                 user.phone_number,
#                 f"SoSens password reset code: {reset_token[:8]}. Valid for 1 hour. Don't share this code.",
#                 db,
#                 user.id
#             )
#     except Exception as e:
#         print(f" Reset notification failed: {e}")
    
#     return {"message": "If account exists, reset instructions have been sent"}

# @app.post("/api/auth/reset-password", tags=["Authentication"])
# async def reset_password(data: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
#     """
#     Reset password with token
    
#     Use token from forgot-password email/SMS
#     """
    
#     user = db.query(models.User).filter(models.User.reset_token == data.token).first()
    
#     if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
#         raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
#     # Update password
#     user.hashed_password = get_password_hash(data.new_password)
#     user.reset_token = None
#     user.reset_token_expires = None
#     db.commit()
    
#     return {"message": "Password reset successful. You can now login with your new password."}

# # ============================================================================
# # SOIL READING ENDPOINTS
# # ============================================================================

# @app.post("/api/soil-readings", tags=["Soil Monitoring"])
# async def create_soil_reading(
#     reading: schemas.SoilReadingCreate,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     Submit soil reading
    
#     Record soil parameters for analysis
#     """
    
#     new_reading = models.SoilReading(
#         user_id=current_user.id,
#         **reading.dict()
#     )
    
#     db.add(new_reading)
#     db.commit()
#     db.refresh(new_reading)
    
#     return {
#         "success": True,
#         "message": "Soil reading saved successfully",
#         "reading_id": new_reading.id,
#         "recorded_at": new_reading.reading_date.isoformat()
#     }

# @app.get("/api/soil-readings", tags=["Soil Monitoring"])
# async def get_soil_readings(
#     limit: int = 50,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     Get user's soil reading history
    
#     Returns most recent readings
#     """
    
#     readings = db.query(models.SoilReading).filter(
#         models.SoilReading.user_id == current_user.id
#     ).order_by(models.SoilReading.reading_date.desc()).limit(limit).all()
    
#     return {
#         "success": True,
#         "total": len(readings),
#         "readings": [
#             {
#                 "id": r.id,
#                 "ph": r.ph,
#                 "nitrogen": r.nitrogen,
#                 "phosphorus": r.phosphorus,
#                 "potassium": r.potassium,
#                 "date": r.reading_date.isoformat()
#             }
#             for r in readings
#         ]
#     }

# # ============================================================================
# # PREDICTION ENDPOINT (CORE FEATURE)
# # ============================================================================

# @app.post("/api/predict", response_model=schemas.PredictionResponse, tags=["Predictions"])
# async def get_crop_recommendation(
#     request: schemas.PredictionRequest,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     Get crop recommendation based on soil analysis
    
#     **Integrated with:**
#     - ML prediction model
#     - Weather data
#     - Soil health assessment
#     - Fertilizer recommendations
#     """
    
#     if not ml_service:
#         raise HTTPException(
#             status_code=503, 
#             detail="ML service unavailable. Please contact support."
#         )
    
#     # Prepare soil data
#     soil_data = {
#         'Ph': request.ph,
#         'N': request.nitrogen,
#         'P': request.phosphorus,
#         'K': request.potassium,
#         'Zn': request.zinc or 5.0,
#         'S': request.sulfur or 15.0
#     }
    
#     # Get prediction
#     try:
#         result = ml_service.predict(soil_data)
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, 
#             detail=f"Prediction failed: {str(e)}"
#         )
    
#     if not result.get('success'):
#         raise HTTPException(status_code=400, detail=result.get('error', 'Prediction failed'))
    
#     # Get weather if requested
#     weather_advice = None
#     if request.include_weather and current_user.district:
#         try:
#             weather = weather_service.get_weather(current_user.district, db)
#             if weather:
#                 weather_advice = weather.get('advice')
#         except Exception as e:
#             print(f" Weather fetch failed: {e}")
#             weather_advice = "Weather data temporarily unavailable"
    
#     # Save reading
#     reading = models.SoilReading(
#         user_id=current_user.id,
#         ph=request.ph,
#         nitrogen=request.nitrogen,
#         phosphorus=request.phosphorus,
#         potassium=request.potassium,
#         zinc=request.zinc,
#         sulfur=request.sulfur
#     )
#     db.add(reading)
#     db.flush()
    
#     # Save recommendation
#     recommendation = models.Recommendation(
#         user_id=current_user.id,
#         soil_reading_id=reading.id,
#         recommended_crop=result['prediction']['crop'],
#         confidence_score=result['prediction']['confidence'],
#         alternative_crops=result.get('alternatives', []),
#         soil_health_status=result['soil_health']['status'],
#         soil_issues=result['soil_health'].get('issues', []),
#         fertilizer_recommendation=result['recommendations']['fertilizer'],
#         planting_season=result['recommendations']['planting_season'],
#         weather_advice=weather_advice
#     )
#     db.add(recommendation)
#     db.commit()
#     db.refresh(recommendation)
    
#     # Send notification
#     try:
#         message = f"""🌾 SoSens Soil Analysis

# Recommended Crop: {result['prediction']['crop']}
# Confidence: {result['prediction']['confidence_percent']}
# Soil Health: {result['soil_health']['status']}

# Fertilizer: {result['recommendations']['fertilizer']}
# Planting Season: {result['recommendations']['planting_season']}

# {weather_advice or 'Check weather for latest updates.'}

# - SoSens Team"""
        
#         if current_user.preferred_contact == 'sms' and current_user.phone_number:
#             await notification_service.send_sms(current_user.phone_number, message, db, current_user.id)
#         elif current_user.preferred_contact == 'email' and current_user.email:
#             await notification_service.send_email(
#                 current_user.email,
#                 "Your Crop Recommendation - SoSens",
#                 message.replace('\n', '<br>'),
#                 db,
#                 current_user.id
#             )
#     except Exception as e:
#         print(f" Notification failed: {e}")
    
#     return {
#         "success": True,
#         "crop": result['prediction']['crop'],
#         "confidence": result['prediction']['confidence'],
#         "soil_health": result['soil_health']['status'],
#         "fertilizer_advice": result['recommendations']['fertilizer'],
#         "planting_season": result['recommendations']['planting_season'],
#         "weather_advice": weather_advice,
#         "alternatives": result.get('alternatives', [])
#     }

# # ============================================================================
# # WEATHER ENDPOINT
# # ============================================================================

# @app.get("/api/weather", response_model=schemas.WeatherResponse, tags=["Weather"])
# async def get_weather(
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     Get current weather and farming advice for user's district
    
#     **Provides:**
#     - Temperature & humidity
#     - Rainfall forecast
#     - Farming advice based on conditions
#     """
    
#     if not current_user.district:
#         raise HTTPException(
#             status_code=400, 
#             detail="Please set your district in profile to get weather data"
#         )
    
#     try:
#         weather = weather_service.get_weather(current_user.district, db)
#     except Exception as e:
#         raise HTTPException(
#             status_code=503, 
#             detail=f"Weather service unavailable: {str(e)}"
#         )
    
#     if not weather:
#         raise HTTPException(status_code=503, detail="Weather data unavailable")
    
#     return weather

# # ============================================================================
# # RECOMMENDATION HISTORY
# # ============================================================================

# @app.get("/api/recommendations", tags=["Recommendations"])
# async def get_recommendations(
#     limit: int = 20,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     Get user's crop recommendation history
    
#     Returns past recommendations with timestamps
#     """
    
#     recommendations = db.query(models.Recommendation).filter(
#         models.Recommendation.user_id == current_user.id
#     ).order_by(models.Recommendation.created_at.desc()).limit(limit).all()
    
#     return {
#         "success": True,
#         "total": len(recommendations),
#         "recommendations": [
#             {
#                 "id": r.id,
#                 "crop": r.recommended_crop,
#                 "confidence": r.confidence_score,
#                 "soil_health": r.soil_health_status,
#                 "fertilizer": r.fertilizer_recommendation,
#                 "date": r.created_at.isoformat()
#             }
#             for r in recommendations
#         ]
#     }

# # ============================================================================
# # USER PREFERENCES
# # ============================================================================

# @app.put("/api/preferences", tags=["User Settings"])
# async def update_preferences(
#     preferences: schemas.NotificationPreferences,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     Update notification preferences
    
#     Choose how you want to receive updates (SMS or Email)
#     """
    
#     current_user.receive_notifications = preferences.receive_notifications
#     current_user.preferred_contact = preferences.preferred_contact.value
    
#     db.commit()
    
#     return {
#         "success": True,
#         "message": "Preferences updated successfully",
#         "preferences": {
#             "receive_notifications": current_user.receive_notifications,
#             "preferred_contact": current_user.preferred_contact
#         }
#     }

# # ============================================================================
# # ADMIN ENDPOINTS
# # ============================================================================

# @app.get("/api/admin/users", tags=["Admin"])
# async def get_all_users(
#     skip: int = 0,
#     limit: int = 50,
#     role: Optional[str] = None,
#     district: Optional[str] = None,
#     current_user: models.User = Depends(get_current_admin),
#     db: Session = Depends(get_db)
# ):
#     """
#     Admin: Get all users with filtering
    
#     **Requires:** Admin role
#     """
    
#     query = db.query(models.User)
    
#     if role:
#         query = query.filter(models.User.role == role)
#     if district:
#         query = query.filter(models.User.district == district)
    
#     users = query.offset(skip).limit(limit).all()
#     total = query.count()
    
#     return {
#         "success": True,
#         "total": total,
#         "page": (skip // limit) + 1,
#         "users": [
#             {
#                 "id": u.id,
#                 "name": u.full_name,
#                 "email": u.email,
#                 "phone": u.phone_number,
#                 "role": u.role,
#                 "district": u.district,
#                 "is_active": u.is_active,
#                 "registered": u.created_at.isoformat() if u.created_at else None
#             }
#             for u in users
#         ]
#     }

# @app.get("/api/admin/analytics", tags=["Admin"])
# async def get_analytics(
#     current_user: models.User = Depends(get_current_admin),
#     db: Session = Depends(get_db)
# ):
#     """
#     Admin: System analytics and statistics
    
#     **Requires:** Admin role
#     """
    
#     from sqlalchemy import func
    
#     total_users = db.query(func.count(models.User.id)).scalar() or 0
#     active_users = db.query(func.count(models.User.id)).filter(models.User.is_active == True).scalar() or 0
#     total_readings = db.query(func.count(models.SoilReading.id)).scalar() or 0
#     total_recommendations = db.query(func.count(models.Recommendation.id)).scalar() or 0
    
#     # Farmers only
#     farmers_count = db.query(func.count(models.User.id)).filter(
#         models.User.role == models.UserRole.FARMER
#     ).scalar() or 0
    
#     # Top crops
#     top_crops = db.query(
#         models.Recommendation.recommended_crop,
#         func.count(models.Recommendation.id).label('count')
#     ).group_by(models.Recommendation.recommended_crop).order_by(
#         func.count(models.Recommendation.id).desc()
#     ).limit(5).all()
    
#     # Users by district
#     users_by_district = db.query(
#         models.User.district,
#         func.count(models.User.id).label('count')
#     ).filter(models.User.district != None).group_by(models.User.district).all()
    
#     # Soil health distribution
#     soil_health = db.query(
#         models.Recommendation.soil_health_status,
#         func.count(models.Recommendation.id).label('count')
#     ).filter(models.Recommendation.soil_health_status != None).group_by(
#         models.Recommendation.soil_health_status
#     ).all()
    
#     return {
#         "success": True,
#         "summary": {
#             "total_users": total_users,
#             "active_users": active_users,
#             "farmers": farmers_count,
#             "total_readings": total_readings,
#             "total_recommendations": total_recommendations
#         },
#         "top_crops": [{"crop": c[0], "count": c[1]} for c in top_crops],
#         "users_by_district": [{"district": d[0] or "Unknown", "count": d[1]} for d in users_by_district],
#         "soil_health": [{"status": s[0], "count": s[1]} for s in soil_health]
#     }

# @app.post("/api/admin/send-notification", tags=["Admin"])
# async def send_bulk_notification(
#     message: str = Body(..., embed=True),
#     district: Optional[str] = Body(None, embed=True),
#     current_user: models.User = Depends(get_current_admin),
#     db: Session = Depends(get_db)
# ):
#     """
#     Admin: Send bulk notification to farmers
    
#     **Requires:** Admin role
#     - Send to all farmers or filter by district
#     """
    
#     query = db.query(models.User).filter(
#         models.User.role == models.UserRole.FARMER,
#         models.User.is_active == True,
#         models.User.receive_notifications == True
#     )
    
#     if district:
#         query = query.filter(models.User.district == district)
    
#     users = query.all()
    
#     sent_count = 0
#     failed_count = 0
    
#     for user in users:
#         try:
#             if user.preferred_contact == 'sms' and user.phone_number:
#                 success = await notification_service.send_sms(user.phone_number, message, db, user.id)
#                 if success:
#                     sent_count += 1
#                 else:
#                     failed_count += 1
#             elif user.preferred_contact == 'email' and user.email:
#                 success = await notification_service.send_email(
#                     user.email,
#                     "Important Update from SoSens",
#                     f"<p>{message}</p>",
#                     db,
#                     user.id
#                 )
#                 if success:
#                     sent_count += 1
#                 else:
#                     failed_count += 1
#         except Exception as e:
#             print(f"⚠ Failed to send to user {user.id}: {e}")
#             failed_count += 1
    
#     return {
#         "success": True,
#         "message": f"Notification sent to {sent_count} users",
#         "total_users": len(users),
#         "sent": sent_count,
#         "failed": failed_count
#     }

# # ============================================================================
# # CROPS INFO
# # ============================================================================

# @app.get("/api/crops", tags=["Crops"])
# async def list_crops():
#     """
#     List all supported crops
    
#     Returns crops that can be grown in Rwanda
#     """
    
#     if not ml_service:
#         raise HTTPException(status_code=503, detail="ML service unavailable")
    
#     try:
#         crops = ml_service.list_supported_crops()
#         return {
#             "success": True,
#             "total": len(crops),
#             "crops": crops
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to load crops: {str(e)}")

# @app.get("/api/crops/{crop_name}", tags=["Crops"])
# async def get_crop_details(crop_name: str):
#     """
#     Get detailed information about a specific crop
    
#     **Includes:**
#     - pH requirements
#     - Fertilizer needs
#     - Planting season
#     - Spacing guidelines
#     - Common pests
#     """
    
#     if not ml_service:
#         raise HTTPException(status_code=503, detail="ML service unavailable")
    
#     try:
#         result = ml_service.get_crop_info(crop_name)
        
#         if not result.get('success'):
#             raise HTTPException(status_code=404, detail=f"Crop '{crop_name}' not found")
        
#         return result
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to get crop info: {str(e)}")

# # ============================================================================
# # RUN APPLICATION
# # ============================================================================

# if __name__ == "__main__":
#     import uvicorn
    
#     port = int(os.getenv('API_PORT', 5000))
#     host = os.getenv('API_HOST', '0.0.0.0')
    
#     print(f"\n Starting SoSens API on {host}:{port}")
    
#     uvicorn.run(
#         "app:app",
#         host=host,
#         port=port,
#         reload=True,
#         log_level="info"
#     )