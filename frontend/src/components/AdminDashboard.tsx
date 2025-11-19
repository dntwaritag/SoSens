import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import {
    Users,
    TrendingUp,
    BarChart3,
    Sprout,
    MapPin,
    Activity,
    Bell,
    AlertCircle,
} from 'lucide-react';
import { getAdminAnalytics, getAllUsers } from '../lib/api';
import type { User } from '../lib/auth';
import { toast } from 'sonner@2.0.3';

interface AdminDashboardProps {
    user: User;
}

export function AdminDashboard({ user }: AdminDashboardProps) {
    const [analytics, setAnalytics] = useState<any>(null);
    const [users, setUsers] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            const [analyticsData, usersData] = await Promise.all([
                getAdminAnalytics(),
                getAllUsers(0, 10)
            ]);
            
            setAnalytics(analyticsData);
            setUsers(usersData.users || []);
        } catch (error) {
            toast.error('Failed to load dashboard data');
            console.error('Dashboard error:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 py-8">
                <div className="container mx-auto px-4">
                    <div className="text-center py-12">
                        <Activity className="w-8 h-8 animate-spin mx-auto text-green-600 mb-4" />
                        <p className="text-gray-600">Loading admin dashboard...</p>
                    </div>
                </div>
            </div>
        );
    }

    const summary = analytics?.summary || {};

    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="container mx-auto px-4">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-gray-800 mb-2">Admin Dashboard</h1>
                    <p className="text-gray-600">
                        Rwanda Soil Quality Monitoring System - Administration Panel
                    </p>
                </div>

                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <Card className="border-t-4 border-t-blue-600">
                        <CardHeader className="pb-3">
                            <CardTitle className="text-sm flex items-center gap-2">
                                <Users className="w-4 h-4 text-blue-600" />
                                Total Users
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-blue-700">{summary.total_users || 0}</p>
                            <p className="text-xs text-gray-500 mt-1">
                                {summary.active_users || 0} active
                            </p>
                        </CardContent>
                    </Card>

                    <Card className="border-t-4 border-t-green-600">
                        <CardHeader className="pb-3">
                            <CardTitle className="text-sm flex items-center gap-2">
                                <Sprout className="w-4 h-4 text-green-600" />
                                Recommendations
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-green-700">{summary.total_recommendations || 0}</p>
                            <p className="text-xs text-gray-500 mt-1">Total predictions made</p>
                        </CardContent>
                    </Card>

                    <Card className="border-t-4 border-t-orange-600">
                        <CardHeader className="pb-3">
                            <CardTitle className="text-sm flex items-center gap-2">
                                <BarChart3 className="w-4 h-4 text-orange-600" />
                                Soil Readings
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-orange-700">{summary.total_readings || 0}</p>
                            <p className="text-xs text-gray-500 mt-1">Data points collected</p>
                        </CardContent>
                    </Card>

                    <Card className="border-t-4 border-t-purple-600">
                        <CardHeader className="pb-3">
                            <CardTitle className="text-sm flex items-center gap-2">
                                <TrendingUp className="w-4 h-4 text-purple-600" />
                                Farmers
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-purple-700">{summary.farmers || summary.total_users || 0}</p>
                            <p className="text-xs text-gray-500 mt-1">Registered farmers</p>
                        </CardContent>
                    </Card>
                </div>

                {/* Tabs */}
                <Tabs defaultValue="crops" className="space-y-6">
                    <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
                        <TabsTrigger value="crops">Top Crops</TabsTrigger>
                        <TabsTrigger value="districts">Districts</TabsTrigger>
                        <TabsTrigger value="users">Recent Users</TabsTrigger>
                    </TabsList>

                    {/* Top Crops Tab */}
                    <TabsContent value="crops" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Sprout className="w-5 h-5 text-green-600" />
                                    Most Recommended Crops
                                </CardTitle>
                                <CardDescription>
                                    Top crops recommended by the ML model
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {analytics?.top_crops && analytics.top_crops.length > 0 ? (
                                    analytics.top_crops.map((item: any, index: number) => (
                                        <div key={index} className="space-y-2">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-2">
                                                    <span className="w-6 h-6 bg-green-100 text-green-700 rounded-full flex items-center justify-center text-xs">
                                                        {index + 1}
                                                    </span>
                                                    <span className="text-gray-700">{item.crop}</span>
                                                </div>
                                                <Badge variant="secondary">{item.count} times</Badge>
                                            </div>
                                            <Progress 
                                                value={(item.count / (analytics.top_crops[0]?.count || 1)) * 100} 
                                                className="h-2"
                                            />
                                        </div>
                                    ))
                                ) : (
                                    <div className="text-center py-8 text-gray-500">
                                        <AlertCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                        <p>No crop recommendations yet</p>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* Districts Tab */}
                    <TabsContent value="districts" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <MapPin className="w-5 h-5 text-blue-600" />
                                    Users by District
                                </CardTitle>
                                <CardDescription>
                                    Geographic distribution of farmers
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {analytics?.by_district && analytics.by_district.length > 0 ? (
                                    analytics.by_district.map((item: any, index: number) => (
                                        <div key={index} className="space-y-2">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-2">
                                                    <MapPin className="w-4 h-4 text-blue-600" />
                                                    <span className="text-gray-700">{item.district || 'Unknown'}</span>
                                                </div>
                                                <Badge variant="outline">{item.count} users</Badge>
                                            </div>
                                            <Progress 
                                                value={(item.count / summary.total_users) * 100} 
                                                className="h-2"
                                            />
                                        </div>
                                    ))
                                ) : (
                                    <div className="text-center py-8 text-gray-500">
                                        <AlertCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                        <p>No district data available</p>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* Recent Users Tab */}
                    <TabsContent value="users" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Users className="w-5 h-5 text-purple-600" />
                                    Recent Farmer Registrations
                                </CardTitle>
                                <CardDescription>
                                    Latest farmers who joined the platform
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                {users.length > 0 ? (
                                    <div className="space-y-3">
                                        {users.slice(0, 10).map((farmer: any) => (
                                            <div 
                                                key={farmer.id} 
                                                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                                            >
                                                <div>
                                                    <p className="text-gray-800">{farmer.full_name}</p>
                                                    <p className="text-xs text-gray-500">
                                                        {farmer.district} • {farmer.phone_number || farmer.email}
                                                    </p>
                                                </div>
                                                <Badge variant={farmer.is_active ? 'default' : 'secondary'}>
                                                    {farmer.is_active ? 'Active' : 'Inactive'}
                                                </Badge>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-center py-8 text-gray-500">
                                        <AlertCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                        <p>No users found</p>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>

                {/* Soil Health Summary (if available) */}
                {analytics?.soil_health && analytics.soil_health.length > 0 && (
                    <Card className="mt-6">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Activity className="w-5 h-5 text-orange-600" />
                                Soil Health Distribution
                            </CardTitle>
                            <CardDescription>
                                Overview of soil health status across all readings
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                {analytics.soil_health.map((item: any, index: number) => (
                                    <div key={index} className="p-4 border rounded-lg">
                                        <p className="text-sm text-gray-600 mb-1">{item.status}</p>
                                        <p className="text-gray-800 mb-2">{item.count} readings</p>
                                        <Progress 
                                            value={(item.count / summary.total_readings) * 100} 
                                            className="h-2"
                                        />
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Actions */}
                <Card className="mt-6 border-t-4 border-t-blue-600">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Bell className="w-5 h-5 text-blue-600" />
                            Quick Actions
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="flex flex-wrap gap-3">
                        <Button 
                            variant="outline"
                            onClick={() => toast.info('Notification feature coming soon')}
                        >
                            <Bell className="w-4 h-4 mr-2" />
                            Send Bulk Notification
                        </Button>
                        <Button 
                            variant="outline"
                            onClick={fetchDashboardData}
                        >
                            <Activity className="w-4 h-4 mr-2" />
                            Refresh Data
                        </Button>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}