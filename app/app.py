# from fastapi import FastAPI, Depends, HTTPException, status, Request, Query
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from sqlalchemy.orm import Session
# from typing import List, Optional
# import os
# from datetime import datetime

# # Import database and models
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
#     docs_url="/docs",
#     redoc_url="/redoc"
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
#     # You can implement database logging here if needed
    
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
#         "documentation": "/docs",
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

# @app.get("/api/health", tags=["Health"])
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

# @app.post("/api/sms/webhook", tags=["SMS"])
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

# @app.get("/api/analytics/dashboard", response_model=schemas.DashboardResponse, tags=["Analytics"])
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

# @app.get("/api/analytics/soil-trends", tags=["Analytics"])
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
#     print(f" API Documentation: http://localhost:{os.getenv('API_PORT', 5000)}/docs")
#     print(f" ReDoc: http://localhost:{os.getenv('API_PORT', 5000)}/redoc")
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

from fastapi import FastAPI, Depends, HTTPException, status, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime

# Import database and models
# NOTE: These imports (database, models, schemas, services, etc.) are assumed to exist
# in your project structure for the code to run correctly.
from database import get_db, engine
import models
import schemas

# Import services
from ml_service import MLPredictionService
from sms_service import SMSService
from preprocess import clean_phone_number, validate_location

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Rwanda Soil Quality Monitoring API",
    description="Machine Learning-powered soil quality monitoring and crop recommendation system for smallholder farmers in Rwanda",
    version="1.0.0",
    # ----------------------------------------
    # SECURITY UPDATE: DISABLE DEFAULT DOCUMENTATION PAGES IN PRODUCTION
    # Uncomment these lines in a production environment:
    # docs_url=None,    
    # redoc_url=None
    # ----------------------------------------
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# INITIALIZE SERVICES
# ============================================================================

# Initialize ML Service
ml_service = MLPredictionService(
    model_path=os.getenv('MODEL_PATH', 'models/rwanda_soil_model_random_forest.pkl'),
    scaler_path=os.getenv('SCALER_PATH', 'models/feature_scaler.pkl'),
    encoder_path=os.getenv('ENCODER_PATH', 'models/label_encoder.pkl'),
    features_path=os.getenv('FEATURES_PATH', 'models/feature_names.pkl'),
    metadata_path=os.getenv('METADATA_PATH', 'models/model_metadata.json')
)

# Initialize SMS Service
sms_service = None
if os.getenv('TWILIO_ACCOUNT_SID') and os.getenv('TWILIO_AUTH_TOKEN'):
    sms_service = SMSService(
        account_sid=os.getenv('TWILIO_ACCOUNT_SID'),
        auth_token=os.getenv('TWILIO_AUTH_TOKEN'),
        phone_number=os.getenv('TWILIO_PHONE_NUMBER')
    )
    print("✓ SMS Service initialized")
else:
    print("⚠ SMS Service not configured")

# ============================================================================
# MIDDLEWARE FOR LOGGING
# ============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds()
    
    # Log to database (optional)
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# ============================================================================
# ROOT & HEALTH ENDPOINTS
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """API root endpoint with information"""
    return {
        "project": "Rwanda Soil Quality Monitoring System",
        "version": "1.0.0",
        "status": "active",
        "documentation": "/docs" if app.docs_url else "Disabled",
        "endpoints": {
            "health": "/api/health",
            "farmers": "/api/farmers",
            "soil_readings": "/api/soil-readings",
            "predict": "/api/predict",
            "recommendations": "/api/recommendations",
            "feedback": "/api/feedback",
            "crops": "/api/crops",
            "analytics": "/api/analytics/dashboard"
        }
    }

# SECURITY UPDATE: HIDE HEALTH CHECK FROM DOCUMENTATION
@app.get("/api/health", tags=["Health"], include_in_schema=False)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "ml_model": "loaded",
        "sms_service": "active" if sms_service else "inactive",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# FARMER ENDPOINTS
