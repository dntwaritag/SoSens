// Backend API Configuration
// ============================================================================
// Production Backend URL - Deployed on Render
// ============================================================================

export const API_CONFIG = {
  BASE_URL: "https://sosens.onrender.com/api/", // Production FastAPI backend on Render
  TIMEOUT: 30000, // 30 seconds (for Render cold starts)
};

// ============================================================================
// BACKEND INFORMATION
// ============================================================================
// Backend: https://sosens.onrender.com
// Documentation: https://sosens.onrender.com/docs
// Health Check: https://sosens.onrender.com/api/health
//
// The application connects exclusively to the production backend.
// No mock data or fallback mode is available.
//
// Available Endpoints:
// - Authentication: /api/auth/register, /api/auth/login, /api/auth/me
// - Predictions: /api/predict, /api/recommendations, /api/soil-readings
// - Weather: /api/weather
// - Admin: /api/admin/users, /api/admin/analytics, /api/admin/broadcast
// - Preferences: /api/preferences
// ============================================================================
