import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Sprout, FileText, TrendingUp, Calendar, Loader2, Settings } from 'lucide-react';
import { getRecommendations, getSoilReadings, updatePreferences } from '../lib/api';
import type { User } from '../lib/auth';
import { toast } from 'sonner@2.0.3';
import { Switch } from './ui/switch';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';

interface FarmerDashboardProps {
    user: User;
    onNavigate: (page: string) => void;
}

export function FarmerDashboard({ user, onNavigate }: FarmerDashboardProps) {
    const [recommendations, setRecommendations] = useState<any[]>([]);
    const [soilReadings, setSoilReadings] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [showPreferences, setShowPreferences] = useState(false);
    const [preferences, setPreferences] = useState({
        receive_notifications: user.receive_notifications,
        preferred_contact: user.preferred_contact
    });
    const [savingPreferences, setSavingPreferences] = useState(false);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            setLoading(true);
            const [recommendationsData, soilData] = await Promise.all([
                getRecommendations().catch(() => ({ recommendations: [] })),
                getSoilReadings().catch(() => ({ readings: [] }))
            ]);
            setRecommendations(recommendationsData.recommendations || []);
            setSoilReadings(soilData.readings || []);
        } catch (error) {
            console.error('Failed to load dashboard:', error);
            toast.error('Failed to load some dashboard data');
        } finally {
            setLoading(false);
        }
    };

    const handleSavePreferences = async () => {
        try {
            setSavingPreferences(true);
            await updatePreferences(preferences);
            toast.success('Preferences updated successfully');
            setShowPreferences(false);
        } catch (error) {
            toast.error('Failed to update preferences');
        } finally {
            setSavingPreferences(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <Loader2 className="w-12 h-12 animate-spin text-green-600 mx-auto mb-4" />
                    <p className="text-gray-600">Loading dashboard...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="container mx-auto px-4">
                <div className="mb-8 flex items-center justify-between">
                    <div>
                        <h1 className="text-gray-800 mb-2">Welcome, {user.full_name}</h1>
                        <p className="text-gray-600">Your farming overview and recent activities</p>
                        {user.district && (
                            <p className="text-sm text-gray-500">Location: {user.district}{user.sector ? `, ${user.sector}` : ''}</p>
                        )}
                    </div>
                    <Button 
                        variant="outline"
                        onClick={() => setShowPreferences(!showPreferences)}
                        className="flex items-center gap-2"
                    >
                        <Settings className="w-4 h-4" />
                        Preferences
                    </Button>
                </div>

                {/* Preferences Card */}
                {showPreferences && (
                    <Card className="mb-6 border-l-4 border-l-blue-600">
                        <CardHeader>
                            <CardTitle>Notification Preferences</CardTitle>
                            <CardDescription>Manage how you receive crop recommendations</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex items-center justify-between">
                                <div className="space-y-0.5">
                                    <Label>Receive Notifications</Label>
                                    <p className="text-sm text-gray-500">Get alerts for new recommendations</p>
                                </div>
                                <Switch
                                    checked={preferences.receive_notifications}
                                    onCheckedChange={(checked) => 
                                        setPreferences({ ...preferences, receive_notifications: checked })
                                    }
                                />
                            </div>

                            <div className="space-y-2">
                                <Label>Preferred Contact Method</Label>
                                <Select
                                    value={preferences.preferred_contact}
                                    onValueChange={(value: 'sms' | 'email') => 
                                        setPreferences({ ...preferences, preferred_contact: value })
                                    }
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

                            <div className="flex gap-2">
                                <Button 
                                    onClick={handleSavePreferences}
                                    disabled={savingPreferences}
                                    className="bg-green-600 hover:bg-green-700"
                                >
                                    {savingPreferences ? 'Saving...' : 'Save Preferences'}
                                </Button>
                                <Button 
                                    variant="outline"
                                    onClick={() => setShowPreferences(false)}
                                >
                                    Cancel
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <Card className="border-l-4 border-l-green-600">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle>Total Recommendations</CardTitle>
                            <Sprout className="h-5 w-5 text-green-600" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-gray-900">{recommendations.length}</div>
                            <p className="text-xs text-gray-600 mt-1">Crop recommendations</p>
                        </CardContent>
                    </Card>

                    <Card className="border-l-4 border-l-blue-600">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle>Soil Tests</CardTitle>
                            <FileText className="h-5 w-5 text-blue-600" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-gray-900">{soilReadings.length}</div>
                            <p className="text-xs text-gray-600 mt-1">Completed tests</p>
                        </CardContent>
                    </Card>

                    <Card className="border-l-4 border-l-purple-600">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle>Farm Size</CardTitle>
                            <TrendingUp className="h-5 w-5 text-purple-600" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-gray-900">{user.farm_size || 'N/A'}</div>
                            <p className="text-xs text-gray-600 mt-1">Hectares</p>
                        </CardContent>
                    </Card>
                </div>

                {/* Quick Actions */}
                <Card className="mb-8 bg-gradient-to-r from-green-50 to-blue-50 border-none shadow-lg">
                    <CardContent className="pt-6">
                        <div className="text-center">
                            <h3 className="text-gray-800 mb-4">Get a New Crop Recommendation</h3>
                            <Button 
                                onClick={() => onNavigate('predict')}
                                size="lg"
                                className="bg-green-600 hover:bg-green-700"
                            >
                                <Sprout className="w-4 h-4 mr-2" />
                                Start Prediction
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                {/* Recent Recommendations */}
                <Card>
                    <CardHeader>
                        <CardTitle>Recent Recommendations</CardTitle>
                        <CardDescription>Your latest crop recommendations and soil analyses</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {recommendations.length === 0 ? (
                            <div className="text-center py-8">
                                <Sprout className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                                <p className="text-gray-600 mb-4">No recommendations yet</p>
                                <Button 
                                    onClick={() => onNavigate('predict')}
                                    variant="outline"
                                >
                                    Get Your First Recommendation
                                </Button>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {recommendations.slice(0, 5).map((rec) => (
                                    <div 
                                        key={rec.id}
                                        className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                                    >
                                        <div className="flex items-start justify-between mb-2">
                                            <div>
                                                <h4 className="text-gray-800">{rec.recommended_crop}</h4>
                                                <p className="text-sm text-gray-500">
                                                    {new Date(rec.created_at).toLocaleDateString('en-US', {
                                                        year: 'numeric',
                                                        month: 'long',
                                                        day: 'numeric'
                                                    })}
                                                </p>
                                            </div>
                                            <Badge className="bg-green-600">
                                                {Math.round(rec.confidence_score * 100)}% confidence
                                            </Badge>
                                        </div>
                                        
                                        <div className="grid md:grid-cols-2 gap-3 mt-3">
                                            <div className="text-sm">
                                                <span className="text-gray-600">Soil Health:</span>{' '}
                                                <span className={
                                                    rec.soil_health_status === 'Optimal' 
                                                        ? 'text-green-600' 
                                                        : rec.soil_health_status === 'Moderate'
                                                        ? 'text-yellow-600'
                                                        : 'text-red-600'
                                                }>
                                                    {rec.soil_health_status}
                                                </span>
                                            </div>
                                            <div className="text-sm">
                                                <span className="text-gray-600">Season:</span>{' '}
                                                <span className="text-gray-800">{rec.planting_season}</span>
                                            </div>
                                        </div>

                                        {rec.weather_advice && (
                                            <div className="mt-3 p-2 bg-blue-50 rounded text-sm text-gray-700">
                                                Weather: {rec.weather_advice}
                                            </div>
                                        )}

                                        <div className="mt-3 text-sm text-gray-700">
                                            <span className="text-gray-600">Fertilizer:</span> {rec.fertilizer_recommendation}
                                        </div>
                                    </div>
                                ))}

                                {recommendations.length > 5 && (
                                    <div className="text-center pt-4">
                                        <p className="text-sm text-gray-500">
                                            Showing 5 of {recommendations.length} recommendations
                                        </p>
                                    </div>
                                )}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}