# ============================================================================

@app.post("/api/farmers", response_model=schemas.FarmerResponse, status_code=status.HTTP_201_CREATED, tags=["Farmers"])
async def create_farmer(farmer: schemas.FarmerCreate, db: Session = Depends(get_db)):
    """Register a new farmer"""
    
    # Clean phone number
    phone = clean_phone_number(farmer.phone_number)
    
    # Check if farmer exists
    existing = db.query(models.Farmer).filter(models.Farmer.phone_number == phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Farmer with this phone number already registered"
        )
    
    # Validate location
    if not validate_location(farmer.district):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid district name"
        )
    
    # Create farmer
    db_farmer = models.Farmer(
        name=farmer.name,
        phone_number=phone,
        district=farmer.district,
        sector=farmer.sector,
        cell=farmer.cell,
        village=farmer.village,
        farm_size=farmer.farm_size
    )
    
    db.add(db_farmer)
    db.commit()
    db.refresh(db_farmer)
    
    # Send welcome SMS
    if sms_service:
        sms_service.send_sms(
            phone,
            f"Welcome {farmer.name}! You are registered with Rwanda Soil Monitoring System. Send HELP for instructions."
        )
    
    return db_farmer

@app.get("/api/farmers", response_model=List[schemas.FarmerResponse], tags=["Farmers"])
async def list_farmers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    district: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of farmers with pagination"""
    
    query = db.query(models.Farmer)
    
    if district:
        query = query.filter(models.Farmer.district == district)
    
    farmers = query.offset(skip).limit(limit).all()
    return farmers

@app.get("/api/farmers/{farmer_id}", response_model=schemas.FarmerResponse, tags=["Farmers"])
async def get_farmer(farmer_id: int, db: Session = Depends(get_db)):
    """Get specific farmer details"""
    
    farmer = db.query(models.Farmer).filter(models.Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    return farmer

@app.put("/api/farmers/{farmer_id}", response_model=schemas.FarmerResponse, tags=["Farmers"])
async def update_farmer(farmer_id: int, farmer_update: schemas.FarmerUpdate, db: Session = Depends(get_db)):
    """Update farmer information"""
    
    farmer = db.query(models.Farmer).filter(models.Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    # Update fields
    update_data = farmer_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(farmer, field, value)
    
    db.commit()
    db.refresh(farmer)
    
    return farmer

# NOTE: This DELETE endpoint should likely be restricted with authorization,
# but for documentation simplicity, we'll leave it visible for now.
@app.delete("/api/farmers/{farmer_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Farmers"])
async def delete_farmer(farmer_id: int, db: Session = Depends(get_db)):
    """Delete a farmer"""
    
    farmer = db.query(models.Farmer).filter(models.Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    db.delete(farmer)
    db.commit()
    
    return None

# ============================================================================
# SOIL READING ENDPOINTS
# ============================================================================

@app.post("/api/soil-readings", response_model=schemas.SoilReadingResponse, status_code=status.HTTP_201_CREATED, tags=["Soil Readings"])
async def create_soil_reading(reading: schemas.SoilReadingCreate, db: Session = Depends(get_db)):
    """Submit a new soil reading"""
    
    # Verify farmer exists
    farmer = db.query(models.Farmer).filter(models.Farmer.id == reading.farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    # Create soil reading
    db_reading = models.SoilReading(**reading.dict())
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    
    return db_reading

@app.get("/api/soil-readings", response_model=List[schemas.SoilReadingResponse], tags=["Soil Readings"])
async def list_soil_readings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    farmer_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get list of soil readings"""
    
    query = db.query(models.SoilReading)
    
    if farmer_id:
        query = query.filter(models.SoilReading.farmer_id == farmer_id)
    
    readings = query.order_by(models.SoilReading.reading_date.desc()).offset(skip).limit(limit).all()
    return readings

# ============================================================================
# PREDICTION ENDPOINT
# ============================================================================

