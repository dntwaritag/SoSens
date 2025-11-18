import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Button } from './ui/button';
import { toast } from 'sonner';
import { AlertCircle } from 'lucide-react';
import { login, type User } from '../lib/auth';

interface LoginPageProps {
    onLogin: (user: User) => void;
    onNavigate: (page: string) => void;
}

export function LoginPage({ onLogin, onNavigate }: LoginPageProps) {
    const [credentials, setCredentials] = useState({
        username: '',
        password: '',
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const user = await login(credentials.username, credentials.password);
            
            toast.success('Login successful', {
                description: `Welcome back, ${user.full_name}`
            });
            
            onLogin(user);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Login failed';
            setError(errorMessage);
            toast.error('Login failed', {
                description: errorMessage
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <h1 className="text-gray-800 mb-2">Login</h1>
                    <p className="text-gray-600">Access your crop recommendations</p>
                </div>

                <Card>
                    <CardHeader>
                        <CardTitle>Sign In</CardTitle>
                        <CardDescription>Enter your credentials to continue</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            {error && (
                                <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                                    <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
                                    <p className="text-sm text-red-700">{error}</p>
                                </div>
                            )}

                            <div className="space-y-2">
                                <Label htmlFor="username">Phone Number or Email</Label>
                                <Input
                                    id="username"
                                    type="text"
                                    placeholder="+250788123456 or email@example.com"
                                    value={credentials.username}
                                    onChange={(e) => setCredentials({ 
                                        ...credentials, 
                                        username: e.target.value 
                                    })}
                                    required
                                />
                                <p className="text-xs text-gray-500">
                                    Demo: Use 'admin' / 'admin123' for admin access
                                </p>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="password">Password</Label>
                                <Input
                                    id="password"
                                    type="password"
                                    placeholder="Enter your password"
                                    value={credentials.password}
                                    onChange={(e) => setCredentials({ 
                                        ...credentials, 
                                        password: e.target.value 
                                    })}
                                    required
                                />
                            </div>

                            <Button 
                                type="submit" 
                                className="w-full bg-green-600 hover:bg-green-700"
                                disabled={loading}
                            >
                                {loading ? 'Signing in...' : 'Sign In'}
                            </Button>
                        </form>

                        <div className="mt-6 text-center">
                            <p className="text-sm text-gray-600">
                                Don't have an account?{' '}
                                <button 
                                    onClick={() => onNavigate('register')}
                                    className="text-green-600 hover:underline"
                                >
                                    Register here
                                </button>
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
