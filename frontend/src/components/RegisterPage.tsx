import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { toast } from 'sonner@2.0.3';
import { AlertCircle } from 'lucide-react';
import { register } from '../lib/auth';
import { Checkbox } from './ui/checkbox';

interface RegisterPageProps {
    onNavigate: (page: string) => void;
}

export function RegisterPage({ onNavigate }: RegisterPageProps) {
    const [formData, setFormData] = useState({
        fullName: '',
        phone: '',
        email: '',
        password: '',
        confirmPassword: '',
        district: '',
        sector: '',
        village: '',
        farmSize: '',
        preferredContact: 'sms' as 'sms' | 'email',
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const districts = [
        'Bugesera', 'Gatsibo', 'Kayonza', 'Kirehe', 'Ngoma', 'Nyagatare', 'Rwamagana',
        'Gicumbi', 'Rulindo', 'Gakenke', 'Musanze', 'Burera',
        'Kamonyi', 'Muhanga', 'Ruhango', 'Nyanza', 'Karongi', 'Ngororero', 'Nyabihu', 
        'Nyamasheke', 'Rubavu', 'Rusizi', 'Rutsiro',
        'Gasabo', 'Kicukiro', 'Nyarugenge',
        'Gisagara', 'Huye', 'Nyamagabe', 'Nyaruguru'
    ].sort();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        // Validation
        if (!formData.fullName || !formData.password || !formData.district) {
            setError('Please fill in all required fields');
            return;
        }

        if (!formData.phone && !formData.email) {
            setError('Please provide either a phone number or email address');
            return;
        }

        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (formData.password.length < 6) {
            setError('Password must be at least 6 characters');
            return;
        }

        setLoading(true);

        try {
            await register(
                formData.fullName,
                formData.phone || '',
                formData.password,
                formData.district,
                formData.email || undefined,
                formData.sector || undefined,
                formData.village || undefined,
                formData.farmSize ? parseFloat(formData.farmSize) : undefined,
                formData.preferredContact
            );

            toast.success('Registration successful', {
                description: 'You can now login with your credentials'
            });
            
            // Redirect to login
            setTimeout(() => {
                onNavigate('login');
            }, 1500);

        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Registration failed';
            setError(errorMessage);
            toast.error('Registration failed', {
                description: errorMessage
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 py-12">
            <div className="container mx-auto px-4 max-w-2xl">
                <div className="mb-8">
                    <h1 className="text-gray-800 mb-2">Farmer Registration</h1>
                    <p className="text-gray-600">Create an account to access crop recommendations</p>
                </div>

                <Card>
                    <CardHeader>
                        <CardTitle>Register New Account</CardTitle>
                        <CardDescription>All fields marked with * are required</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-6">
                            {error && (
                                <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                                    <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
                                    <p className="text-sm text-red-700">{error}</p>
                                </div>
                            )}

                            <div className="space-y-2">
                                <Label htmlFor="fullName">Full Name *</Label>
                                <Input
                                    id="fullName"
                                    placeholder="Enter your full name"
                                    value={formData.fullName}
                                    onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                                    required
                                />
                            </div>

                            <div className="grid md:grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label htmlFor="phone">Phone Number</Label>
                                    <Input
                                        id="phone"
                                        type="tel"
                                        placeholder="+250788123456"
                                        value={formData.phone}
                                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                    />
                                    <p className="text-xs text-gray-500">For SMS notifications</p>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="email">Email Address</Label>
                                    <Input
                                        id="email"
                                        type="email"
                                        placeholder="farmer@example.com"
                                        value={formData.email}
                                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    />
                                    <p className="text-xs text-gray-500">For email notifications</p>
                                </div>
                            </div>

                            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                                <p className="text-sm text-blue-700">
                                    * At least one contact method (phone or email) is required
                                </p>
                            </div>

                            <div className="grid md:grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label htmlFor="password">Password *</Label>
                                    <Input
                                        id="password"
                                        type="password"
                                        placeholder="Minimum 6 characters"
                                        value={formData.password}
                                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                        required
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="confirmPassword">Confirm Password *</Label>
                                    <Input
                                        id="confirmPassword"
                                        type="password"
                                        placeholder="Re-enter password"
                                        value={formData.confirmPassword}
                                        onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                                        required
                                    />
                                </div>
                            </div>

                            <div className="grid md:grid-cols-3 gap-4">
                                <div className="space-y-2">
                                    <Label htmlFor="district">District *</Label>
                                    <Select value={formData.district} onValueChange={(value) => setFormData({ ...formData, district: value })}>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select district" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {districts.map((district) => (
                                                <SelectItem key={district} value={district}>
                                                    {district}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="sector">Sector</Label>
                                    <Input
                                        id="sector"
                                        placeholder="Optional"
                                        value={formData.sector}
                                        onChange={(e) => setFormData({ ...formData, sector: e.target.value })}
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="village">Village</Label>
                                    <Input
                                        id="village"
                                        placeholder="Optional"
                                        value={formData.village}
                                        onChange={(e) => setFormData({ ...formData, village: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="farmSize">Farm Size (Hectares)</Label>
                                <Input
                                    id="farmSize"
                                    type="number"
                                    step="0.1"
                                    placeholder="Optional"
                                    value={formData.farmSize}
                                    onChange={(e) => setFormData({ ...formData, farmSize: e.target.value })}
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="preferredContact">Preferred Contact Method *</Label>
                                <Select 
                                    value={formData.preferredContact} 
                                    onValueChange={(value: 'sms' | 'email') => setFormData({ ...formData, preferredContact: value })}
                                >
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="sms">SMS</SelectItem>
                                        <SelectItem value="email">Email</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="flex gap-4">
                                <Button 
                                    type="submit" 
                                    className="flex-1 bg-green-600 hover:bg-green-700"
                                    disabled={loading}
                                >
                                    {loading ? 'Creating Account...' : 'Create Account'}
                                </Button>
                                <Button 
                                    type="button"
                                    variant="outline"
                                    onClick={() => onNavigate('login')}
                                    disabled={loading}
                                >
                                    Cancel
                                </Button>
                            </div>
                        </form>

                        <div className="mt-6 text-center">
                            <p className="text-sm text-gray-600">
                                Already have an account?{' '}
                                <button 
                                    onClick={() => onNavigate('login')}
                                    className="text-green-600 hover:underline"
                                >
                                    Login here
                                </button>
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}