@app.post("/api/predict", response_model=schemas.PredictionResponse, tags=["Predictions"])
async def predict_crop(request: schemas.PredictionRequest, db: Session = Depends(get_db)):
    """Generate crop recommendation based on soil data"""
    
    # Verify farmer if provided
    farmer = None
    if request.farmer_id:
        farmer = db.query(models.Farmer).filter(models.Farmer.id == request.farmer_id).first()
        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer not found")
    
    # Prepare soil data
    soil_data = {
        'Ph': request.ph,
        'N': request.nitrogen,
        'P': request.phosphorus,
        'K': request.potassium,
        'Zn': request.zinc,
        'S': request.sulfur
    }
    
    # Make prediction
    result = ml_service.predict(soil_data)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Prediction failed'))
    
    # Save reading and recommendation if farmer provided
    if farmer:
        # Save soil reading
        db_reading = models.SoilReading(
            farmer_id=farmer.id,
            ph=request.ph,
            nitrogen=request.nitrogen,
            phosphorus=request.phosphorus,
            potassium=request.potassium,
            zinc=request.zinc,
            sulfur=request.sulfur,
            reading_source='api'
        )
        db.add(db_reading)
        db.flush()
        
        # Save recommendation
        db_recommendation = models.Recommendation(
            farmer_id=farmer.id,
            soil_reading_id=db_reading.id,
            recommended_crop=result['prediction']['crop'],
            confidence_score=result['prediction']['confidence'],
            alternative_crops=result['alternatives'],
            soil_health_status=result['soil_health']['status'],
            soil_issues=result['soil_health']['issues'],
            fertilizer_recommendation=result['recommendations']['fertilizer'],
            planting_season=result['recommendations']['planting_season'],
            spacing_recommendation=result['recommendations']['spacing'],
            additional_tips='\n'.join(result['recommendations']['tips']),
            delivered_via='api'
        )
        db.add(db_recommendation)
        db.commit()
        db.refresh(db_recommendation)
        
        result['recommendation_id'] = db_recommendation.id
        result['reading_id'] = db_reading.id
        
        # Send SMS if requested
        if request.send_sms and sms_service:
            sms_result = sms_service.send_recommendation(farmer.phone_number, result)
            if sms_result['success']:
                db_recommendation.is_delivered = True
                db_recommendation.delivered_via = 'sms'
                db.commit()
    
    return result

# ============================================================================
# RECOMMENDATION ENDPOINTS
# ============================================================================

@app.get("/api/recommendations", response_model=List[schemas.RecommendationResponse], tags=["Recommendations"])
async def list_recommendations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    farmer_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get list of recommendations"""
    
    query = db.query(models.Recommendation)
    
    if farmer_id:
        query = query.filter(models.Recommendation.farmer_id == farmer_id)
    
    recommendations = query.order_by(models.Recommendation.created_at.desc()).offset(skip).limit(limit).all()
    return recommendations

# ============================================================================
# FEEDBACK ENDPOINTS
# ============================================================================

@app.post("/api/feedback", response_model=schemas.FeedbackResponse, status_code=status.HTTP_201_CREATED, tags=["Feedback"])
async def create_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    """Submit farmer feedback"""
    
    # Verify farmer and recommendation exist
    farmer = db.query(models.Farmer).filter(models.Farmer.id == feedback.farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    recommendation = db.query(models.Recommendation).filter(
        models.Recommendation.id == feedback.recommendation_id
    ).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Create feedback
    db_feedback = models.Feedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    return db_feedback

@app.get("/api/feedback", response_model=List[schemas.FeedbackResponse], tags=["Feedback"])
async def list_feedback(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    farmer_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get list of feedback"""
    
    query = db.query(models.Feedback)
    
    if farmer_id:
        query = query.filter(models.Feedback.farmer_id == farmer_id)
    
    feedback_list = query.order_by(models.Feedback.submitted_at.desc()).offset(skip).limit(limit).all()
    return feedback_list

# ============================================================================
# SMS WEBHOOK ENDPOINT
# ============================================================================

