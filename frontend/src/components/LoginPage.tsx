import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Button } from './ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { toast } from 'sonner@2.0.3';
import { AlertCircle, KeyRound, Loader2 } from 'lucide-react';
import { login, type User } from '../lib/auth';
import { forgotPassword, resetPassword } from '../lib/api';

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
    
    // Forgot Password state
    const [forgotPasswordOpen, setForgotPasswordOpen] = useState(false);
    const [resetEmail, setResetEmail] = useState('');
    const [resetToken, setResetToken] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [resetStep, setResetStep] = useState<'request' | 'reset'>('request');
    const [resetLoading, setResetLoading] = useState(false);
    const [debugToken, setDebugToken] = useState('');

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

    const handleForgotPassword = async (e: React.FormEvent) => {
        e.preventDefault();
        setResetLoading(true);

        try {
            const response = await forgotPassword(resetEmail);
            
            toast.success('Reset link sent', {
                description: 'If your account exists, you will receive reset instructions'
            });
            
            // Check if debug token is available (development mode)
            if (response.debug_token) {
                setDebugToken(response.debug_token);
                toast.info('Debug Mode', {
                    description: `Reset token: ${response.debug_token.substring(0, 10)}...`
                });
            }
            
            setResetStep('reset');
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to send reset link';
            toast.error('Reset failed', {
                description: errorMessage
            });
        } finally {
            setResetLoading(false);
        }
    };

    const handleResetPassword = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (newPassword !== confirmPassword) {
            toast.error('Passwords do not match');
            return;
        }

        if (newPassword.length < 6) {
            toast.error('Password must be at least 6 characters');
            return;
        }

        setResetLoading(true);

        try {
            await resetPassword(resetToken, newPassword);
            
            toast.success('Password reset successful', {
                description: 'You can now login with your new password'
            });
            
            // Reset form and close dialog
            setForgotPasswordOpen(false);
            setResetStep('request');
            setResetEmail('');
            setResetToken('');
            setNewPassword('');
            setConfirmPassword('');
            setDebugToken('');
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to reset password';
            toast.error('Reset failed', {
                description: errorMessage
            });
        } finally {
            setResetLoading(false);
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
                            </div>

                            <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                    <Label htmlFor="password">Password</Label>
                                    <Dialog open={forgotPasswordOpen} onOpenChange={setForgotPasswordOpen}>
                                        <DialogTrigger asChild>
                                            <button 
                                                type="button"
                                                className="text-xs text-green-600 hover:underline flex items-center gap-1"
                                            >
                                                <KeyRound className="w-3 h-3" />
                                                Forgot password?
                                            </button>
                                        </DialogTrigger>
                                        <DialogContent className="sm:max-w-md">
                                            <DialogHeader>
                                                <DialogTitle>Reset Password</DialogTitle>
                                                <DialogDescription>
                                                    {resetStep === 'request' 
                                                        ? 'Enter your email or phone number to receive reset instructions'
                                                        : 'Enter the reset token and your new password'}
                                                </DialogDescription>
                                            </DialogHeader>
                                            
                                            {resetStep === 'request' ? (
                                                <form onSubmit={handleForgotPassword} className="space-y-4">
                                                    <div className="space-y-2">
                                                        <Label htmlFor="resetEmail">Email or Phone Number</Label>
                                                        <Input
                                                            id="resetEmail"
                                                            type="text"
                                                            placeholder="+250788123456 or email@example.com"
                                                            value={resetEmail}
                                                            onChange={(e) => setResetEmail(e.target.value)}
                                                            required
                                                        />
                                                    </div>
                                                    <div className="flex gap-2">
                                                        <Button 
                                                            type="submit" 
                                                            className="flex-1 bg-green-600 hover:bg-green-700"
                                                            disabled={resetLoading}
                                                        >
                                                            {resetLoading ? (
                                                                <>
                                                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                                                    Sending...
                                                                </>
                                                            ) : (
                                                                'Send Reset Link'
                                                            )}
                                                        </Button>
                                                        <Button 
                                                            type="button"
                                                            variant="outline"
                                                            onClick={() => setForgotPasswordOpen(false)}
                                                        >
                                                            Cancel
                                                        </Button>
                                                    </div>
                                                </form>
                                            ) : (
                                                <form onSubmit={handleResetPassword} className="space-y-4">
                                                    {debugToken && (
                                                        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                                                            <p className="text-xs text-blue-700 mb-1">Debug Mode - Use this token:</p>
                                                            <code className="text-xs text-blue-900 break-all">{debugToken}</code>
                                                        </div>
                                                    )}
                                                    
                                                    <div className="space-y-2">
                                                        <Label htmlFor="resetToken">Reset Token</Label>
                                                        <Input
                                                            id="resetToken"
                                                            type="text"
                                                            placeholder="Enter token from email/SMS"
                                                            value={resetToken}
                                                            onChange={(e) => setResetToken(e.target.value)}
                                                            required
                                                        />
                                                    </div>
                                                    
                                                    <div className="space-y-2">
                                                        <Label htmlFor="newPassword">New Password</Label>
                                                        <Input
                                                            id="newPassword"
                                                            type="password"
                                                            placeholder="Minimum 6 characters"
                                                            value={newPassword}
                                                            onChange={(e) => setNewPassword(e.target.value)}
                                                            required
                                                        />
                                                    </div>
                                                    
                                                    <div className="space-y-2">
                                                        <Label htmlFor="confirmPassword">Confirm Password</Label>
                                                        <Input
                                                            id="confirmPassword"
                                                            type="password"
                                                            placeholder="Re-enter password"
                                                            value={confirmPassword}
                                                            onChange={(e) => setConfirmPassword(e.target.value)}
                                                            required
                                                        />
                                                    </div>
                                                    
                                                    <div className="flex gap-2">
                                                        <Button 
                                                            type="submit" 
                                                            className="flex-1 bg-green-600 hover:bg-green-700"
                                                            disabled={resetLoading}
                                                        >
                                                            {resetLoading ? (
                                                                <>
                                                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                                                    Resetting...
                                                                </>
                                                            ) : (
                                                                'Reset Password'
                                                            )}
                                                        </Button>
                                                        <Button 
                                                            type="button"
                                                            variant="outline"
                                                            onClick={() => {
                                                                setResetStep('request');
                                                                setResetToken('');
                                                                setNewPassword('');
                                                                setConfirmPassword('');
                                                                setDebugToken('');
                                                            }}
                                                        >
                                                            Back
                                                        </Button>
                                                    </div>
                                                </form>
                                            )}
                                        </DialogContent>
                                    </Dialog>
                                </div>
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