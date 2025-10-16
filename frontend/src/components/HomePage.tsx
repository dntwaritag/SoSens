import React from 'react';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { Sprout, CloudRain, Beaker, TrendingUp } from 'lucide-react';

interface HomePageProps {
    onNavigate: (page: string) => void;
}

export function HomePage({ onNavigate }: HomePageProps) {
    const features = [
        {
            icon: <Beaker className="w-12 h-12 text-green-600" />,
            title: 'Soil Analysis',
            description: 'Comprehensive soil testing including pH, nutrients, and mineral content for optimal crop selection.',
        },
        {
            icon: <CloudRain className="w-12 h-12 text-green-600" />,
            title: 'Weather Integration',
            description: 'Seasonal weather data analysis to match crops with your local climate patterns.',
        },
        {
            icon: <TrendingUp className="w-12 h-12 text-green-600" />,
            title: 'AI-Powered Predictions',
            description: 'Advanced machine learning models trained on Rwanda agricultural data for accurate recommendations.',
        },
        {
            icon: <Sprout className="w-12 h-12 text-green-600" />,
            title: 'Crop Optimization',
            description: 'Get recommendations for Maize, Wheat, Beans, Potatoes, Cassava, Sorghum and more.',
        },
    ];

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Hero Section */}
            <section className="relative bg-green-700 text-white py-20">
                <div className="absolute inset-0 opacity-20">
                    <ImageWithFallback 
                        src="https://images.unsplash.com/photo-1739440426767-960f31dada38?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxyd2FuZGElMjBmYXJtZXIlMjBhZ3JpY3VsdHVyZXxlbnwxfHx8fDE3NjA0MzYyNTN8MA&ixlib=rb-4.1.0&q=80&w=1080"
                        alt="Rwanda Agriculture"
                        className="w-full h-full object-cover"
                    />
                </div>
                <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
                    <div className="max-w-3xl mx-auto text-center">
                        <h1 className="mb-6 text-white">
                            Rwanda Crop Recommendation System
                        </h1>
                        <p className="mb-8">
                            Empowering Rwandan farmers with AI-driven crop recommendations based on soil quality and weather patterns. Make informed decisions for better yields and sustainable farming.
                        </p>
                        <button
                            onClick={() => onNavigate('predict')}
                            className="bg-white text-green-700 px-8 py-3 rounded-lg hover:bg-green-50 transition-colors shadow-lg"
                        >
                            Get Your Recommendation
                        </button>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="py-16 bg-white">
                <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-12">
                        <h2 className="mb-4">How It Works</h2>
                        <p className="text-gray-600 max-w-2xl mx-auto">
                            Our system combines soil analysis, weather data, and machine learning to provide personalized crop recommendations for your farm.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                        {features.map((feature, index) => (
                            <div
                                key={index}
                                className="p-6 bg-gray-50 rounded-xl hover:shadow-lg transition-shadow"
                            >
                                <div className="flex justify-center mb-4">
                                    {feature.icon}
                                </div>
                                <h3 className="text-center mb-3">{feature.title}</h3>
                                <p className="text-gray-600 text-center">
                                    {feature.description}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-16 bg-green-50">
                <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-lg p-8 md:p-12">
                        <div className="grid md:grid-cols-2 gap-8 items-center">
                            <div>
                                <h2 className="mb-4">Ready to Get Started?</h2>
                                <p className="text-gray-600 mb-6">
                                    Input your soil and weather data to receive personalized crop recommendations powered by AI. Our system analyzes multiple factors to ensure you plant the right crop for your conditions.
                                </p>
                                <button
                                    onClick={() => onNavigate('predict')}
                                    className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors"
                                >
                                    Start Prediction
                                </button>
                            </div>
                            <div className="rounded-lg overflow-hidden shadow-md">
                                <ImageWithFallback
                                    src="https://images.unsplash.com/photo-1710090720809-527cefdac598?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzb2lsJTIwdGVzdGluZyUyMGFncmljdWx0dXJlfGVufDF8fHx8MTc2MDM1NDIzMHww&ixlib=rb-4.1.0&q=80&w=1080"
                                    alt="Soil Testing"
                                    className="w-full h-64 object-cover"
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Stats Section */}
            <section className="py-16 bg-white">
                <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
                        <div className="p-6">
                            <div className="text-green-700 mb-2">6+</div>
                            <p className="text-gray-600">Supported Crops</p>
                        </div>
                        <div className="p-6">
                            <div className="text-green-700 mb-2">95%+</div>
                            <p className="text-gray-600">Prediction Accuracy</p>
                        </div>
                        <div className="p-6">
                            <div className="text-green-700 mb-2">19</div>
                            <p className="text-gray-600">Data Points Analyzed</p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}
