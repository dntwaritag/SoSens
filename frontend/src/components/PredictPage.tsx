import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { Switch } from './ui/switch';
import { toast } from 'sonner@2.0.3';
import { Beaker, CloudRain, Sprout, TrendingUp, AlertCircle, CheckCircle2, Cloud } from 'lucide-react';
import { createPrediction, getWeather } from '../lib/api';
import type { User } from '../lib/auth';

interface PredictPageProps {
    user?: User;
}

export function PredictPage({ user }: PredictPageProps) {
    const [formData, setFormData] = useState({
        ph: '6.5',
        nitrogen: '80',
        phosphorus: '60',
        potassium: '140',
        zinc: '3.0',
        sulfur: '12.0',
    });
    
    const [includeWeather, setIncludeWeather] = useState(true);
    const [weatherData, setWeatherData] = useState<any>(null);
    const [prediction, setPrediction] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    // Fetch weather data when component mounts
    useEffect(() => {
        if (user && includeWeather) {
            fetchWeather();
        }
    }, [user, includeWeather]);

    const fetchWeather = async () => {
        try {
            const weather = await getWeather();
            setWeatherData(weather);
        } catch (error) {
            console.log('Weather data not available');
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setPrediction(null);

        try {
            const predictionData = {
                ph: parseFloat(formData.ph),
                nitrogen: parseFloat(formData.nitrogen),
                phosphorus: parseFloat(formData.phosphorus),
                potassium: parseFloat(formData.potassium),
                zinc: parseFloat(formData.zinc),
                sulfur: parseFloat(formData.sulfur),
                include_weather: includeWeather,
            };

            const result = await createPrediction(predictionData);
            
            setPrediction(result);
            
            toast.success('Prediction complete!', {
                description: `We recommend ${result.crop} for your conditions.`
            });
            
        } catch (error) {
            toast.error('Prediction failed', {
                description: error instanceof Error ? error.message : 'Unable to get crop recommendation. Please try again.'
            });
            console.error('Prediction error:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 py-8">
            <div className="container mx-auto px-4">
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-green-600 rounded-full mb-4">
                        <Sprout className="w-8 h-8 text-white" />
                    </div>
                    <h1 className="text-green-800 mb-3">Crop Recommendation System</h1>
                    <p className="text-gray-600 max-w-2xl mx-auto">
                        Enter your soil properties to receive AI-powered crop recommendations with weather-integrated insights.
                    </p>
                </div>

                <div className="max-w-4xl mx-auto space-y-6">
                    {/* Weather Card */}
                    {weatherData && includeWeather && (
                        <Card className="border-t-4 border-t-blue-600 bg-gradient-to-r from-blue-50 to-cyan-50">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Cloud className="w-5 h-5 text-blue-600" />
                                    Current Weather - {weatherData.district}
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div className="text-center p-3 bg-white rounded-lg">
                                        <p className="text-sm text-gray-500">Temperature</p>
                                        <p className="text-blue-700">{weatherData.temperature}°C</p>
                                    </div>
                                    <div className="text-center p-3 bg-white rounded-lg">
                                        <p className="text-sm text-gray-500">Humidity</p>
                                        <p className="text-blue-700">{weatherData.humidity}%</p>
                                    </div>
                                    <div className="text-center p-3 bg-white rounded-lg">
                                        <p className="text-sm text-gray-500">Rainfall</p>
                                        <p className="text-blue-700">{weatherData.rainfall}mm</p>
                                    </div>
                                    <div className="text-center p-3 bg-white rounded-lg">
                                        <p className="text-sm text-gray-500">Condition</p>
                                        <p className="text-blue-700">{weatherData.condition}</p>
                                    </div>
                                </div>
                                {weatherData.advice && (
                                    <p className="mt-4 text-sm text-gray-700 bg-white p-3 rounded-lg">
                                        {weatherData.advice}
                                    </p>
                                )}
                            </CardContent>
                        </Card>
                    )}

                    {/* Soil Input Form */}
                    <form onSubmit={handleSubmit}>
                        <Card className="shadow-lg border-t-4 border-t-green-600">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Beaker className="w-5 h-5 text-green-600" />
                                    Soil Analysis Data
                                </CardTitle>
                                <CardDescription>
                                    Enter the results from your soil test. All measurements should be from the same soil sample.
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="space-y-2">
                                        <Label htmlFor="ph">Soil pH Level</Label>
                                        <Input
                                            id="ph"
                                            name="ph"
                                            type="number"
                                            step="0.1"
                                            value={formData.ph}
                                            onChange={handleChange}
                                            placeholder="5.5 - 8.0"
                                            required
                                        />
                                        <p className="text-xs text-gray-500">Normal range: 5.5 - 7.5</p>
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="nitrogen">Nitrogen (N) kg/ha</Label>
                                        <Input
                                            id="nitrogen"
                                            name="nitrogen"
                                            type="number"
                                            step="0.1"
                                            value={formData.nitrogen}
                                            onChange={handleChange}
                                            placeholder="e.g., 80"
                                            required
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="phosphorus">Phosphorus (P) kg/ha</Label>
                                        <Input
                                            id="phosphorus"
                                            name="phosphorus"
                                            type="number"
                                            step="0.1"
                                            value={formData.phosphorus}
                                            onChange={handleChange}
                                            placeholder="e.g., 60"
                                            required
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="potassium">Potassium (K) kg/ha</Label>
                                        <Input
                                            id="potassium"
                                            name="potassium"
                                            type="number"
                                            step="0.1"
                                            value={formData.potassium}
                                            onChange={handleChange}
                                            placeholder="e.g., 140"
                                            required
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="zinc">Zinc (Zn) mg/kg</Label>
                                        <Input
                                            id="zinc"
                                            name="zinc"
                                            type="number"
                                            step="0.1"
                                            value={formData.zinc}
                                            onChange={handleChange}
                                            placeholder="e.g., 3.0"
                                            required
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="sulfur">Sulfur (S) mg/kg</Label>
                                        <Input
                                            id="sulfur"
                                            name="sulfur"
                                            type="number"
                                            step="0.1"
                                            value={formData.sulfur}
                                            onChange={handleChange}
                                            placeholder="e.g., 12.0"
                                            required
                                        />
                                    </div>
                                </div>

                                <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                                    <div className="flex items-center gap-3">
                                        <CloudRain className="w-5 h-5 text-blue-600" />
                                        <div>
                                            <p className="text-gray-700">Include Weather Data</p>
                                            <p className="text-xs text-gray-500">Get weather-integrated recommendations</p>
                                        </div>
                                    </div>
                                    <Switch
                                        checked={includeWeather}
                                        onCheckedChange={setIncludeWeather}
                                    />
                                </div>

                                <Button 
                                    type="submit" 
                                    size="lg"
                                    className="w-full bg-green-600 hover:bg-green-700"
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <>
                                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                            Analyzing Data...
                                        </>
                                    ) : (
                                        <>
                                            <TrendingUp className="w-4 h-4 mr-2" />
                                            Get Crop Recommendation
                                        </>
                                    )}
                                </Button>
                            </CardContent>
                        </Card>
                    </form>

                    {/* Results Section */}
                    {prediction && (
                        <Card className="shadow-xl border-t-4 border-t-green-600 animate-fade-in">
                            <CardHeader className="bg-green-50">
                                <CardTitle className="flex items-center gap-2 text-green-800">
                                    <CheckCircle2 className="w-6 h-6" />
                                    Recommendation Result
                                </CardTitle>
                                <CardDescription>Based on your soil and weather data analysis</CardDescription>
                            </CardHeader>
                            <CardContent className="pt-6 space-y-8">
                                {/* Main Recommendation */}
                                <div className="text-center">
                                    <h2 className="text-green-700 mb-4">
                                        Recommended Crop: {prediction.crop}
                                    </h2>
                                    <div className="max-w-md mx-auto">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-gray-600">Confidence Score</span>
                                            <span className="text-green-700">{Math.round(prediction.confidence * 100)}%</span>
                                        </div>
                                        <Progress value={prediction.confidence * 100} className="h-3" />
                                    </div>
                                </div>

                                {/* Alternative Crops */}
                                {prediction.alternatives && prediction.alternatives.length > 0 && (
                                    <div className="p-4 bg-gray-50 rounded-lg">
                                        <h4 className="text-gray-800 mb-3">Alternative Crops</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                            {prediction.alternatives.map((alt: any, idx: number) => (
                                                <div key={idx} className="flex items-center justify-between p-3 bg-white rounded-lg border">
                                                    <span className="text-gray-700">{alt.crop}</span>
                                                    <Badge variant="outline">{Math.round(alt.confidence * 100)}%</Badge>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Soil Health */}
                                <div>
                                    <h4 className="text-gray-800 mb-3">Soil Health Status</h4>
                                    <div className={`p-4 rounded-lg ${
                                        prediction.soil_health === 'Optimal' 
                                            ? 'bg-green-50 border border-green-200' 
                                            : prediction.soil_health === 'Moderate'
                                            ? 'bg-yellow-50 border border-yellow-200'
                                            : 'bg-red-50 border border-red-200'
                                    }`}>
                                        <div className="flex items-center gap-2">
                                            {prediction.soil_health === 'Optimal' ? (
                                                <CheckCircle2 className="w-5 h-5 text-green-600" />
                                            ) : (
                                                <AlertCircle className="w-5 h-5 text-yellow-600" />
                                            )}
                                            <span className={
                                                prediction.soil_health === 'Optimal' 
                                                    ? 'text-green-800' 
                                                    : 'text-yellow-800'
                                            }>
                                                {prediction.soil_health}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {/* Recommendations */}
                                <div className="space-y-4">
                                    <div>
                                        <h4 className="text-gray-800 mb-2 flex items-center gap-2">
                                            <Beaker className="w-5 h-5 text-green-600" />
                                            Fertilizer Recommendation
                                        </h4>
                                        <p className="text-gray-700 bg-gray-50 p-4 rounded-lg">
                                            {prediction.fertilizer_advice}
                                        </p>
                                    </div>

                                    <div>
                                        <h4 className="text-gray-800 mb-2 flex items-center gap-2">
                                            <CloudRain className="w-5 h-5 text-blue-600" />
                                            Planting Season
                                        </h4>
                                        <p className="text-gray-700 bg-gray-50 p-4 rounded-lg">
                                            {prediction.planting_season}
                                        </p>
                                    </div>

                                    {prediction.weather_advice && (
                                        <div>
                                            <h4 className="text-gray-800 mb-2 flex items-center gap-2">
                                                <Cloud className="w-5 h-5 text-blue-600" />
                                                Weather Advice
                                            </h4>
                                            <p className="text-gray-700 bg-blue-50 p-4 rounded-lg border border-blue-200">
                                                {prediction.weather_advice}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    );
}
