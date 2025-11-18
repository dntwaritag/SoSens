import { API_CONFIG } from '../config';
import { getAuthToken } from './auth';

    const apiClient = axios.create({
    baseURL: API_CONFIG.BASE_URL,
    timeout: API_CONFIG.TIMEOUT,
    });

    // Add request interceptor for better error handling
    apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
        config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
    );

    // Add response interceptor
    apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
        }
        return Promise.reject(error);
    }
    );

    export default apiClient;
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
    preferred_contact: 'sms' | 'email' | 'both';
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
        preferred_contact: 'sms' | 'email' | 'both';
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
        active_users: number;
        farmers?: number;
        total_readings: number;
        total_recommendations: number;
    };
    top_crops: Array<{ crop: string; count: number }>;
    users_by_district: Array<{ district: string; count: number }>;
    soil_health?: Array<{ status: string; count: number }>;
}

// ============================================================================
// MOCK DATA STORE (for fallback)
// ============================================================================

let mockUsers: any[] = [
    {
        id: 1,
        full_name: 'Admin User',
        phone_number: 'admin',
        password: 'admin123',
        district: 'Kigali',
        role: 'admin',
        preferred_contact: 'email',
        receive_notifications: true,
        is_active: true,
        created_at: new Date().toISOString()
    }
];
let mockRecommendations: any[] = [];
let nextUserId = 2;
let nextRecommendationId = 1;

// ============================================================================
// API HELPER FUNCTIONS
// ============================================================================

async function apiCall<T>(
    endpoint: string,
    options: RequestInit = {},
    mockFallback?: () => T
): Promise<T> {
    // Clean up endpoint and base URL to avoid double slashes
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.substring(1) : endpoint;
    const baseUrl = API_CONFIG.BASE_URL.replace(/\/$/, ''); // Remove trailing slash
    const url = `${baseUrl}/${cleanEndpoint}`;
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);

    try {
        console.log(`API Call: ${url}`);
        
        const token = getAuthToken();
        // Default headers, but allow options.headers to override
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
            console.error(`API Error (${response.status}):`, error);
            throw new Error(error.error || error.detail || `API Error: ${response.status}`);
        }

        const data = await response.json();
        console.log(`API Success: ${endpoint}`, data);
        return data;
    } catch (error) {
        clearTimeout(timeoutId);
        
        // If backend is unavailable and we have a mock fallback, use it
        if (mockFallback && (
            error instanceof TypeError || // Network error
            (error instanceof Error && error.name === 'AbortError')
        )) {
            // Only log once per session for cleaner console
            if (!sessionStorage.getItem('backend_unavailable_logged')) {
                console.group('🔌 Backend Connection');
                console.warn('Backend is not responding - using demo mode');
                console.info('Tried URL:', url);
                console.info('To connect to your backend:');
                console.info('  1. Start your FastAPI server: python app.py');
                console.info('  2. Ensure it\'s running on port 5000');
                console.info('  3. Check http://127.0.0.1:5000/ in your browser');
                console.info('\n Demo mode works fully with mock data!');
                console.groupEnd();
                sessionStorage.setItem('backend_unavailable_logged', 'true');
            }
            return mockFallback();
        }
        
        if (error instanceof Error) {
            if (error.name === 'AbortError') {
                throw new Error('Request timeout - backend may be unavailable');
            }
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
        },
        () => {
            // Mock registration
            const newUser = {
                id: nextUserId++,
                full_name: data.full_name,
                phone_number: data.phone_number,
                email: data.email,
                district: data.district,
                sector: data.sector,
                village: data.village,
                farm_size: data.farm_size,
                role: data.role,
                preferred_contact: data.preferred_contact,
                receive_notifications: data.receive_notifications,
                is_active: true,
                created_at: new Date().toISOString(),
                password: data.password
            };
            mockUsers.push(newUser);
            
            return {
                access_token: 'mock_token_' + newUser.id,
                token_type: 'bearer',
                user: newUser
            };
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
        },
        () => {
            // Mock login
            const user = mockUsers.find(
                u => (u.phone_number === username || u.email === username) && u.password === password
            );
            
            if (!user) {
                throw new Error('Invalid credentials');
            }
            
            return {
                access_token: 'mock_token_' + user.id,
                token_type: 'bearer',
                user: user
            };
        }
    );
}

export async function getCurrentUserInfo(): Promise<any> {
    return apiCall<any>(
        'auth/me',
        { method: 'GET' }
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
        },
        () => {
            // Mock prediction
            const crops = ['Maize', 'Beans', 'Irish Potatoes', 'Cassava', 'Sorghum', 'Wheat'];
            const predictedCrop = crops[Math.floor(Math.random() * crops.length)];
            const confidence = 85 + Math.floor(Math.random() * 15);
            
            const mockRecommendation = {
                id: nextRecommendationId++,
                crop: predictedCrop,
                confidence: confidence / 100,
                created_at: new Date().toISOString(),
            };
            mockRecommendations.push(mockRecommendation);
            
            return {
                success: true,
                crop: predictedCrop,
                confidence: confidence / 100,
                soil_health: data.ph >= 6.0 && data.ph <= 7.0 ? 'Optimal' : 'Moderate',
                fertilizer_advice: 'Apply NPK fertilizer at recommended rates',
                planting_season: 'Best planted during rainy season (September-December)',
                weather_advice: 'Current weather conditions are favorable for planting',
                alternatives: [
                    { crop: crops[(crops.indexOf(predictedCrop) + 1) % crops.length], confidence: (confidence - 10) / 100 },
                    { crop: crops[(crops.indexOf(predictedCrop) + 2) % crops.length], confidence: (confidence - 20) / 100 },
                ],
            };
        }
    );
}

