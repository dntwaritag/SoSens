import React from 'react';
import { Target, Users, Globe, Award } from 'lucide-react';

export function AboutPage() {
    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <section className="bg-green-700 text-white py-16">
                <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="max-w-3xl mx-auto text-center">
                        <h1 className="mb-4 text-white">About Our Project</h1>
                        <p>
                            Transforming agriculture in Rwanda through technology and data-driven insights.
                        </p>
                    </div>
                </div>
            </section>

            {/* Mission Section */}
            <section className="py-16 bg-white">
                <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="max-w-4xl mx-auto">
                        <div className="text-center mb-12">
                            <h2 className="mb-4">Our Mission</h2>
                            <p className="text-gray-600">
                                We are dedicated to empowering Rwandan farmers with intelligent, data-driven crop recommendations that improve yields, reduce risks, and promote sustainable agricultural practices.
                            </p>
                        </div>

                        <div className="grid md:grid-cols-2 gap-8 mt-12">
                            <div className="p-6 bg-green-50 rounded-xl">
                                <div className="flex items-start gap-4">
                                    <Target className="w-8 h-8 text-green-600 flex-shrink-0" />
                                    <div>
                                        <h3 className="mb-2">Our Goal</h3>
                                        <p className="text-gray-600">
                                            To provide accessible, accurate crop recommendations to every farmer in Rwanda, regardless of their location or resources, helping them make informed decisions for better harvests.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <div className="p-6 bg-green-50 rounded-xl">
                                <div className="flex items-start gap-4">
                                    <Globe className="w-8 h-8 text-green-600 flex-shrink-0" />
                                    <div>
                                        <h3 className="mb-2">Our Impact</h3>
                                        <p className="text-gray-600">
                                            By combining soil analysis, seasonal weather patterns, and machine learning, we help farmers optimize their crop selection, leading to increased productivity and food security.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Project Info */}
            <section className="py-16 bg-gray-50">
                <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="max-w-4xl mx-auto">
                        <h2 className="text-center mb-12">The Technology Behind the System</h2>
                        
                        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
                            <h3 className="mb-4">Soil Quality Monitoring</h3>
                            <p className="text-gray-600 mb-4">
                                Our system analyzes key soil parameters including pH levels, nutrient content (Nitrogen, Phosphorus, Potassium), and essential minerals (Zinc, Sulphur). These measurements are crucial for determining which crops will thrive in specific soil conditions.
                            </p>
                            <div className="grid md:grid-cols-3 gap-4 mt-6">
                                <div className="p-4 bg-green-50 rounded-lg">
                                    <p className="text-green-700 mb-1">pH Balance</p>
                                    <p className="text-gray-600">Soil acidity measurement</p>
                                </div>
                                <div className="p-4 bg-green-50 rounded-lg">
                                    <p className="text-green-700 mb-1">NPK Analysis</p>
                                    <p className="text-gray-600">Essential nutrients</p>
                                </div>
                                <div className="p-4 bg-green-50 rounded-lg">
                                    <p className="text-green-700 mb-1">Mineral Content</p>
                                    <p className="text-gray-600">Zinc & Sulphur levels</p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-xl shadow-lg p-8">
                            <h3 className="mb-4">Weather Pattern Analysis</h3>
                            <p className="text-gray-600 mb-4">
                                We integrate seasonal weather data including maximum and minimum temperatures, as well as precipitation patterns across all four seasons. This comprehensive climate analysis ensures crop recommendations are suited to your local weather conditions.
                            </p>
                            <div className="grid md:grid-cols-4 gap-4 mt-6">
                                {['Winter', 'Spring', 'Summer', 'Autumn'].map((season) => (
                                    <div key={season} className="p-4 bg-blue-50 rounded-lg text-center">
                                        <p className="text-blue-700">{season}</p>
                                        <p className="text-gray-600">Temp & Rain</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Values Section */}
            <section className="py-16 bg-white">
                <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="max-w-4xl mx-auto">
                        <h2 className="text-center mb-12">Our Values</h2>
                        
                        <div className="grid md:grid-cols-3 gap-8">
                            <div className="text-center">
                                <div className="flex justify-center mb-4">
                                    <Award className="w-12 h-12 text-green-600" />
                                </div>
                                <h3 className="mb-3">Accuracy</h3>
                                <p className="text-gray-600">
                                    We are committed to providing the most accurate and reliable crop recommendations based on scientific data and proven methodologies.
                                </p>
                            </div>

                            <div className="text-center">
                                <div className="flex justify-center mb-4">
                                    <Users className="w-12 h-12 text-green-600" />
                                </div>
                                <h3 className="mb-3">Accessibility</h3>
                                <p className="text-gray-600">
                                    Our platform is designed to be user-friendly and accessible to farmers of all backgrounds and technical skill levels.
                                </p>
                            </div>

                            <div className="text-center">
                                <div className="flex justify-center mb-4">
                                    <Globe className="w-12 h-12 text-green-600" />
                                </div>
                                <h3 className="mb-3">Sustainability</h3>
                                <p className="text-gray-600">
                                    We promote sustainable farming practices that protect the environment while maximizing agricultural productivity.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Contact/Footer Info */}
            <section className="py-12 bg-green-700 text-white">
                <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="max-w-2xl mx-auto text-center">
                        <h3 className="mb-4 text-white">Soil Quality Monitoring Project</h3>
                        <p className="mb-4">
                            Built for the farmers of Rwanda with a commitment to improving agricultural outcomes through technology and innovation.
                        </p>
                        <p className="text-green-200">
                            {/* © 2025 All rights reserved. */}
                        </p>
                    </div>
                </div>
            </section>
        </div>
    );
}
