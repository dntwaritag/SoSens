<img width="1896" height="1023" alt="image" src="https://github.com/user-attachments/assets/dd4943da-0c9f-4377-aa83-2fd22922b25b" /># SoSens - Climate-Smart Agriculture Decision Support System

Climate-smart agriculture decision support system using machine learning to provide crop recommendations for farmers in Rwanda based on soil properties and weather conditions.

## Overview

SoSens is a complete full-stack web application that helps farmers make informed decisions about crop selection, fertilizer application, and planting schedules. The system integrates real-time weather data, automated SMS/email notifications, and a trained machine learning model for accurate crop predictions.

## Features

### Core Features
- Multi-class crop recommendation system (3+ crops)
- Soil nutrient analysis (pH, Nitrogen, Phosphorus, Potassium, Zinc, Sulfur)
- Real-time weather integration with location-based forecasting
- Fertiliser requirement calculation based on soil deficiencies
- Automated daily weather advisories and notifications
- Multi-channel notifications (SMS via Twilio, Email via SendGrid)
- User authentication with role-based access control
- Admin dashboard with system analytics
- Mobile-responsive interface

### Supported Crops
Maize, Beans, Cassava, Potato, Rice, Wheat, Sorghum, Millet, Peas, Banana, Coffee, Tea

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, TypeScript, Tailwind CSS, shadcn/ui |
| **Backend** | FastAPI, SQLAlchemy, PostgreSQL |
| **ML** | Scikit-learn Random Forest, Pandas, NumPy |
| **Auth** | JWT tokens, Bcrypt password hashing |
| **Notifications** | Twilio (SMS), SendGrid (Email) |
| **Weather** | OpenWeather API |
| **Scheduling** | APScheduler |
| **Deployment** | Render, Docker, GitHub |

## Project Structure

```
SoSens/
├── app/                              # Backend (FastAPI)
│   ├── app.py                       # Main application
│   ├── auth.py                      # Authentication logic
│   ├── config.py                    # Configuration
│   ├── database.py                  # Database setup
│   ├── models.py                    # SQLAlchemy models
│   ├── schemas.py                   # Pydantic schemas
│   ├── ml_service.py                # ML predictions
│   ├── weather_service.py           # Weather API
│   ├── notification_service.py      # SMS/Email
│   ├── scheduler.py                 # Daily tasks
│   ├── models/                      # ML artifacts
│   │   ├── rwanda_soil_model_random_forest.pkl
│   │   ├── feature_scaler.pkl
│   │   ├── label_encoder.pkl
│   │   ├── feature_names.pkl
│   │   └── model_metadata.json
│   ├── requirements.txt
│   ├── start.sh
│   └── .env.example
│
├── frontend/                         # Frontend (React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── HomePage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── FarmerDashboard.tsx
│   │   │   ├── AdminDashboard.tsx
│   │   │   ├── PredictPage.tsx
│   │   │   └── Navigation.tsx
│   │   ├── lib/
│   │   │   ├── api.ts              # 19 API endpoints
│   │   │   └── auth.ts
│   │   ├── App.tsx
│   │   └── config.ts
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
│
├── scripts/
│   └── train_model.py               # ML model training
│
├── data/
│   └── Crop_Recommendation_Dataset.csv
│
├── render.yaml                       # Render deployment config
├── docker-compose.yml
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+
- Git

### Backend Setup

```bash
# Clone repository
git clone https://github.com/dntwaritag/SoSens.git
cd SoSens

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd app
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Train model (if needed)
python scripts/train_model.py

# Start backend
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Backend API: http://127.0.0.1:8000/docs

### Frontend Setup

```bash
# In new terminal, from project root
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend: http://localhost:5173

## API Endpoints

### Authentication (5 endpoints)
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/forgot-password` - Password reset request
- `POST /api/auth/reset-password` - Reset password

### Soil & Predictions (5 endpoints)
- `POST /api/soil-readings` - Submit soil reading
- `GET /api/soil-readings` - Get soil history
- `POST /api/predict` - Get crop recommendation
- `GET /api/recommendations` - Get recommendations history
- `GET /api/weather` - Get weather data

### User (1 endpoint)
- `PUT /api/preferences` - Update user preferences

### Admin (7 endpoints)
- `GET /api/admin/users` - List all users
- `GET /api/admin/analytics` - System analytics
- `POST /api/admin/send-weather` - Send weather notifications
- `POST /api/admin/broadcast` - Broadcast message
- `POST /api/admin/send-predictions` - Send crop predictions
- `GET /api/admin/notification-logs` - View logs
- Health check and root endpoints

Full documentation: https://sosens.onrender.com/docs

