from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime
import os

# Import configurations and models
from config import config
from models import db, Farmer, SoilReading, Recommendation, Feedback, SystemLog
from ml_service import MLPredictionService
from sms_service import SMSService
from preprocess import clean_phone_number, validate_location

# Initialize Flask app
def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    migrate = Migrate(app, db)
    
    # Initialize ML Service
    ml_service = MLPredictionService(
        model_path=app.config['MODEL_PATH'],
        scaler_path=app.config['SCALER_PATH'],
        encoder_path=app.config['ENCODER_PATH'],
        features_path=app.config['FEATURES_PATH'],
        metadata_path=app.config['METADATA_PATH']
    )
    
    # Initialize SMS Service (if credentials available)
    sms_service = None
    if app.config['TWILIO_ACCOUNT_SID'] and app.config['TWILIO_AUTH_TOKEN']:
        sms_service = SMSService(
            account_sid=app.config['TWILIO_ACCOUNT_SID'],
            auth_token=app.config['TWILIO_AUTH_TOKEN'],
            phone_number=app.config['TWILIO_PHONE_NUMBER']
        )
        print("✓ SMS Service initialized")
    else:
        print("⚠ SMS Service not configured (Twilio credentials missing)")
    
    # ========================================================================
    # ROUTES - API Endpoints
    # ========================================================================
    
    @app.route('/')
    def index():
        '''API Home Page'''
        return jsonify({
            'project': 'Rwanda Soil Quality Monitoring System',
            'version': '1.0',
            'status': 'active',
            'endpoints': {
                'health': '/api/health',
                'farmers': '/api/farmers',
                'soil_readings': '/api/soil-readings',
                'predict': '/api/predict',
                'recommendations': '/api/recommendations',
                'feedback': '/api/feedback',
                'sms_webhook': '/api/sms/webhook',
                'crops': '/api/crops'
            },
            'documentation': '/api/docs'
        })
    
    @app.route('/api/health')
    def health_check():
        '''Health check endpoint'''
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'ml_model': 'loaded',
            'sms_service': 'active' if sms_service else 'inactive',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # ========================================================================
    # FARMER MANAGEMENT
    # ========================================================================
    
    @app.route('/api/farmers', methods=['GET', 'POST'])
    def manage_farmers():
        '''Get all farmers or register new farmer'''
        
        if request.method == 'GET':
            # Get all farmers with pagination
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            district = request.args.get('district', None)
            
            query = Farmer.query
            if district:
                query = query.filter_by(district=district)
            
            farmers = query.paginate(page=page, per_page=per_page, error_out=False)
            
            return jsonify({
                'success': True,
                'farmers': [f.to_dict() for f in farmers.items],
                'total': farmers.total,
                'page': page,
                'pages': farmers.pages
            })
        
        elif request.method == 'POST':
            # Register new farmer
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'phone_number', 'district']
            missing = [f for f in required_fields if f not in data]
            if missing:
                return jsonify({
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing)}'
                }), 400
            
            # Clean and validate phone number
            phone = clean_phone_number(data['phone_number'])
            
            # Check if farmer already exists
            existing = Farmer.query.filter_by(phone_number=phone).first()
            if existing:
                return jsonify({
                    'success': False,
                    'error': 'Farmer with this phone number already registered'
                }), 409
            
            # Validate location
            if not validate_location(data['district']):
                return jsonify({
                    'success': False,
                    'error': 'Invalid district name'
                }), 400
            
            # Create new farmer
            try:
                farmer = Farmer(
                    name=data['name'],
                    phone_number=phone,
                    district=data['district'],
                    sector=data.get('sector'),
                    cell=data.get('cell'),
                    village=data.get('village'),
                    farm_size=data.get('farm_size')
                )
                
                db.session.add(farmer)
                db.session.commit()
                
                # Send welcome SMS
                if sms_service:
                    sms_service.send_sms(
                        phone,
                        f"Welcome {data['name']}! You are registered with Rwanda Soil Monitoring System. Send HELP for instructions."
                    )
                
                return jsonify({
                    'success': True,
                    'message': 'Farmer registered successfully',
                    'farmer': farmer.to_dict()
                }), 201
                
            except Exception as e:
                db.session.rollback()
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
    
    @app.route('/api/farmers/<int:farmer_id>', methods=['GET', 'PUT', 'DELETE'])
    def farmer_detail(farmer_id):
        '''Get, update, or delete specific farmer'''
        farmer = Farmer.query.get_or_404(farmer_id)
        
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'farmer': farmer.to_dict(),
                'soil_readings_count': farmer.soil_readings.count(),
                'recommendations_count': farmer.recommendations.count()
            })
        
        elif request.method == 'PUT':
            data = request.get_json()
            
            # Update allowed fields
            if 'name' in data:
                farmer.name = data['name']
            if 'district' in data:
                farmer.district = data['district']
            if 'sector' in data:
                farmer.sector = data['sector']
            if 'cell' in data:
                farmer.cell = data['cell']
            if 'village' in data:
                farmer.village = data['village']
            if 'farm_size' in data:
                farmer.farm_size = data['farm_size']
            if 'is_active' in data:
                farmer.is_active = data['is_active']
            
            try:
                db.session.commit()
                return jsonify({
                    'success': True,
                    'message': 'Farmer updated successfully',
                    'farmer': farmer.to_dict()
                })
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'error': str(e)}), 500
        
        elif request.method == 'DELETE':
            try:
                db.session.delete(farmer)
                db.session.commit()
                return jsonify({
                    'success': True,
                    'message': 'Farmer deleted successfully'
                })
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'error': str(e)}), 500
    
    # ========================================================================
    # SOIL READINGS
    # ========================================================================
    
    @app.route('/api/soil-readings', methods=['GET', 'POST'])
    def manage_soil_readings():
        '''Get all soil readings or submit new reading'''
        
        if request.method == 'GET':
            farmer_id = request.args.get('farmer_id', type=int)
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            query = SoilReading.query
            if farmer_id:
                query = query.filter_by(farmer_id=farmer_id)
            
            readings = query.order_by(SoilReading.reading_date.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return jsonify({
                'success': True,
                'readings': [r.to_dict() for r in readings.items],
                'total': readings.total,
                'page': page,
                'pages': readings.pages
            })
        
        elif request.method == 'POST':
            data = request.get_json()
            
            # Validate required fields
            required = ['farmer_id', 'ph', 'nitrogen', 'phosphorus', 'potassium']
            missing = [f for f in required if f not in data]
            if missing:
                return jsonify({
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing)}'
                }), 400
            
            # Verify farmer exists
            farmer = Farmer.query.get(data['farmer_id'])
            if not farmer:
                return jsonify({
                    'success': False,
                    'error': 'Farmer not found'
                }), 404
            
            try:
                reading = SoilReading(
                    farmer_id=data['farmer_id'],
                    ph=data['ph'],
                    nitrogen=data['nitrogen'],
                    phosphorus=data['phosphorus'],
                    potassium=data['potassium'],
                    zinc=data.get('zinc'),
                    sulfur=data.get('sulfur'),
                    environmental_data=data.get('environmental_data'),
                    reading_source=data.get('reading_source', 'manual'),
                    location_lat=data.get('location_lat'),
                    location_lon=data.get('location_lon'),
                    notes=data.get('notes')
                )
                
                db.session.add(reading)
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Soil reading saved successfully',
                    'reading': reading.to_dict()
                }), 201
                
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'error': str(e)}), 500
    
    # ========================================================================
    # PREDICTION & RECOMMENDATIONS
    # ========================================================================
    
    @app.route('/api/predict', methods=['POST'])
    def predict_crop():
        '''Main prediction endpoint - generates crop recommendation'''
        data = request.get_json()
        
        # Check if farmer_id provided
        farmer_id = data.get('farmer_id')
        if farmer_id:
            farmer = Farmer.query.get(farmer_id)
            if not farmer:
                return jsonify({
                    'success': False,
                    'error': 'Farmer not found'
                }), 404
        
        # Prepare soil data for prediction
        soil_data = {
            'Ph': data.get('ph') or data.get('Ph'),
            'N': data.get('nitrogen') or data.get('N'),
            'P': data.get('phosphorus') or data.get('P'),
            'K': data.get('potassium') or data.get('K'),
            'Zn': data.get('zinc') or data.get('Zn'),
            'S': data.get('sulfur') or data.get('S')
        }
        
        # Make prediction
        result = ml_service.predict(soil_data)
        
        if not result['success']:
            return jsonify(result), 400
        
        # Save soil reading if farmer_id provided
        if farmer_id:
            try:
                reading = SoilReading(
                    farmer_id=farmer_id,
                    ph=soil_data['Ph'],
                    nitrogen=soil_data['N'],
                    phosphorus=soil_data['P'],
                    potassium=soil_data['K'],
                    zinc=soil_data.get('Zn'),
                    sulfur=soil_data.get('S'),
                    reading_source='api'
                )
                db.session.add(reading)
                db.session.flush()  # Get reading ID
                
                # Save recommendation
                recommendation = Recommendation(
                    farmer_id=farmer_id,
                    soil_reading_id=reading.id,
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
                db.session.add(recommendation)
                db.session.commit()
                
                result['recommendation_id'] = recommendation.id
                result['reading_id'] = reading.id
                
                # Send SMS if service available
                if sms_service and data.get('send_sms', False):
                    sms_result = sms_service.send_recommendation(
                        farmer.phone_number,
                        result
                    )
                    if sms_result['success']:
                        recommendation.is_delivered = True
                        recommendation.delivered_via = 'sms'
                        db.session.commit()
                
            except Exception as e:
                db.session.rollback()
                result['warning'] = f'Prediction successful but failed to save: {str(e)}'
        
        return jsonify(result)
    
    @app.route('/api/recommendations', methods=['GET'])
    def get_recommendations():
        '''Get recommendations history'''
        farmer_id = request.args.get('farmer_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = Recommendation.query
        if farmer_id:
            query = query.filter_by(farmer_id=farmer_id)
        
        recommendations = query.order_by(Recommendation.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'recommendations': [r.to_dict() for r in recommendations.items],
            'total': recommendations.total,
            'page': page,
            'pages': recommendations.pages
        })
    
    # ========================================================================
    # FEEDBACK
    # ========================================================================
    
    @app.route('/api/feedback', methods=['GET', 'POST'])
    def manage_feedback():
        '''Submit or retrieve feedback'''
        
        if request.method == 'GET':
            farmer_id = request.args.get('farmer_id', type=int)
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            query = Feedback.query
            if farmer_id:
                query = query.filter_by(farmer_id=farmer_id)
            
            feedback_list = query.order_by(Feedback.submitted_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return jsonify({
                'success': True,
                'feedback': [f.to_dict() for f in feedback_list.items],
                'total': feedback_list.total,
                'page': page,
                'pages': feedback_list.pages
            })
        
        elif request.method == 'POST':
            data = request.get_json()
            
            required = ['farmer_id', 'recommendation_id']
            missing = [f for f in required if f not in data]
            if missing:
                return jsonify({
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing)}'
                }), 400
            
            try:
                feedback = Feedback(
                    farmer_id=data['farmer_id'],
                    recommendation_id=data['recommendation_id'],
                    action_taken=data.get('action_taken'),
                    crop_planted=data.get('crop_planted'),
                    yield_achieved=data.get('yield_achieved'),
                    satisfaction_rating=data.get('satisfaction_rating'),
                    comments=data.get('comments'),
                    harvest_date=data.get('harvest_date')
                )
                
                db.session.add(feedback)
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Feedback submitted successfully',
                    'feedback': feedback.to_dict()
                }), 201
                
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'error': str(e)}), 500
    
    # ========================================================================
    # SMS WEBHOOK
    # ========================================================================
    
    @app.route('/api/sms/webhook', methods=['POST'])
    def sms_webhook():
        '''Handle incoming SMS from farmers (Twilio webhook)'''
        
        if not sms_service:
            return jsonify({'error': 'SMS service not configured'}), 503
        
        # Get Twilio request data
        from_number = request.values.get('From', '')
        message_body = request.values.get('Body', '')
        
        # Clean phone number
        phone = clean_phone_number(from_number)
        
        # Find farmer
        farmer = Farmer.query.filter_by(phone_number=phone).first()
        
        # Handle HELP command
        if 'HELP' in message_body.upper():
            sms_service.send_help_message(phone)
            return '', 200
        
        # Parse soil data from SMS
        soil_data = sms_service.parse_incoming_sms(message_body)
        
        if not soil_data:
            # Invalid format
            sms_service.send_sms(
                phone,
                "Invalid format. Send: SOIL [pH] [N] [P] [K]\nExample: SOIL 6.5 40 20 200\nOr send HELP"
            )
            return '', 200
        
        # If farmer not registered, register them
        if not farmer:
            farmer = Farmer(
                name=f"Farmer {phone[-4:]}",  # Temporary name
                phone_number=phone,
                district="Unknown"  # To be updated later
            )
            db.session.add(farmer)
            db.session.commit()
        
        # Make prediction
        result = ml_service.predict(soil_data)
        
        if result['success']:
            # Save soil reading and recommendation
            try:
                reading = SoilReading(
                    farmer_id=farmer.id,
                    ph=soil_data['Ph'],
                    nitrogen=soil_data['N'],
                    phosphorus=soil_data['P'],
                    potassium=soil_data['K'],
                    reading_source='sms'
                )
                db.session.add(reading)
                db.session.flush()
                
                recommendation = Recommendation(
                    farmer_id=farmer.id,
                    soil_reading_id=reading.id,
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
                db.session.add(recommendation)
                db.session.commit()
                
                # Send recommendation via SMS
                sms_result = sms_service.send_recommendation(phone, result)
                
                if sms_result['success']:
                    recommendation.is_delivered = True
                    db.session.commit()
                
            except Exception as e:
                db.session.rollback()
                print(f"Error saving SMS data: {e}")
        else:
            # Send error message
            sms_service.send_sms(
                phone,
                f"Error processing your request: {result.get('error', 'Unknown error')}"
            )
        
        return '', 200
    
    # ========================================================================
    # CROPS INFO
    # ========================================================================
    
    @app.route('/api/crops', methods=['GET'])
    def list_crops():
        '''List all supported crops'''
        return jsonify({
            'success': True,
            'total_crops': len(ml_service.list_supported_crops()),
            'crops': ml_service.list_supported_crops()
        })
    
    @app.route('/api/crops/<crop_name>', methods=['GET'])
    def crop_info(crop_name):
        '''Get detailed information about a specific crop'''
        result = ml_service.get_crop_info(crop_name)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
    
    # ========================================================================
    # ANALYTICS & STATISTICS
    # ========================================================================
    
    @app.route('/api/analytics/dashboard', methods=['GET'])
    def analytics_dashboard():
        '''Get dashboard analytics'''
        
        # Total counts
        total_farmers = Farmer.query.count()
        active_farmers = Farmer.query.filter_by(is_active=True).count()
        total_readings = SoilReading.query.count()
        total_recommendations = Recommendation.query.count()
        total_feedback = Feedback.query.count()
        
        # District distribution
        district_stats = db.session.query(
            Farmer.district,
            db.func.count(Farmer.id)
        ).group_by(Farmer.district).all()
        
        # Most recommended crops
        crop_stats = db.session.query(
            Recommendation.recommended_crop,
            db.func.count(Recommendation.id)
        ).group_by(Recommendation.recommended_crop).order_by(
            db.func.count(Recommendation.id).desc()
        ).limit(10).all()
        
        # Soil health distribution
        soil_health_stats = db.session.query(
            Recommendation.soil_health_status,
            db.func.count(Recommendation.id)
        ).group_by(Recommendation.soil_health_status).all()
        
        # Average satisfaction rating
        avg_satisfaction = db.session.query(
            db.func.avg(Feedback.satisfaction_rating)
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'summary': {
                'total_farmers': total_farmers,
                'active_farmers': active_farmers,
                'total_soil_readings': total_readings,
                'total_recommendations': total_recommendations,
                'total_feedback': total_feedback,
                'average_satisfaction': round(avg_satisfaction, 2)
            },
            'districts': [
                {'district': d[0], 'farmers': d[1]} 
                for d in district_stats
            ],
            'top_crops': [
                {'crop': c[0], 'count': c[1]} 
                for c in crop_stats
            ],
            'soil_health': [
                {'status': s[0], 'count': s[1]} 
                for s in soil_health_stats
            ]
        })
    
    @app.route('/api/analytics/soil-trends', methods=['GET'])
    def soil_trends():
        '''Get soil parameter trends over time'''
        farmer_id = request.args.get('farmer_id', type=int)
        district = request.args.get('district')
        
        query = SoilReading.query
        if farmer_id:
            query = query.filter_by(farmer_id=farmer_id)
        elif district:
            query = query.join(Farmer).filter(Farmer.district == district)
        
        readings = query.order_by(SoilReading.reading_date).all()
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'date': r.reading_date.isoformat(),
                    'ph': r.ph,
                    'nitrogen': r.nitrogen,
                    'phosphorus': r.phosphorus,
                    'potassium': r.potassium
                }
                for r in readings
            ]
        })
    
    # ========================================================================
    # ERROR HANDLERS
    # ========================================================================
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 'Bad request'
        }), 400
    
    # ========================================================================
    # LOGGING
    # ========================================================================
    
    @app.after_request
    def log_request(response):
        '''Log all API requests'''
        try:
            log = SystemLog(
                log_type='info' if response.status_code < 400 else 'error',
                endpoint=request.endpoint,
                method=request.method,
                status_code=response.status_code,
                message=f"{request.method} {request.path}",
                ip_address=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()
        except:
            pass  # Don't fail request if logging fails
        
        return response
    
    return app

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Get configuration from environment
    config_name = os.getenv('FLASK_ENV', 'development')
    
    # Create app
    app = create_app(config_name)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✓ Database tables created")
    
    # Print startup information
    print("\n" + "="*80)
    print("RWANDA SOIL QUALITY MONITORING SYSTEM - BACKEND API")
    print("="*80)
    print(f"Environment: {config_name}")
    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"ML Model: Loaded")
    print(f"SMS Service: {'Active' if app.config['TWILIO_ACCOUNT_SID'] else 'Inactive'}")
    print("="*80)
    print("\n Starting server...")
    print(f"API available at: http://{app.config['API_HOST']}:{app.config['API_PORT']}")
    print("\nEndpoints:")
    print("  GET  /                           - API information")
    print("  GET  /api/health                 - Health check")
    print("  POST /api/farmers                - Register farmer")
    print("  POST /api/soil-readings          - Submit soil reading")
    print("  POST /api/predict                - Get crop recommendation")
    print("  POST /api/sms/webhook            - SMS webhook (Twilio)")
    print("  GET  /api/crops                  - List crops")
    print("  GET  /api/analytics/dashboard    - Dashboard analytics")
    print("="*80 + "\n")
    
    # Run the application
    app.run(
        host=app.config['API_HOST'],
        port=app.config['API_PORT'],
        debug=app.config['DEBUG']
    )