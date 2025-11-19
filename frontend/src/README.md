# Rwanda Crop Recommendation System - Frontend

A modern web application that provides smart crop recommendations to Rwandan farmers based on soil and weather data analysis.

## 🌾 Overview

This React TypeScript application connects to a FastAPI backend hosted on Render to deliver:
- Intelligent crop recommendations based on soil properties
- Weather-integrated predictions
- User authentication and authorization
- Prediction history tracking
- Admin analytics dashboard
- SMS/Email notifications for farmers

## 🔗 Backend Connection

**Production Backend:** https://sosens.onrender.com  
**API Documentation:** https://sosens.onrender.com/docs  
**Health Check:** https://sosens.onrender.com/api/health

The frontend is **100% connected** to the production backend with no mock data or fallback modes.

## 🚀 Features

### Farmer Features
- **User Registration & Login** - Secure authentication with phone/email
- **Password Reset** - Forgot password functionality with token-based reset
- **Crop Predictions** - ML-powered recommendations based on:
  - Soil pH
  - Nitrogen (N)
  - Phosphorus (P)
  - Potassium (K)
  - Zinc (Zn)
  - Sulfur (S)
  - Optional weather data integration
- **Prediction History** - View past recommendations
- **Soil Readings** - Submit and track soil test results
- **Notification Preferences** - Configure alert settings

### Admin Features
- **User Management** - View and manage registered farmers
- **System Analytics** - Dashboard with key metrics
- **Weather Notifications** - Send weather alerts to farmers
- **Broadcast Messages** - Mass communication system
- **Bulk Predictions** - Process multiple predictions
- **Notification Logs** - Track all sent notifications

## 🛠️ Technology Stack

- **Framework:** React 18 with TypeScript
- **Styling:** Tailwind CSS v4.0
- **UI Components:** shadcn/ui
- **Icons:** Lucide React
- **Charts:** Recharts
- **Notifications:** Sonner
- **HTTP Client:** Fetch API
- **Authentication:** JWT tokens

## 📁 Project Structure

```
/
├── components/
│   ├── ui/                    # shadcn/ui components
│   ├── figma/                 # Custom components
│   ├── HomePage.tsx           # Landing page
│   ├── LoginPage.tsx          # Authentication (login + forgot password)
│   ├── RegisterPage.tsx       # User registration
│   ├── DashboardPage.tsx      # Main dashboard router
│   ├── FarmerDashboard.tsx    # Farmer-specific dashboard
│   ├── AdminDashboard.tsx     # Admin-specific dashboard
│   ├── PredictPage.tsx        # Crop prediction form
│   ├── AboutPage.tsx          # About the system
│   └── Navigation.tsx         # Navigation component
├── lib/
│   ├── api.ts                 # API service (19 endpoints)
│   └── auth.ts                # Authentication utilities
├── styles/
│   └── globals.css            # Global styles + Tailwind
├── App.tsx                    # Main application component
└── config.ts                  # Backend configuration
```

## 🔌 API Integration

The application connects to 19 backend endpoints:

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password with token

### Predictions & Soil
- `POST /api/predict` - Get crop recommendation
- `GET /api/recommendations` - Get prediction history
- `GET /api/recommendations/{id}` - Get specific prediction
- `POST /api/soil-readings` - Submit soil reading
- `GET /api/soil-readings` - Get soil reading history

### Weather
- `POST /api/weather` - Get weather data

### Preferences
- `GET /api/preferences` - Get user preferences
- `PUT /api/preferences` - Update preferences

### Admin Endpoints
- `GET /api/admin/analytics` - System analytics
- `GET /api/admin/users` - List all users
- `POST /api/admin/weather-notification` - Send weather alert
- `POST /api/admin/broadcast` - Send broadcast message
- `POST /api/admin/bulk-predict` - Bulk predictions
- `GET /api/admin/notifications` - View notification logs

### System
- `GET /api/health` - Health check

## 🚀 Deployment on Render

### Prerequisites
- Render account
- Git repository with this code
- Backend already deployed at https://sosens.onrender.com

### Step 1: Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Static Site"**
3. Connect your Git repository

### Step 2: Configure Build Settings

**Build Command:**
```bash
npm install && npm run build
```

**Publish Directory:**
```
dist
```

### Step 3: Environment Variables

No environment variables needed - backend URL is hardcoded in `/config.ts`:
```typescript
export const API_CONFIG = {
  BASE_URL: "https://sosens.onrender.com/api/",
  TIMEOUT: 30000,
};
```

### Step 4: Deploy

1. Click **"Create Static Site"**
2. Wait for build to complete (2-5 minutes)
3. Access your deployed app at: `https://your-app-name.onrender.com`

### Step 5: Verify Connection

1. Visit your deployed frontend
2. Open browser console (F12)
3. Run:
```javascript
fetch('https://sosens.onrender.com/api/health')
  .then(r => r.json())
  .then(data => console.log('Backend status:', data))
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-19T10:30:00"
}
```

## 🧪 Testing After Deployment

### 1. Test Registration
```
1. Go to registration page
2. Enter: Full Name, Phone (+250788123456), Email, Password
3. Click "Register"
4. Should receive success message
```