# SECURITY UPDATE: HIDE SMS WEBHOOK FROM DOCUMENTATION
@app.post("/api/sms/webhook", tags=["SMS"], include_in_schema=False)
async def sms_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle incoming SMS from Twilio"""
    
    if not sms_service:
        raise HTTPException(status_code=503, detail="SMS service not configured")
    
    # Get form data from Twilio
    form_data = await request.form()
    from_number = form_data.get('From', '')
    message_body = form_data.get('Body', '')
    
    # Clean phone number
    phone = clean_phone_number(from_number)
    
    # Find farmer
    farmer = db.query(models.Farmer).filter(models.Farmer.phone_number == phone).first()
    
    # Handle HELP command
    if 'HELP' in message_body.upper():
        sms_service.send_help_message(phone)
        return {"status": "help_sent"}
    
    # Parse soil data
    soil_data = sms_service.parse_incoming_sms(message_body)
    
    if not soil_data:
        sms_service.send_sms(
            phone,
            "Invalid format. Send: SOIL [pH] [N] [P] [K]\nExample: SOIL 6.5 40 20 200\nOr send HELP"
        )
        return {"status": "invalid_format"}
    
    # Register farmer if not exists
    if not farmer:
        farmer = models.Farmer(
            name=f"Farmer {phone[-4:]}",
            phone_number=phone,
            district="Unknown"
        )
        db.add(farmer)
        db.commit()
        db.refresh(farmer)
    
    # Make prediction
    result = ml_service.predict(soil_data)
    
    if result['success']:
        # Save soil reading
        db_reading = models.SoilReading(
            farmer_id=farmer.id,
            ph=soil_data['Ph'],
            nitrogen=soil_data['N'],
            phosphorus=soil_data['P'],
            potassium=soil_data['K'],
            # Assuming Zn and S might be optional/defaulted for SMS input
            zinc=soil_data.get('Zn'), 
            sulfur=soil_data.get('S'),
            reading_source='sms'
        )
        db.add(db_reading)
        db.flush()
        
        # Save recommendation
        db_recommendation = models.Recommendation(
            farmer_id=farmer.id,
            soil_reading_id=db_reading.id,
            recommended_crop=result['prediction']['crop'],
            confidence_score=result['prediction']['confidence'],
            alternative_crops=result['alternatives'],
            soil_health_status=result['soil_health']['status'],
            soil_issues=result['soil_health']['issues'],
            fertilizer_recommendation=result['recommendations']['fertilizer'],
            planting_season=result['recommendations']['planting_season'],
            spacing_recommendation=result['recommendations']['spacing'],
            delivered_via='sms',
            is_delivered=False
        )
        db.add(db_recommendation)
        db.commit()
        
        # Send recommendation via SMS
        sms_result = sms_service.send_recommendation(phone, result)
        
        if sms_result['success']:
            db_recommendation.is_delivered = True
            db.commit()
        
        return {"status": "recommendation_sent"}
    else:
        sms_service.send_sms(
            phone,
            f"Error processing your request: {result.get('error', 'Unknown error')}"
        )
        return {"status": "error"}

# ============================================================================
# CROPS ENDPOINTS
# ============================================================================

@app.get("/api/crops", tags=["Crops"])
async def list_crops():
    """List all supported crops"""
    crops = ml_service.list_supported_crops()
    return {
        "success": True,
        "total_crops": len(crops),
        "crops": crops
    }

@app.get("/api/crops/{crop_name}", tags=["Crops"])
async def get_crop_info(crop_name: str):
    """Get detailed information about a specific crop"""
    result = ml_service.get_crop_info(crop_name)
    
    if not result['success']:
        raise HTTPException(status_code=404, detail=f"Crop '{crop_name}' not found")
    
    return result

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

# SECURITY UPDATE: HIDE ANALYTICS DASHBOARD FROM DOCUMENTATION (and ideally secure with Auth)
@app.get("/api/analytics/dashboard", response_model=schemas.DashboardResponse, tags=["Analytics"], include_in_schema=False)
async def analytics_dashboard(db: Session = Depends(get_db)):
    """Get dashboard analytics"""
    
    from sqlalchemy import func
    
    # Total counts
    total_farmers = db.query(func.count(models.Farmer.id)).scalar()
    active_farmers = db.query(func.count(models.Farmer.id)).filter(
        models.Farmer.is_active == True
    ).scalar()
    total_readings = db.query(func.count(models.SoilReading.id)).scalar()
    total_recommendations = db.query(func.count(models.Recommendation.id)).scalar()
    total_feedback = db.query(func.count(models.Feedback.id)).scalar()
    
    # Average satisfaction
    avg_satisfaction = db.query(func.avg(models.Feedback.satisfaction_rating)).scalar() or 0.0
    
    # District distribution
    district_stats = db.query(
        models.Farmer.district,
        func.count(models.Farmer.id)
    ).group_by(models.Farmer.district).all()
    
    # Top crops
    crop_stats = db.query(
        models.Recommendation.recommended_crop,
        func.count(models.Recommendation.id)
    ).group_by(models.Recommendation.recommended_crop).order_by(
        func.count(models.Recommendation.id).desc()
    ).limit(10).all()
    
    # Soil health distribution
    soil_health_stats = db.query(
        models.Recommendation.soil_health_status,
        func.count(models.Recommendation.id)
    ).group_by(models.Recommendation.soil_health_status).all()
    
    return {
        "success": True,
        "summary": {
            "total_farmers": total_farmers,
            "active_farmers": active_farmers,
            "total_soil_readings": total_readings,
            "total_recommendations": total_recommendations,
            "total_feedback": total_feedback,
            "average_satisfaction": round(avg_satisfaction, 2)
        },
        "districts": [
            {"district": d[0], "farmers": d[1]} 
            for d in district_stats
        ],
        "top_crops": [
            {"crop": c[0], "count": c[1]} 
            for c in crop_stats
        ],
        "soil_health": [
            {"status": s[0] or "Unknown", "count": s[1]} 
            for s in soil_health_stats
        ]
    }

# SECURITY UPDATE: HIDE SOIL TRENDS FROM DOCUMENTATION (and ideally secure with Auth)
@app.get("/api/analytics/soil-trends", tags=["Analytics"], include_in_schema=False)
async def soil_trends(
    farmer_id: Optional[int] = None,
    district: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get soil parameter trends over time"""
    
    query = db.query(models.SoilReading)
    
    if farmer_id:
        query = query.filter(models.SoilReading.farmer_id == farmer_id)
    elif district:
        query = query.join(models.Farmer).filter(models.Farmer.district == district)
    
    readings = query.order_by(models.SoilReading.reading_date).all()
    
    return {
        "success": True,
        "data": [
            {
                "date": r.reading_date.isoformat(),
                "ph": r.ph,
                "nitrogen": r.nitrogen,
                "phosphorus": r.phosphorus,
                "potassium": r.potassium
            }
            for r in readings
        ]
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc)
        }
    )

# ============================================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("\n" + "="*80)
    print("RWANDA SOIL QUALITY MONITORING SYSTEM - FASTAPI")
    print("="*80)
    print(f"ML Model: Loaded")
    print(f"SMS Service: {'Active' if sms_service else 'Inactive'}")
    print(f"Database: Connected")
    print("="*80)
    print("\n Server started successfully!")
    print(f" API Documentation: http://localhost:{os.getenv('API_PORT', 5000)}/docs" if app.docs_url else " API Documentation: Disabled")
    print(f" ReDoc: http://localhost:{os.getenv('API_PORT', 5000)}/redoc" if app.redoc_url else " ReDoc: Disabled")
    print("="*80 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("\n" + "="*80)
    print("Shutting down gracefully...")
    print("="*80 + "\n")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('API_PORT', 5000))
    host = os.getenv('API_HOST', '0.0.0.0')
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info"
    )