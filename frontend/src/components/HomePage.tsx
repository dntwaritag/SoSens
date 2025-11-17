import React from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Sprout, CloudRain, Beaker, TrendingUp } from 'lucide-react';

interface HomePageProps {
    onNavigate: (page: string) => void;
}

export function HomePage({ onNavigate }: HomePageProps) {
    const features = [
        {
            icon: <Beaker className="w-10 h-10 text-green-600" />,
            title: 'Soil Analysis',
            description: 'Comprehensive soil testing for optimal crop selection',
        },
        {
            icon: <CloudRain className="w-10 h-10 text-green-600" />,
            title: 'Weather Data',
            description: 'Seasonal weather analysis for crop matching',
        },
        {
            icon: <TrendingUp className="w-10 h-10 text-green-600" />,
            title: 'AI Predictions',
            description: 'Machine learning powered recommendations',
        },
        {
            icon: <Sprout className="w-10 h-10 text-green-600" />,
            title: 'Crop Selection',
            description: 'Optimized recommendations for Rwandan agriculture',
        },
    ];

    return (
        <div className="min-h-screen bg-gray-50">
            <section className="bg-green-600 text-white py-20">
                <div className="container mx-auto px-4">
                    <div className="max-w-3xl mx-auto text-center">
                        <h1 className="mb-6 text-white">
                            Rwanda Crop Recommendation System
                        </h1>
                        <p className="mb-8 text-lg text-green-50">
                            AI-driven crop recommendations based on soil quality and weather patterns for Rwandan farmers.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <Button
                                onClick={() => onNavigate('register')}
                                size="lg"
                                className="bg-white text-green-700 hover:bg-green-50"
                            >
                                Register
                            </Button>
                            <Button
                                onClick={() => onNavigate('login')}
                                size="lg"
                                variant="outline"
                                className="border-white text-white hover:bg-green-700"
                            >
                                Login
                            </Button>
                        </div>
                    </div>
                </div>
            </section>

            <section className="py-16 bg-white">
                <div className="container mx-auto px-4">
                    <div className="text-center mb-12">
                        <h2 className="mb-4 text-gray-800">System Features</h2>
                        <p className="text-gray-600 max-w-2xl mx-auto">
                            Combining soil analysis, weather data, and machine learning for accurate crop recommendations.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                        {features.map((feature, index) => (
                            <Card key={index}>
                                <CardContent className="pt-6">
                                    <div className="flex justify-center mb-4">
                                        {feature.icon}
                                    </div>
                                    <h3 className="text-center mb-3 text-gray-800">{feature.title}</h3>
                                    <p className="text-gray-600 text-center text-sm">
                                        {feature.description}
                                    </p>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>
            </section>

            <section className="py-16 bg-gray-50">
                <div className="container mx-auto px-4">
                    <Card className="max-w-4xl mx-auto">
                        <CardContent className="p-8 md:p-12">
                            <div className="text-center">
                                <h2 className="mb-4 text-gray-800">Get Started</h2>
                                <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
                                    Register for an account to access personalized crop recommendations based on your soil and weather conditions.
                                </p>
                                <div className="flex gap-4 justify-center">
                                    <Button
                                        onClick={() => onNavigate('register')}
                                        size="lg"
                                        className="bg-green-600 hover:bg-green-700"
                                    >
                                        Create Account
                                    </Button>
                                    <Button
                                        onClick={() => onNavigate('about')}
                                        size="lg"
                                        variant="outline"
                                    >
                                        Learn More
                                    </Button>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </section>

            <section className="py-12 bg-white">
                <div className="container mx-auto px-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center max-w-3xl mx-auto">
                        <div>
                            <div className="text-green-700 mb-2">6+</div>
                            <p className="text-gray-600 text-sm">Supported Crops</p>
                        </div>
                        <div>
                            <div className="text-green-700 mb-2">95%</div>
                            <p className="text-gray-600 text-sm">Prediction Accuracy</p>
                        </div>
                        <div>
                            <div className="text-green-700 mb-2">19</div>
                            <p className="text-gray-600 text-sm">Data Points</p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}
