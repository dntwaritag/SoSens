import React, { useState } from 'react';
import { Navigation } from './components/Navigation';
import { HomePage } from './components/HomePage';
import { PredictPage } from './components/PredictPage';
import { AboutPage } from './components/AboutPage';

export default function App() {
    const [currentPage, setCurrentPage] = useState('home');

    const handleNavigate = (page: string) => {
        setCurrentPage(page);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const renderPage = () => {
        switch (currentPage) {
            case 'home':
                return <HomePage onNavigate={handleNavigate} />;
            case 'predict':
                return <PredictPage />;
            case 'about':
                return <AboutPage />;
            default:
                return <HomePage onNavigate={handleNavigate} />;
        }
    };

    return (
        <div className="min-h-screen">
            <Navigation currentPage={currentPage} onNavigate={handleNavigate} />
            <main>
                {renderPage()}
            </main>
            <footer className="bg-gray-800 text-white py-6">
                <div className="container mx-auto px-4 text-center">
                    <p>&copy; 2025 Soil Quality Monitoring Project. Built for the farmers of Rwanda.</p>
                </div>
            </footer>
        </div>
    );
}
