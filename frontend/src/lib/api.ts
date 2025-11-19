import { API_CONFIG } from '../config';
import { getAuthToken } from './auth';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface UserRegisterRequest {
    full_name: string;
    email?: string;
    phone_number?: string;
    password: string;
    role: 'farmer' | 'admin';
    district?: string;
    sector?: string;
    village?: string;
    farm_size?: number;
    preferred_contact: 'sms' | 'email';
    receive_notifications: boolean;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
    user: {
        id: number;
        full_name: string;
        email?: string;
        phone_number?: string;
        role: 'farmer' | 'admin';
        district?: string;
        sector?: string;
        village?: string;
        farm_size?: number;
        preferred_contact: 'sms' | 'email';
        receive_notifications: boolean;
        is_active: boolean;
        created_at: string;
        last_login?: string;
    };
}

export interface PredictionRequest {
    ph: number;
    nitrogen: number;
    phosphorus: number;
    potassium: number;
    zinc?: number;
    sulfur?: number;
    include_weather?: boolean;
}

export interface PredictionResponse {
    success: boolean;
    crop: string;
    confidence: number;
    soil_health: string;
    fertilizer_advice: string;
    planting_season: string;
    weather_advice?: string;
    alternatives: Array<{ crop: string; confidence: number }>;
}

export interface RecommendationResponse {
    id: number;
    user_id: number;
    soil_reading_id: number;
    recommended_crop: string;
    confidence_score: number;
    alternative_crops: any[];
    soil_health_status: string;
    soil_issues: string[];
    fertilizer_recommendation: string;
    planting_season: string;
    weather_advice?: string;
    created_at: string;
}

export interface SoilReadingResponse {
    id: number;
    user_id: number;
    ph: number;
    nitrogen: number;
    phosphorus: number;
    potassium: number;
    zinc?: number;
    sulfur?: number;
    reading_date: string;
}

export interface WeatherResponse {
    success: boolean;
    district: string;
    temperature: number;
    humidity: number;
    rainfall: number;
    condition: string;
    advice: string;
    updated_at: string;
}

export interface DashboardAnalytics {
    success: boolean;
    summary: {
        total_users: number;
        farmers: number;
        total_readings: number;
        total_recommendations: number;
        total_notifications?: number;
        sent_notifications?: number;
    };
    top_crops: Array<{ crop: string; count: number }>;
    by_district: Array<{ district: string; count: number }>;
}

// ============================================================================
// API HELPER FUNCTIONS
// ============================================================================

async function apiCall<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    // Clean up endpoint and base URL to avoid double slashes
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.substring(1) : endpoint;
    const baseUrl = API_CONFIG.BASE_URL.replace(/\/$/, '');
    const url = `${baseUrl}/${cleanEndpoint}`;
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);

    try {
        console.log(`🌐 API Call: ${url}`);
        
        const token = getAuthToken();
        const headers: HeadersInit = {
            'Content-Type': 'application/json',
        };
        
        // Merge with provided headers (they take precedence)
        if (options.headers) {
            Object.assign(headers, options.headers);
        }
        
        // Add auth token if available
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await fetch(url, {
            ...options,
            signal: controller.signal,
            headers,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            console.error(`❌ API Error (${response.status}):`, error);
            throw new Error(error.error || error.detail || `Request failed with status ${response.status}`);
        }

        const data = await response.json();
        console.log(`✅ API Success:`, data);
        return data;
    } catch (error) {
        clearTimeout(timeoutId);
        
        if (error instanceof Error) {
            if (error.name === 'AbortError') {
                console.error('⏱️ Request timeout - backend may be starting up');
                throw new Error('Request timeout. The backend may be waking up. Please try again in a moment.');
            }
            console.error('❌ API Error:', error.message);
            throw error;
        }
        throw new Error('Unknown error occurred');
    }
}

// ============================================================================
// AUTHENTICATION APIs
// ============================================================================

export async function registerUser(data: UserRegisterRequest): Promise<AuthResponse> {
    return apiCall<AuthResponse>(
        'auth/register',
        {
            method: 'POST',
            body: JSON.stringify(data),
        }
    );
}

export async function loginUser(username: string, password: string): Promise<AuthResponse> {
    return apiCall<AuthResponse>(
        'auth/login',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                username: username,
                password: password,
            }),
        }
    );
}

export async function getCurrentUserInfo(): Promise<any> {
    return apiCall<any>(
        'auth/me',
        { method: 'GET' }
    );
}

export async function forgotPassword(username: string): Promise<any> {
    return apiCall<any>(
        'auth/forgot-password',
        {
            method: 'POST',
            body: JSON.stringify({ username }),
        }
    );
}

export async function resetPassword(token: string, new_password: string): Promise<any> {
    return apiCall<any>(
        'auth/reset-password',
        {
            method: 'POST',
            body: JSON.stringify({ token, new_password }),
        }
    );
}

// ============================================================================
// PREDICTION APIs
// ============================================================================