### 2. Test Login
```
1. Use registered credentials
2. Click "Sign In"
3. Should redirect to dashboard
```

### 3. Test Forgot Password
```
1. Click "Forgot password?" on login page
2. Enter your email/phone
3. Check for reset token (if DEBUG mode enabled on backend)
4. Enter token + new password
5. Reset should succeed
```

### 4. Test Prediction
```
1. Login as farmer
2. Navigate to prediction page
3. Enter soil data:
   - pH: 6.5
   - Nitrogen: 50
   - Phosphorus: 25
   - Potassium: 200
   - Zinc: 5
   - Sulfur: 15
4. Click "Get Recommendation"
5. Should receive crop prediction
```

### 5. Test Admin Features (if admin user)
```
1. Login with admin credentials
2. Access admin dashboard
3. View analytics
4. Check user list
5. Test notifications
```

## 🔧 Local Development

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

### Development Notes

- All API calls go directly to production backend
- No mock data or development fallbacks
- Authentication tokens stored in localStorage
- CORS must be enabled on backend for local development

## 🔒 Security Features

- JWT-based authentication
- Secure password hashing (backend)
- Token expiration handling
- Password reset with time-limited tokens
- Protected admin routes
- Input validation
- XSS prevention via React

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop (1024px+)
- Tablet (768px - 1023px)
- Mobile (320px - 767px)

## 🎨 UI/UX Features

- Clean, minimalist design
- Loading states for all async operations
- Toast notifications for user feedback
- Error handling with clear messages
- Form validation
- Accessible components (shadcn/ui)
- Dark mode support (via Tailwind)

## 🔍 Troubleshooting

### Issue: "Network Error" or "Failed to fetch"

**Cause:** Backend not responding or CORS issue

**Solution:**
```bash
# Check backend health
curl https://sosens.onrender.com/api/health

# If down, wait for Render to restart (cold start)
# Free tier Render services sleep after 15 min inactivity
```

### Issue: "Unauthorized" or "Token expired"

**Cause:** JWT token expired

**Solution:**
1. Logout
2. Login again
3. New token will be issued

### Issue: Login fails with correct credentials

**Cause:** Backend database may not have user

**Solution:**
1. Try registering a new account
2. Check backend logs for errors
3. Verify backend database is running

### Issue: Predictions always return same crop

**Cause:** ML model may not be loaded on backend

**Solution:**
1. Check backend logs for ML model errors
2. Verify model file exists on Render
3. Test with very different soil values
4. Contact backend administrator

## 📊 Performance

### Expected Load Times
- Initial page load: 1-2 seconds
- Login/Register: 1-3 seconds
- Prediction: 2-5 seconds
- Dashboard: 1-2 seconds

### Backend Cold Start
- Render free tier sleeps after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds
- Subsequent requests are fast (< 1 second)

## 🌍 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📄 License

Private project for Rwanda agricultural system.

## 👥 Users

### Farmer User Flow
```
Register → Login → Dashboard → Make Prediction → View History → Update Preferences
```

### Admin User Flow
```
Login (admin) → Admin Dashboard → View Analytics → Manage Users → Send Notifications
```

## 🔄 Update Process

To update the deployed application:

```bash
# 1. Make changes locally
# 2. Test changes
npm run dev

# 3. Commit and push to Git
git add .
git commit -m "Update description"
git push origin main

# 4. Render auto-deploys from main branch
# 5. Wait 2-5 minutes for build
# 6. Verify deployment
```

## 📞 Support

### Quick Tests

**Test backend connection:**
```javascript
// In browser console (F12)
fetch('https://sosens.onrender.com/api/health')
  .then(r => r.json())
  .then(console.log)
```

**Check authentication:**
```javascript
// In browser console
localStorage.getItem('sosens_auth_token') // Should show JWT token
JSON.parse(localStorage.getItem('sosens_user')) // Should show user data
```

**Test prediction endpoint:**
```javascript
// In browser console (must be logged in)
const token = localStorage.getItem('sosens_auth_token');
fetch('https://sosens.onrender.com/api/predict', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    ph: 6.5,
    nitrogen: 50,
    phosphorus: 25,
    potassium: 200,
    zinc: 5,
    sulfur: 15
  })
})
  .then(r => r.json())
  .then(console.log)
```

## ✅ Deployment Checklist

Before deploying:
- [x] Backend URL configured in `/config.ts`
- [x] All API endpoints tested
- [x] Authentication flow working
- [x] Password reset functional
- [x] Prediction system operational
- [x] Admin features accessible
- [x] Responsive design verified
- [x] Error handling implemented
- [x] Loading states added
- [x] Toast notifications working

After deploying:
- [ ] Test registration
- [ ] Test login
- [ ] Test forgot password
- [ ] Test prediction
- [ ] Test dashboard
- [ ] Verify backend connection
- [ ] Check mobile responsiveness
- [ ] Test admin features (if applicable)

## 🎉 Production Ready

This application is **production-ready** and fully configured to work with your Render-hosted backend at `https://sosens.onrender.com`.

All features are implemented, tested, and documented. Simply deploy to Render and it will work immediately with your existing backend.

---

**Version:** 2.0.0  
**Last Updated:** November 19, 2025  
**Status:** Production Ready  
**Backend:** https://sosens.onrender.com
