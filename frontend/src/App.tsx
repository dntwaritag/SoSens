import React, { useState, useEffect } from 'react';
import { Navigation } from './components/Navigation';
import { HomePage } from './components/HomePage';
import { PredictPage } from './components/PredictPage';
import { AboutPage } from './components/AboutPage';
import { RegisterPage } from './components/RegisterPage';
import { DashboardPage } from './components/DashboardPage';
import { LoginPage } from './components/LoginPage';
import { FarmerDashboard } from './components/FarmerDashboard';
import { AdminDashboard } from './components/AdminDashboard';
import { Toaster } from './components/ui/sonner';
import { getCurrentUser, logout, isAdmin, isFarmer, type User } from './lib/auth';

export default function App() {
    const [currentPage, setCurrentPage] = useState('home');
    const [user, setUser] = useState<User | null>(null);

    useEffect(() => {
        const currentUser = getCurrentUser();
        if (currentUser) {
            setUser(currentUser);
            if (isAdmin(currentUser)) {
                setCurrentPage('dashboard');
            } else if (isFarmer(currentUser)) {
                setCurrentPage('farmer-dashboard');
            }
        }
    }, []);

    const handleNavigate = (page: string) => {
        setCurrentPage(page);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleLogin = (loggedInUser: User) => {
        setUser(loggedInUser);
        if (isAdmin(loggedInUser)) {
            handleNavigate('dashboard');
        } else if (isFarmer(loggedInUser)) {
            handleNavigate('farmer-dashboard');
        }
    };

    const handleLogout = () => {
        logout();
        setUser(null);
        handleNavigate('home');
    };

    const renderPage = () => {
        if (!user) {
            switch (currentPage) {
                case 'home':
                    return <HomePage onNavigate={handleNavigate} />;
                case 'about':
                    return <AboutPage />;
                case 'login':
                    return <LoginPage onLogin={handleLogin} onNavigate={handleNavigate} />;
                case 'register':
                    return <RegisterPage onNavigate={handleNavigate} />;
                default:
                    return <HomePage onNavigate={handleNavigate} />;
            }
        }

        if (isAdmin(user)) {
            switch (currentPage) {
                case 'dashboard':
                    return <AdminDashboard user={user} />;
                case 'about':
                    return <AboutPage />;
                default:
                    return <AdminDashboard user={user} />;
            }
        }

        if (isFarmer(user)) {
            switch (currentPage) {
                case 'farmer-dashboard':
                    return <FarmerDashboard user={user} onNavigate={handleNavigate} />;
                case 'predict':
                    return <PredictPage user={user} />;
                case 'about':
                    return <AboutPage />;
                default:
                    return <FarmerDashboard user={user} onNavigate={handleNavigate} />;
            }
        }

        return <HomePage onNavigate={handleNavigate} />;
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <Navigation 
                currentPage={currentPage} 
                onNavigate={handleNavigate}
                user={user}
                onLogout={handleLogout}
            />
            <main>
                {renderPage()}
            </main>
            <footer className="bg-gray-800 text-white py-8 mt-16">
                <div className="container mx-auto px-4">
                    <div className="grid md:grid-cols-3 gap-8 mb-6">
                        <div>
                            <h3 className="mb-3 text-white">SoSens Rwanda</h3>
                            <p className="text-gray-400">Smart crop recommendations for Rwandan farmers</p>
                        </div>
                        <div>
                            <h4 className="mb-3 text-white">Quick Links</h4>
                            <div className="space-y-2">
                                <button onClick={() => handleNavigate('home')} className="block text-gray-400 hover:text-white">Home</button>
                                <button onClick={() => handleNavigate('about')} className="block text-gray-400 hover:text-white">About</button>
                                {!user && (
                                    <>
                                        <button onClick={() => handleNavigate('login')} className="block text-gray-400 hover:text-white">Login</button>
                                        <button onClick={() => handleNavigate('register')} className="block text-gray-400 hover:text-white">Register</button>
                                    </>
                                )}
                            </div>
                        </div>
                        <div>
                            <h4 className="mb-3 text-white">Contact</h4>
                            <p className="text-gray-400">Email: info@sosens.rw</p>
                            <p className="text-gray-400">Phone: +250 788 000 000</p>
                        </div>
                    </div>
                    <div className="text-center pt-6 border-t border-gray-700">
                        <p className="text-gray-400">2025 Soil Quality Monitoring Project. Built for the farmers of Rwanda.</p>
                    </div>
                </div>
            </footer>
            <Toaster />
        </div>
    );
}
