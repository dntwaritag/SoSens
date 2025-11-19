import { loginUser, registerUser, getCurrentUserInfo } from './api';

export interface User {
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
}

const AUTH_STORAGE_KEY = 'sosens_auth_token';
const USER_STORAGE_KEY = 'sosens_user';

export async function register(
    fullName: string, 
    phoneNumber: string, 
    password: string,
    district: string,
    email?: string,
    sector?: string,
    village?: string,
    farmSize?: number,
    preferredContact?: 'sms' | 'email'
): Promise<User> {
    const response = await registerUser({
        full_name: fullName,
        phone_number: phoneNumber,
        email,
        password,
        role: 'farmer',
        district,
        sector,
        village,
        farm_size: farmSize,
        preferred_contact: preferredContact || 'sms',
        receive_notifications: true
    });
    
    // Store auth state
    if (response.access_token) {
        localStorage.setItem(AUTH_STORAGE_KEY, response.access_token);
    }
    
    const user: User = response.user;
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));

    return user;
}

export async function login(username: string, password: string): Promise<User> {
    const response = await loginUser(username, password);
    
    // Store auth state
    if (response.access_token) {
        localStorage.setItem(AUTH_STORAGE_KEY, response.access_token);
    }
    
    const user: User = response.user;
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));

    return user;
}

export async function refreshCurrentUser(): Promise<User | null> {
    try {
        const user = await getCurrentUserInfo();
        localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
        return user;
    } catch (error) {
        // If token is invalid, clear auth
        logout();
        return null;
    }
}

export function logout(): void {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    localStorage.removeItem(USER_STORAGE_KEY);
}

export function getCurrentUser(): User | null {
    const userStr = localStorage.getItem(USER_STORAGE_KEY);
    
    if (userStr) {
        try {
            return JSON.parse(userStr);
        } catch {
            return null;
        }
    }
    
    return null;
}

export function getAuthToken(): string | null {
    return localStorage.getItem(AUTH_STORAGE_KEY);
}

export function isAuthenticated(): boolean {
    return !!getAuthToken() && !!getCurrentUser();
}

export function isAdmin(user: User | null): boolean {
    return user?.role === 'admin';
}

export function isFarmer(user: User | null): boolean {
    return user?.role === 'farmer';
}