## Example: Get Crop Prediction

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ph": 6.5,
    "nitrogen": 45,
    "phosphorus": 22,
    "potassium": 210,
    "zinc": 5.5,
    "sulfur": 16.0,
    "include_weather": true
  }'
```

Response:
```json
{
  "success": true,
  "crop": "Maize",
  "confidence": 0.87,
  "soil_health": "Good",
  "fertilizer_advice": "50kg Urea per hectare",
  "planting_season": "Season A (Sep-Dec)",
  "weather_advice": "Suitable conditions for planting",
  "alternatives": [
    {"crop": "Beans", "confidence": 0.75},
    {"crop": "Cassava", "confidence": 0.68}
  ]
}
```

## Environment Variables

### Backend (.env)

```
# Application
APP_NAME=SoSens Rwanda
DEBUG=False
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=postgresql://user:password@localhost/sosens

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Email
SENDGRID_API_KEY=sg_...

# SMS
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1234567890

# Weather
OPENWEATHER_API_KEY=...

# Scheduling
NOTIFICATION_TIME=06:00
TIMEZONE=Africa/Kigali
```

### Frontend
Backend URL configured in `src/config.ts`:
```typescript
export const API_CONFIG = {
  BASE_URL: "https://sosens.onrender.com/api/",
};
```

## Deployment

### Backend Deployment on Render

1. **Create Web Service**
   - Go to https://dashboard.render.com/
   - Click "New +" → "Web Service"
   - Connect GitHub repository

2. **Configure Build**
   - Build Command: `pip install -r app/requirements.txt`
   - Start Command: `bash app/start.sh`

3. **Add Environment Variables**
   - DATABASE_URL (PostgreSQL)
   - SECRET_KEY
   - SENDGRID_API_KEY
   - TWILIO credentials
   - OPENWEATHER_API_KEY

4. **Deploy Database**
   - Create PostgreSQL database (free tier available)
   - Link to service

5. **Deploy**
   - Click "Create Web Service"
   - Wait for build (5-10 minutes)
   - Backend available at: https://sosens-api.onrender.com

### Frontend Deployment on Render

1. **Create Static Site**
   - Go to https://dashboard.vercel/
   - Click "New +" → "Project"
   - Connect GitHub repository

2. **Build Configuration**
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`

