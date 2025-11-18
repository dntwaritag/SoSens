import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { Users, FileText, TrendingUp, MapPin, Award, Loader2 } from 'lucide-react';
import { getAdminAnalytics } from '../lib/api';
import { toast } from 'sonner@2.0.3';

export function DashboardPage() {
    const [loading, setLoading] = useState(true);
    const [dashboardData, setDashboardData] = useState<any>(null);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            setLoading(true);
            const data = await getAdminAnalytics();
            setDashboardData(data);
        } catch (error) {
            console.error('Failed to load dashboard:', error);
            toast.error('Failed to load analytics data');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <Loader2 className="w-12 h-12 animate-spin text-green-600 mx-auto mb-4" />
                    <p className="text-gray-600">Loading dashboard data...</p>
                </div>
            </div>
        );
    }

    if (!dashboardData) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <p className="text-gray-600">Failed to load dashboard data</p>
            </div>
        );
    }

    const summary = dashboardData.summary || {
        total_users: 0,
        active_users: 0,
        total_readings: 0,
        total_recommendations: 0,
    };

    // Process data from API
    const topCrops = (dashboardData.top_crops || []).map((crop: any, idx: number) => ({
        ...crop,
        percentage: summary.total_recommendations > 0 
            ? ((crop.count / summary.total_recommendations) * 100).toFixed(1)
            : 0
    }));

    const districtData = dashboardData.users_by_district || [];

    const monthlyTrends = [
        { month: 'Jul', predictions: 234, farmers: 98 },
        { month: 'Aug', predictions: 289, farmers: 124 },
        { month: 'Sep', predictions: 356, farmers: 167 },
        { month: 'Oct', predictions: 412, farmers: 198 },
        { month: 'Nov', predictions: 478, farmers: 245 },
    ];

    const COLORS = ['#16a34a', '#15803d', '#166534', '#14532d'];

    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="container mx-auto px-4">
                <div className="mb-8">
                    <h1 className="text-gray-800 mb-2">Analytics Dashboard</h1>
                    <p className="text-gray-600">Monitor system performance and farmer engagement across Rwanda</p>
                </div>

                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <Card className="border-l-4 border-l-green-600">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle>Total Users</CardTitle>
                            <Users className="h-5 w-5 text-green-600" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-gray-900">{summary.total_users.toLocaleString()}</div>
                            <p className="text-xs text-gray-600 mt-1">{summary.farmers || summary.total_users} farmers</p>
                        </CardContent>
                    </Card>

                    <Card className="border-l-4 border-l-blue-600">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle>Active Users</CardTitle>
                            <Users className="h-5 w-5 text-blue-600" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-gray-900">{summary.active_users.toLocaleString()}</div>
                            <p className="text-xs text-gray-600 mt-1">Currently active</p>
                        </CardContent>
                    </Card>

                    <Card className="border-l-4 border-l-purple-600">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle>Soil Readings</CardTitle>
                            <FileText className="h-5 w-5 text-purple-600" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-gray-900">{summary.total_readings.toLocaleString()}</div>
                            <p className="text-xs text-gray-600 mt-1">Total readings</p>
                        </CardContent>
                    </Card>

                    <Card className="border-l-4 border-l-yellow-600">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle>Recommendations</CardTitle>
                            <TrendingUp className="h-5 w-5 text-yellow-600" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-gray-900">{summary.total_recommendations.toLocaleString()}</div>
                            <p className="text-xs text-gray-600 mt-1">Generated by AI</p>
                        </CardContent>
                    </Card>
                </div>

                {/* Charts Section */}
                <Tabs defaultValue="crops" className="space-y-6">
                    <TabsList className="grid w-full grid-cols-2 lg:w-auto">
                        <TabsTrigger value="crops">Top Crops</TabsTrigger>
                        <TabsTrigger value="districts">Districts</TabsTrigger>
                    </TabsList>

                    <TabsContent value="crops" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle>Most Recommended Crops</CardTitle>
                                <CardDescription>Top crops recommended by the AI system</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <ResponsiveContainer width="100%" height={350}>
                                    <BarChart data={topCrops}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="crop" />
                                        <YAxis />
                                        <Tooltip />
                                        <Legend />
                                        <Bar dataKey="count" fill="#16a34a" name="Recommendations" />
                                    </BarChart>
                                </ResponsiveContainer>
                                <div className="mt-6 grid grid-cols-2 md:grid-cols-3 gap-4">
                                    {topCrops.map((crop, idx) => (
                                        <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                            <span className="text-gray-700">{crop.crop}</span>
                                            <span className="text-green-700">{crop.percentage}%</span>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    <TabsContent value="districts" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle>Farmers by District</CardTitle>
                                <CardDescription>Distribution of registered farmers across Rwanda</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <ResponsiveContainer width="100%" height={350}>
                                    <BarChart data={districtData} layout="horizontal">
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis type="number" />
                                        <YAxis dataKey="district" type="category" width={100} />
                                        <Tooltip />
                                        <Legend />
                                        <Bar dataKey="farmers" fill="#2563eb" name="Registered Farmers" />
                                    </BarChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    <TabsContent value="soil" className="space-y-4">
                        <div className="grid md:grid-cols-2 gap-6">
                            <Card>
                                <CardHeader>
                                    <CardTitle>Soil Health Status</CardTitle>
                                    <CardDescription>Distribution of soil health categories</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <ResponsiveContainer width="100%" height={300}>
                                        <PieChart>
                                            <Pie
                                                data={soilHealthData}
                                                cx="50%"
                                                cy="50%"
                                                labelLine={false}
                                                label={({ status, percentage }) => `${status}: ${percentage}%`}
                                                outerRadius={80}
                                                fill="#8884d8"
                                                dataKey="count"
                                            >
                                                {soilHealthData.map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                                ))}
                                            </Pie>
                                            <Tooltip />
                                        </PieChart>
                                    </ResponsiveContainer>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader>
                                    <CardTitle>Soil Health Summary</CardTitle>
                                    <CardDescription>Detailed breakdown of soil conditions</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        {soilHealthData.map((item, idx) => (
                                            <div key={idx} className="space-y-2">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                                                        <span className="text-gray-700">{item.status}</span>
                                                    </div>
                                                    <span className="text-gray-900">{item.count}</span>
                                                </div>
                                                <div className="w-full bg-gray-200 rounded-full h-2">
                                                    <div 
                                                        className="h-2 rounded-full" 
                                                        style={{ 
                                                            width: `${(item.count / summary.total_soil_readings * 100)}%`,
                                                            backgroundColor: item.color 
                                                        }}
                                                    ></div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    </TabsContent>

                    <TabsContent value="trends" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle>Monthly Growth Trends</CardTitle>
                                <CardDescription>Predictions and new farmer registrations over time</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <ResponsiveContainer width="100%" height={350}>
                                    <LineChart data={monthlyTrends}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="month" />
                                        <YAxis />
                                        <Tooltip />
                                        <Legend />
                                        <Line type="monotone" dataKey="predictions" stroke="#16a34a" strokeWidth={2} name="Predictions" />
                                        <Line type="monotone" dataKey="farmers" stroke="#2563eb" strokeWidth={2} name="New Farmers" />
                                    </LineChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>
            </div>
        </div>
    );
}