export async function getRecommendations(): Promise<{ success: boolean; total: number; recommendations: any[] }> {
    const response = await apiCall<any>(
        'recommendations',
        { method: 'GET' },
        () => {
            return {
                success: true,
                total: mockRecommendations.length,
                recommendations: mockRecommendations.map(r => ({
                    id: r.id,
                    crop: r.crop,
                    confidence: r.confidence,
                    soil_health: 'Optimal',
                    fertilizer: 'NPK fertilizer',
                    date: r.created_at,
                }))
            };
        }
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
        { method: 'GET' },
        () => ({ success: true, total: 0, readings: [] })
    );
    
    // Ensure response has expected structure
    return {
        success: response.success !== false,
        total: response.total || (response.readings?.length || 0),
        readings: response.readings || []
    };
}

// ============================================================================
// WEATHER API
// ============================================================================

export async function getWeather(): Promise<WeatherResponse> {
    return apiCall<WeatherResponse>(
        'weather',
        { method: 'GET' },
        () => ({
            success: true,
            district: 'Kigali',
            temperature: 24,
            humidity: 65,
            rainfall: 5,
            condition: 'Partly Cloudy',
            advice: 'Good conditions for most crops',
            updated_at: new Date().toISOString(),
        })
    );
}

// ============================================================================
// ADMIN APIs
// ============================================================================

export async function getAdminAnalytics(): Promise<DashboardAnalytics> {
    const response = await apiCall<any>(
        'admin/analytics',
        { method: 'GET' },
        () => ({
            success: true,
            summary: {
                total_users: mockUsers.length,
                active_users: mockUsers.filter(u => u.is_active).length,
                farmers: mockUsers.filter(u => u.role === 'farmer').length,
                total_readings: 0,
                total_recommendations: mockRecommendations.length,
            },
            top_crops: [
                { crop: 'Maize', count: 150 },
                { crop: 'Beans', count: 120 },
                { crop: 'Irish Potatoes', count: 95 },
            ],
            users_by_district: [
                { district: 'Kigali', count: 45 },
                { district: 'Huye', count: 38 },
                { district: 'Muhanga', count: 32 },
            ],
            soil_health: [
                { status: 'Optimal', count: 45 },
                { status: 'Good', count: 30 },
                { status: 'Needs Improvement', count: 15 },
            ]
        })
    );
    
    return {
        success: response.success !== false,
        summary: response.summary || {},
        top_crops: response.top_crops || [],
        users_by_district: response.users_by_district || [],
        soil_health: response.soil_health || []
    };
}

export async function getAllUsers(skip: number = 0, limit: number = 50): Promise<any> {
    const response = await apiCall<any>(
        `admin/users?skip=${skip}&limit=${limit}`,
        { method: 'GET' },
        () => ({
            success: true,
            users: mockUsers.filter(u => u.role === 'farmer'),
            total: mockUsers.filter(u => u.role === 'farmer').length,
            page: 1,
        })
    );
    
    return {
        success: response.success !== false,
        users: response.users || [],
        total: response.total || 0,
        page: response.page || 1
    };
}

// ============================================================================
// CROPS API
// ============================================================================

export async function getCrops(): Promise<{ crops: string[]; total: number }> {
    return apiCall<{ crops: string[]; total: number }>(
        'crops',
        { method: 'GET' },
        () => ({
            crops: ['Maize', 'Beans', 'Irish Potatoes', 'Cassava', 'Sorghum', 'Wheat', 'Rice', 'Soybeans'],
            total: 8,
        })
    );
}

export async function getCropDetails(cropName: string): Promise<any> {
    return apiCall<any>(
        `crops/${cropName}`,
        { method: 'GET' },
        () => ({
            success: true,
            crop: cropName,
            optimal_conditions: {
                ph: '6.0-7.0',
                nitrogen: '40-60 kg/ha',
                phosphorus: '20-30 kg/ha',
                potassium: '180-220 kg/ha',
            },
            planting_season: 'September-December',
            maturity_period: '3-4 months',
        })
    );
}

// ============================================================================
// PREFERENCES API
// ============================================================================

export async function updatePreferences(data: {
    receive_notifications: boolean;
    preferred_contact: 'sms' | 'email' | 'both';
}): Promise<{ message: string }> {
    return apiCall<{ message: string }>(
        'preferences',
        {
            method: 'PUT',
            body: JSON.stringify(data),
        },
        () => ({ message: 'Preferences updated successfully' })
    );
}