3. **Deploy**
   - Click "Create project"
   - Wait for build (2-5 minutes)
   - Frontend available at: [SoSens-Frontend](https://sosens.vercel.app/)

### Alternative: GitHub Pages for Frontend

```bash
# Build production
npm run build

# Deploy to gh-pages
npm run deploy
```


## Machine Learning Model

### Architecture
- **Algorithm**: Random Forest Classifier
- **Input Features**: 6 soil parameters (pH, N, P, K, Zn, S)
- **Output**: Crop recommendation with confidence scores
- **Training**: 80% train, 20% test split
- **Evaluation**: Cross-validation with accuracy, precision, recall

### Model Performance
- Accuracy on test dataset
- Per-crop precision/recall metrics
- Feature importance ranking

### Training

```bash
cd app
python scripts/train_model.py
```

Generates:
- `models/rwanda_soil_model_random_forest.pkl` - Model
- `models/feature_scaler.pkl` - Feature normalizer
- `models/label_encoder.pkl` - Crop encoder
- `models/feature_names.pkl` - Feature names
- `models/model_metadata.json` - Metadata

## User Roles

### Farmer
- Register with phone/email
- Submit soil readings
- Get crop predictions
- View prediction history
- Manage notification preferences
- Receive daily weather updates

### Admin
- User management
- View system analytics
- Send weather notifications
- Broadcast messages
- Process bulk predictions
- Track notification logs

## Testing

### Test Registration
1. Navigate to registration page
2. Enter Full Name, Phone, Email, Password
3. Click Register
4. Should receive confirmation

### Test Login
1. Use registered credentials
2. Click Sign In
3. Should redirect to dashboard

### Test Prediction
1. Login as farmer
2. Go to prediction page
3. Enter soil data
4. Submit and get recommendation

### Test Admin Features
1. Login as admin
2. Access admin dashboard
3. View analytics and user list
4. Test notification sending

### Verify Backend Connection

```javascript
// Browser console
fetch('https://sosens.onrender.com/api/health')
  .then(r => r.json())
  .then(console.log)
```

## Screenshots

### Login Page
![Login] <img width="1891" height="1022" alt="image" src="https://github.com/user-attachments/assets/90077ab3-c67d-49d4-be59-9b28222b0fe3" />

### Dashboard
![Dashboard]<img width="1896" height="1023" alt="image" src="https://github.com/user-attachments/assets/22639f64-130a-435e-aaf4-9abed3af01f2" />

### Soil Analysis Form
![Soil Analysis]<img width="1902" height="1028" alt="image" src="https://github.com/user-attachments/assets/88d862c9-3525-4382-9102-a115c112efa0" />

### Crop Recommendation
![Recommendation]<img width="1895" height="1017" alt="image" src="https://github.com/user-attachments/assets/b3c669b4-e2dd-4c1a-b9d9-5444655cfa57" />

### Weather Widget
![Weather]<img width="1898" height="1021" alt="image" src="https://github.com/user-attachments/assets/6d826efe-cf61-4d6e-9bd5-cbe04773ae89" />

### Admin Panel
![Admin] <img width="1896" height="1016" alt="image" src="https://github.com/user-attachments/assets/2f9ef096-5705-48d1-a0c5-3a323a4701d6" />

## Troubleshooting

### Backend Issues

**Model not loading**: Run `python app/scripts/train_model.py`

**Database connection error**: Verify DATABASE_URL environment variable

**Notifications not sending**: Check SENDGRID_API_KEY and TWILIO credentials

**Cold start on Render**: Free tier sleeps after 15 minutes, takes 30-60 seconds to restart

### Frontend Issues

**Network error**: Check if backend is running and accessible

**Login fails**: Try registering a new account

**CORS error**: Ensure backend CORS is enabled

**Token expired**: Logout and login again

### General

**Port already in use**: Change port: `uvicorn app:app --port 8001`

**Module not found**: Reinstall dependencies: `pip install -r requirements.txt`

**Build fails on Render**: Check logs in dashboard, clear build cache

## Performance

| Operation | Time |
|-----------|------|
| Initial page load | 1-2 seconds |
| Login | 1-3 seconds |
| Prediction | 2-5 seconds |
| Render cold start | 30-60 seconds |

## Browser Support

Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

## Mobile Support

Fully responsive on:
- Desktop (1024px+)
- Tablet (768px-1023px)
- Mobile (320px-767px)

## Security

- JWT token-based authentication
- Bcrypt password hashing
- Token expiration handling
- Role-based access control
- Input validation and sanitization
- XSS prevention
- CORS configuration

## Development Workflow

```bash
# 1. Make changes locally
npm run dev  # frontend
uvicorn app:app --reload  # backend

# 2. Test changes

# 3. Commit and push
git add .
git commit -m "Feature description"
git push origin main

# 4. Render auto-deploys

# 5. Verify deployment
```

## Monitoring

### Check Backend Status
```bash
curl https://sosens.onrender.com/api/health
```

### View Logs
- Render Dashboard → Service → Logs

### Monitor Notifications
- Admin Panel → Notification Logs

## Future Enhancements

- Mobile native app (iOS/Android)
- IoT soil sensor integration
- Crop rotation recommendations
- Market price integration
- Fertilizer cost optimization
- Community knowledge sharing
- Offline capabilities
- Multi-language support

## License

Private project for Rwanda agricultural system

## Video Demonstration

Full project walkthrough: [https://youtu.be/BpB7NFI0thQ](https://youtu.be/BpB7NFI0thQ)

## Support

### Documentation
- Backend: https://sosens.onrender.com/docs
- Frontend: See frontend/README.md
- API: POST /api/health for status

### Quick Debug Tests

**Backend health:**
```javascript
fetch('https://sosens.onrender.com/api/health').then(r => r.json()).then(console.log)
```

**Check authentication:**
```javascript
localStorage.getItem('sosens_auth_token')
```

**Test prediction (must be logged in):**
```javascript
const token = localStorage.getItem('sosens_auth_token');
fetch('https://sosens.onrender.com/api/predict', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    ph: 6.5, nitrogen: 50, phosphorus: 25, potassium: 200, zinc: 5, sulfur: 15
  })
}).then(r => r.json()).then(console.log)
```

## Author

**Denys Ntwaritaganzwa**
- Email: d.ntwaritag@alustudent.com
- GitHub: https://github.com/dntwaritag
- Project Repository: https://github.com/dntwaritag/SoSens

## Deployment Checklist

Before deployment:
- [ ] Update SECRET_KEY in backend
- [ ] Configure all API keys
- [ ] Test registration and login
- [ ] Test crop prediction
- [ ] Verify notifications
- [ ] Test admin features
- [ ] Check mobile responsiveness

After deployment:
- [ ] Verify backend health
- [ ] Test user registration
- [ ] Test prediction endpoint
- [ ] Verify database connection
- [ ] Check notification delivery
- [ ] Monitor error logs

---

**Status**: Production Ready | **Version**: 1.0.0 | **Last Updated**: November 2025


Production Deployment: Backend https://sosens.onrender.com | Frontend https://sosens.vercel.app/