export async function createPrediction(data: PredictionRequest): Promise<PredictionResponse> {
    return apiCall<PredictionResponse>(
        'predict',
        {
            method: 'POST',
            body: JSON.stringify(data),
        }
    );
}

export async function getRecommendations(): Promise<{ success: boolean; total: number; recommendations: any[] }> {
    const response = await apiCall<any>(
        'recommendations',
        { method: 'GET' }
    );
    
    // Transform backend response to match expected format
    if (response.recommendations) {
        return {
            success: response.success || true,
            total: response.total || response.recommendations.length,
            recommendations: response.recommendations.map((r: any) => ({
                id: r.id,
                user_id: r.user_id,
                soil_reading_id: r.soil_reading_id,
                recommended_crop: r.crop || r.recommended_crop,
                confidence_score: r.confidence || r.confidence_score,
                alternative_crops: r.alternative_crops || [],
                soil_health_status: r.soil_health || r.soil_health_status,
                soil_issues: r.soil_issues || [],
                fertilizer_recommendation: r.fertilizer || r.fertilizer_recommendation,
                planting_season: r.planting_season || 'Check seasonal calendar',
                weather_advice: r.weather_advice,
                created_at: r.date || r.created_at,
            }))
        };
    }
    
    return response;
}

export async function getSoilReadings(): Promise<{ success: boolean; total: number; readings: any[] }> {
    const response = await apiCall<any>(
        'soil-readings',
        { method: 'GET' }
    );
    
    // Ensure response has expected structure
    return {
        success: response.success !== false,
        total: response.total || (response.readings?.length || 0),
        readings: response.readings || []
    };
}

export async function submitSoilReading(data: {
    ph: number;
    nitrogen: number;
    phosphorus: number;
    potassium: number;
    zinc?: number;
    sulfur?: number;
}): Promise<any> {
    return apiCall<any>(
        'soil-readings',
        {
            method: 'POST',
            body: JSON.stringify(data),
        }
    );
}

// ============================================================================
// WEATHER API
// ============================================================================

export async function getWeather(): Promise<WeatherResponse> {
    return apiCall<WeatherResponse>(
        'weather',
        { method: 'GET' }
    );
}

// ============================================================================
// PREFERENCES API
// ============================================================================

export async function updatePreferences(data: {
    receive_notifications?: boolean;
    preferred_contact?: 'sms' | 'email';
    farm_size?: number;
    district?: string;
    sector?: string;
    village?: string;
}): Promise<{ success: boolean; message: string; user: any }> {
    return apiCall<{ success: boolean; message: string; user: any }>(
        'preferences',
        {
            method: 'PUT',
            body: JSON.stringify(data),
        }
    );
}

// ============================================================================
// ADMIN APIs
// ============================================================================

export async function getAdminAnalytics(): Promise<DashboardAnalytics> {
    const response = await apiCall<any>(
        'admin/analytics',
        { method: 'GET' }
    );
    
    return {
        success: response.success !== false,
        summary: {
            total_users: response.summary?.total_users || 0,
            farmers: response.summary?.farmers || 0,
            total_readings: response.summary?.total_readings || 0,
            total_recommendations: response.summary?.total_recommendations || 0,
            total_notifications: response.summary?.total_notifications,
            sent_notifications: response.summary?.sent_notifications,
        },
        top_crops: response.top_crops || [],
        by_district: response.by_district || [],
    };
}

export async function getAllUsers(skip: number = 0, limit: number = 50, role?: string, district?: string): Promise<any> {
    let url = `admin/users?skip=${skip}&limit=${limit}`;
    if (role) url += `&role=${role}`;
    if (district) url += `&district=${district}`;
    
    const response = await apiCall<any>(url, { method: 'GET' });
    
    return {
        success: response.success !== false,
        users: response.users || [],
        total: response.total || 0,
    };
}

export async function sendWeatherNotifications(): Promise<any> {
    return apiCall<any>(
        'admin/send-weather',
        { method: 'POST' }
    );
}

export async function broadcastMessage(message: string, district?: string): Promise<any> {
    return apiCall<any>(
        'admin/broadcast',
        {
            method: 'POST',
            body: JSON.stringify({ message, district }),
        }
    );
}

export async function sendBulkPredictions(crop: string, district?: string, message?: string): Promise<any> {
    return apiCall<any>(
        'admin/send-predictions',
        {
            method: 'POST',
            body: JSON.stringify({ crop, district, message }),
        }
    );
}

export async function getNotificationLogs(skip: number = 0, limit: number = 100): Promise<any> {
    return apiCall<any>(
        `admin/notification-logs?skip=${skip}&limit=${limit}`,
        { method: 'GET' }
    );
}

// ============================================================================
// SYSTEM APIs
// ============================================================================

export async function checkHealth(): Promise<{ status: string; timestamp: string }> {
    return apiCall<{ status: string; timestamp: string }>(
        'health',
        { method: 'GET' }
    );
}
