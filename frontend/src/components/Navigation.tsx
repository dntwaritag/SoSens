import React from 'react';
import { Menu, X } from 'lucide-react';

interface NavigationProps {
    currentPage: string;
    onNavigate: (page: string) => void;
}

export function Navigation({ currentPage, onNavigate }: NavigationProps) {
    const [isMenuOpen, setIsMenuOpen] = React.useState(false);

    const navItems = [
        { id: 'home', label: 'Home' },
        { id: 'predict', label: 'Get Prediction' },
        { id: 'about', label: 'About' },
    ];

    return (
        <nav className="bg-green-700 shadow-lg">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    {/* Logo/Brand */}
                    <div 
                        className="text-white cursor-pointer"
                        onClick={() => onNavigate('home')}
                    >
                        <span className="flex items-center gap-2">
                            <span className="text-2xl">🌾</span>
                            <span>SoSens</span>
                        </span>
                    </div>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex space-x-8">
                        {navItems.map((item) => (
                            <button
                                key={item.id}
                                onClick={() => onNavigate(item.id)}
                                className={`px-3 py-2 rounded-md transition-colors ${
                                    currentPage === item.id
                                        ? 'bg-green-800 text-white'
                                        : 'text-green-100 hover:bg-green-600 hover:text-white'
                                }`}
                            >
                                {item.label}
                            </button>
                        ))}
                    </div>

                    {/* Mobile menu button */}
                    <div className="md:hidden">
                        <button
                            onClick={() => setIsMenuOpen(!isMenuOpen)}
                            className="text-green-100 hover:text-white p-2"
                        >
                            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
                        </button>
                    </div>
                </div>

                {/* Mobile Navigation */}
                {isMenuOpen && (
                    <div className="md:hidden pb-4">
                        <div className="flex flex-col space-y-2">
                            {navItems.map((item) => (
                                <button
                                    key={item.id}
                                    onClick={() => {
                                        onNavigate(item.id);
                                        setIsMenuOpen(false);
                                    }}
                                    className={`px-3 py-2 rounded-md text-left transition-colors ${
                                        currentPage === item.id
                                            ? 'bg-green-800 text-white'
                                            : 'text-green-100 hover:bg-green-600 hover:text-white'
                                    }`}
                                >
                                    {item.label}
                                </button>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </nav>
    );
}
