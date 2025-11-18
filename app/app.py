"""
Complete FastAPI application with all endpoints including missing preferences endpoint
"""

from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from datetime import timedelta, datetime

from .database import get_db, engine
import models
import schemas
from auth import (
    authenticate_user, create_access_token, get_current_user,
    get_current_admin, get_current_farmer, get_password_hash, create_reset_token
)
from ml_service import ml_service
from weather_service import weather_service
from notification_service import notification_service
from scheduler import start_scheduler, stop_scheduler
from config import settings

# Create tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="SoSens",
    description="Climate-Smart Agriculture Decision Support System",
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

# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    start_scheduler()
    print("="*80)
    print(" SoSens")
    print("="*80)
    print(f" Database: Connected")
    print(f" ML Model: Loaded")
    print(f" Scheduler: Active (Daily at {settings.NOTIFICATION_TIME})")
    print("="*80)

@app.on_event("shutdown")
async def shutdown_event():
    stop_scheduler()

# ============================================================================
# PUBLIC ENDPOINTS
# ============================================================================

@app.get("/", tags=["System"])
async def root():
    return {
        "app": "SoSens",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# AUTHENTICATION ENDPOINTS 
# ============================================================================

@app.post("/api/auth/register", response_model=schemas.Token, status_code=201, tags=["Authentication"])
async def register(user_data: schemas.UserRegister, db: Session = Depends(get_db)):
    """Register new user with welcome notification"""
    
    # Validation
    if not user_data.email and not user_data.phone_number:
        raise HTTPException(400, "Email or phone number required")
    
    # Check existing
    if user_data.email:
        if db.query(models.User).filter(models.User.email == user_data.email).first():
            raise HTTPException(400, "Email already registered")
    
    if user_data.phone_number:
        if db.query(models.User).filter(models.User.phone_number == user_data.phone_number).first():
            raise HTTPException(400, "Phone already registered")
    
    # Create user
    new_user = models.User(
        email=user_data.email,
        phone_number=user_data.phone_number,
        hashed_password=get_password_hash(user_data.password),
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
    try:
        await notification_service.send_welcome_notification(new_user, db)
    except Exception as e:
        print(f"Welcome notification failed: {e}")
    
    # Generate token
    access_token = create_access_token(data={"sub": new_user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }

@app.post("/api/auth/login", response_model=schemas.Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with email or phone"""
    
    print(f"LOGIN ATTEMPT: username={form_data.username}, password={'*' * len(form_data.password)}")

    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        print("FAIL: User not found or password mismatch")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/phone or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        print("FAIL: Account deactivated")
        raise HTTPException(403, "Account deactivated")
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    print("SUCCESS: Login successful")
    
    # Generate token
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@app.post("/api/auth/forgot-password", tags=["Authentication"])
async def forgot_password(data: schemas.PasswordReset, db: Session = Depends(get_db)):
    """Request password reset with notification"""
    
    user = db.query(models.User).filter(
        (models.User.email == data.username) | (models.User.phone_number == data.username)
    ).first()
    
    # Base response
    response_data = {
        "success": True,
        "message": "If account exists, reset instructions sent"
    }

    if not user:
        return response_data
    
    # Generate token
    reset_token = create_reset_token()
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    
    # Send reset notification
    try:
        await notification_service.send_password_reset(user, reset_token, db)
    except Exception as e:
        print(f"Password reset notification failed: {e}")
    
    if settings.DEBUG:
        print(f"DEBUG: Password reset token for {user.email} is {reset_token}")
        response_data["debug_token"] = reset_token
    
    return response_data

@app.post("/api/auth/reset-password", tags=["Authentication"])
async def reset_password(data: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password with token"""
    
    user = db.query(models.User).filter(models.User.reset_token == data.token).first()
    
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        raise HTTPException(400, "Invalid or expired reset token")
    
    user.hashed_password = get_password_hash(data.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return {"success": True, "message": "Password reset successful"}

# ============================================================================
# USER ENDPOINTS
# ============================================================================

@app.get("/api/auth/me", response_model=schemas.UserResponse, tags=["User"])
async def get_me(current_user: models.User = Depends(get_current_user)):
    """Get current user info"""
    return current_user

@app.put("/api/preferences", tags=["User"])
async def update_preferences(
    preferences: dict = Body(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences (contact method, notifications)"""
    
    try:
        # Update preferred contact method
        if "preferred_contact" in preferences:
            if preferences["preferred_contact"] not in ["sms", "email"]:
                raise HTTPException(400, "preferred_contact must be 'sms' or 'email'")
            current_user.preferred_contact = preferences["preferred_contact"]
        
        # Update notification preference
        if "receive_notifications" in preferences:
            current_user.receive_notifications = bool(preferences["receive_notifications"])
        
        # Update farm size if provided
        if "farm_size" in preferences:
            current_user.farm_size = float(preferences["farm_size"])
        
        # Update district if provided
        if "district" in preferences:
            current_user.district = preferences["district"]
        
        # Update sector if provided
        if "sector" in preferences:
            current_user.sector = preferences["sector"]
        
        # Update village if provided
        if "village" in preferences:
            current_user.village = preferences["village"]
        
        db.commit()
        db.refresh(current_user)
        
        return {
            "success": True,
            "message": "Preferences updated successfully",
            "user": {
                "id": current_user.id,
                "preferred_contact": current_user.preferred_contact,
                "receive_notifications": current_user.receive_notifications,
                "farm_size": current_user.farm_size,
                "district": current_user.district,
                "sector": current_user.sector,
                "village": current_user.village
            }
        }
    except Exception as e:
        print(f"Error updating preferences: {e}")
        raise HTTPException(500, f"Failed to update preferences: {str(e)}")

# ============================================================================
# FARMER ENDPOINTS
# ============================================================================

@app.post("/api/soil-readings", tags=["Farmers"])
async def submit_soil_reading(
    reading: schemas.SoilReadingCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Farmer: Submit soil reading"""
    
    # Verify user is farmer or admin
    if current_user.role not in [models.UserRole.FARMER, models.UserRole.ADMIN]:
        raise HTTPException(403, "Only farmers can submit soil readings")
    
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

@app.get("/api/soil-readings", tags=["Farmers"])
async def get_soil_readings(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get own soil readings"""
    
    readings = db.query(models.SoilReading).filter(
        models.SoilReading.user_id == current_user.id
    ).order_by(models.SoilReading.reading_date.desc()).limit(50).all()
    
    return {
        "success": True,
        "total": len(readings),
        "readings": [
            {
                "id": r.id,
                "ph": r.ph,
                "nitrogen": r.nitrogen,
                "phosphorus": r.phosphorus,
                "potassium": r.potassium,
                "date": r.reading_date.isoformat()
            }
            for r in readings
        ]
    }

@app.post("/api/predict", response_model=schemas.PredictionResponse, tags=["Farmers"])
async def get_prediction(
    request: schemas.PredictionRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get crop recommendation with notification"""
    
    # Prepare data
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
    
    if not result.get('success'):
        raise HTTPException(400, result.get('error', 'Prediction failed'))
    
    # Get weather
    weather_advice = None
    if request.include_weather:
        weather = weather_service.get_weather(current_user.district, db)
        weather_advice = weather.get('advice')
    
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
        alternative_crops=result.get('alternatives', []),
        soil_health_status=result['soil_health']['status'],
        soil_issues=result['soil_health'].get('issues', []),
        fertilizer_recommendation=result['recommendations']['fertilizer'],
        planting_season=result['recommendations']['planting_season'],
        weather_advice=weather_advice
    )
    db.add(recommendation)
    db.commit()
    
    # Send prediction notification
    try:
        prediction_data = {
            'crop': result['prediction']['crop'],
            'confidence': result['prediction']['confidence'],
            'soil_health': result['soil_health']['status'],
            'fertilizer_advice': result['recommendations']['fertilizer'],
            'planting_season': result['recommendations']['planting_season']
        }
        await notification_service.send_prediction_notification(
            current_user, prediction_data, weather_advice, db
        )
    except Exception as e:
        print(f"Prediction notification failed: {e}")
    
    return {
        "success": True,
        "crop": result['prediction']['crop'],
        "confidence": result['prediction']['confidence'],
        "soil_health": result['soil_health']['status'],
        "fertilizer_advice": result['recommendations']['fertilizer'],
        "planting_season": result['recommendations']['planting_season'],
        "weather_advice": weather_advice,
        "alternatives": result.get('alternatives', [])
    }

@app.get("/api/recommendations", tags=["Farmers"])
async def get_recommendations(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recommendation history"""
    
    recs = db.query(models.Recommendation).filter(
        models.Recommendation.user_id == current_user.id
    ).order_by(models.Recommendation.created_at.desc()).limit(20).all()
    
    return {
        "success": True,
        "total": len(recs),
        "recommendations": [
            {
                "id": r.id,
                "crop": r.recommended_crop,
                "confidence": r.confidence_score,
                "soil_health": r.soil_health_status,
                "fertilizer": r.fertilizer_recommendation,
                "date": r.created_at.isoformat()
            }
            for r in recs
        ]
    }

@app.get("/api/weather", response_model=schemas.WeatherResponse, tags=["Farmers"])
async def get_weather(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current weather"""
    
    weather = weather_service.get_weather(current_user.district, db)
    if not weather:
        raise HTTPException(503, "Weather service unavailable")
    
    return weather

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.get("/api/admin/users", tags=["Admin"])
async def get_all_users(
    skip: int = 0,
    limit: int = 50,
    role: Optional[str] = None,
    district: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: Get all users"""
    
    # Verify admin role
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(403, "Admin access required")
    
    query = db.query(models.User)
    
    if role:
        query = query.filter(models.User.role == role)
    if district:
        query = query.filter(models.User.district == district)
    
    users = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "success": True,
        "total": total,
        "users": [
            {
                "id": u.id,
                "name": u.full_name,
                "email": u.email,
                "phone": u.phone_number,
                "role": u.role.value,
                "district": u.district,
                "is_active": u.is_active,
                "last_login": u.last_login.isoformat() if u.last_login else None
            }
            for u in users
        ]
    }

@app.get("/api/admin/analytics", tags=["Admin"])
async def get_analytics(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: System analytics"""
    
    # Verify admin role
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(403, "Admin access required")
    
    from sqlalchemy import func
    
    total_users = db.query(func.count(models.User.id)).scalar() or 0
    farmers = db.query(func.count(models.User.id)).filter(
        models.User.role == models.UserRole.FARMER
    ).scalar() or 0
    total_readings = db.query(func.count(models.SoilReading.id)).scalar() or 0
    total_recs = db.query(func.count(models.Recommendation.id)).scalar() or 0
    total_notifications = db.query(func.count(models.NotificationLog.id)).scalar() or 0
    sent_notifications = db.query(func.count(models.NotificationLog.id)).filter(
        models.NotificationLog.is_sent == True
    ).scalar() or 0
    
    # Top crops
    top_crops = db.query(
        models.Recommendation.recommended_crop,
        func.count(models.Recommendation.id)
    ).group_by(models.Recommendation.recommended_crop).order_by(
        func.count(models.Recommendation.id).desc()
    ).limit(5).all()
    
    # By district
    by_district = db.query(
        models.User.district,
        func.count(models.User.id)
    ).filter(models.User.district != None).group_by(
        models.User.district
    ).all()
    
    return {
        "success": True,
        "summary": {
            "total_users": total_users,
            "farmers": farmers,
            "total_readings": total_readings,
            "total_recommendations": total_recs,
            "total_notifications": total_notifications,
            "sent_notifications": sent_notifications
        },
        "top_crops": [{"crop": c[0], "count": c[1]} for c in top_crops],
        "by_district": [{"district": d[0], "count": d[1]} for d in by_district]
    }

@app.post("/api/admin/send-weather", tags=["Admin"])
async def admin_send_weather(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: Manually trigger weather notifications"""
    
    # Verify admin role
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(403, "Admin access required")
    
    result = await notification_service.send_daily_weather(db)
    
    return {
        "success": True,
        "message": f"Weather notifications sent: {result['sent']} successful, {result['failed']} failed",
        "sent": result['sent'],
        "failed": result['failed']
    }

@app.post("/api/admin/broadcast", tags=["Admin"])
async def broadcast_message(
    message: str = Body(..., embed=True),
    district: Optional[str] = Body(None, embed=True),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: Broadcast custom message to farmers"""
    
    # Verify admin role
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(403, "Admin access required")
    
    if not message or len(message.strip()) == 0:
        raise HTTPException(400, "Message cannot be empty")
    
    query = db.query(models.User).filter(
        models.User.role == models.UserRole.FARMER,
        models.User.is_active == True
    )
    
    if district:
        query = query.filter(models.User.district == district)
    
    users = query.all()
    sent = 0
    failed = 0
    
    print(f"📢 Broadcasting message to {len(users)} farmers...")
    
    for user in users:
        try:
            if user.preferred_contact == 'sms' and user.phone_number:
                success = await notification_service.send_sms(user.phone_number, message, db, user.id)
            elif user.preferred_contact == 'email' and user.email:
                success = await notification_service.send_email(
                    user.email,
                    "📢 Important Message from SoSens",
                    message,
                    db,
                    user.id
                )
            else:
                success = False
            
            if success:
                sent += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Broadcast error for user {user.id}: {e}")
            failed += 1
    
    return {
        "success": True,
        "message": f"Broadcast complete: {sent} sent, {failed} failed",
        "total_users": len(users),
        "sent": sent,
        "failed": failed
    }

@app.post("/api/admin/send-predictions", tags=["Admin"])
async def send_bulk_predictions(
    crop: str = Body(..., embed=True),
    district: Optional[str] = Body(None, embed=True),
    message: Optional[str] = Body(None, embed=True),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: Send crop prediction/advice to farmers in a district"""
    
    # Verify admin role
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(403, "Admin access required")
    
    if not crop or len(crop.strip()) == 0:
        raise HTTPException(400, "Crop name cannot be empty")
    
    # Get farmers in district or all farmers
    query = db.query(models.User).filter(
        models.User.role == models.UserRole.FARMER,
        models.User.is_active == True,
        models.User.receive_notifications == True
    )
    
    if district:
        query = query.filter(models.User.district == district)
    
    users = query.all()
    sent = 0
    failed = 0
    
    print(f"📢 Sending {crop} prediction to {len(users)} farmers...")
    
    for user in users:
        try:
            prediction_message = message or f"""
🌾 Recommended Crop: {crop}

Based on current soil and weather conditions in {user.district}, we recommend planting {crop}.

For detailed personalized recommendations, please:
1. Submit your soil reading in the app
2. Get a customized prediction

Thank you for using SoSens!
            """.strip()
            
            if user.preferred_contact == 'sms' and user.phone_number:
                success = await notification_service.send_sms(
                    user.phone_number, 
                    prediction_message, 
                    db, 
                    user.id
                )
            elif user.preferred_contact == 'email' and user.email:
                success = await notification_service.send_email(
                    user.email,
                    f"🌾 Crop Recommendation: {crop}",
                    prediction_message,
                    db,
                    user.id
                )
            else:
                success = False
            
            if success:
                sent += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Prediction send error for user {user.id}: {e}")
            failed += 1
    
    return {
        "success": True,
        "message": f"Crop prediction sent: {sent} successful, {failed} failed",
        "crop": crop,
        "district": district or "All Districts",
        "total_farmers": len(users),
        "sent": sent,
        "failed": failed
    }

@app.get("/api/admin/notification-logs", tags=["Admin"])
async def get_notification_logs(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: View notification logs"""
    
    # Verify admin role
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(403, "Admin access required")
    
    logs = db.query(models.NotificationLog).order_by(
        models.NotificationLog.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    total = db.query(models.NotificationLog).count()
    
    return {
        "success": True,
        "total": total,
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "type": log.notification_type,
                "channel": log.channel,
                "is_sent": log.is_sent,
                "sent_at": log.sent_at.isoformat() if log.sent_at else None,
                "error": log.error_message,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ]
    }

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)