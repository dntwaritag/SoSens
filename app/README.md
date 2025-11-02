# Rwanda Soil Quality Monitoring System - Backend

## Overview
Backend API for the Rwanda Soil Quality Monitoring and Decision Support System for Climate-Smart Agriculture. This system provides ML-powered crop recommendations based on soil analysis.

## Features
- Farmer registration and management
- Soil reading collection and storage
- ML-powered crop recommendations
- SMS integration (Twilio)
- Real-time soil health assessment
- Fertilizer recommendations
- Analytics dashboard
- Feedback collection system

## Tech Stack
- **Framework**: Flask (Python)
- **Database**: PostgreSQL / SQLite
- **ML**: scikit-learn, pandas, numpy
- **SMS**: Twilio API
- **ORM**: SQLAlchemy

## Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd rwanda-soil-backend
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file:
```bash
cp .env.example .env
# Edit .env with your configurations
```

### 5. Initialize database
```bash
python init_db.py
```

### 6. Place ML models
Ensure these files are in the `models/` directory:
- rwanda_soil_model_random_forest.pkl
- feature_scaler.pkl
- label_encoder.pkl
- feature_names.pkl
- model_metadata.json

## Running the Application

### Development
```bash
python app.py
```

### Production
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

### Farmers
- `POST /api/farmers` - Register new farmer
- `GET /api/farmers` - List all farmers
- `GET /api/farmers/<id>` - Get farmer details
- `PUT /api/farmers/<id>` - Update farmer
- `DELETE /api/farmers/<id>` - Delete farmer

### Soil Readings
- `POST /api/soil-readings` - Submit soil reading
- `GET /api/soil-readings` - List soil readings
- `GET /api/soil-readings?farmer_id=<id>` - Get farmer's readings

### Predictions
- `POST /api/predict` - Get crop recommendation

### Feedback
- `POST /api/feedback` - Submit feedback
- `GET /api/feedback` - List feedback

### SMS
- `POST /api/sms/webhook` - Twilio webhook endpoint

### Analytics
- `GET /api/analytics/dashboard` - Dashboard statistics
- `GET /api/analytics/soil-trends` - Soil parameter trends

### Crops
- `GET /api/crops` - List supported crops
- `GET /api/crops/<name>` - Get crop details

## SMS Usage

Farmers can interact via SMS:

**Format**: `SOIL [pH] [N] [P] [K]`

**Example**: `SOIL 6.5 40 20 200`

**Response**: Crop recommendation with fertilizer advice

## Testing

Run API tests:
```bash
python test_api.py
```

## Database Schema

### Farmers
- id, name, phone_number, district, sector, cell, village, farm_size

### SoilReadings
- id, farmer_id, ph, nitrogen, phosphorus, potassium, zinc, sulfur, reading_date

### Recommendations
- id, farmer_id, soil_reading_id, recommended_crop, confidence_score, soil_health_status

### Feedback
- id, farmer_id, recommendation_id, action_taken, yield_achieved, satisfaction_rating


## Contact
For questions: d.ntwaritag@alustudent.com