import React from 'react';
import { Menu, X, Leaf, LogOut, User } from 'lucide-react';
import { Button } from './ui/button';
import { isAdmin, isFarmer, type User as UserType } from '../lib/auth';

interface NavigationProps {
    currentPage: string;
    onNavigate: (page: string) => void;
    user: UserType | null;
    onLogout: () => void;
}

export function Navigation({ currentPage, onNavigate, user, onLogout }: NavigationProps) {
    const [isMenuOpen, setIsMenuOpen] = React.useState(false);

    // Define navigation items based on user role
    const getNavItems = () => {
        if (!user) {
            // Public navigation
            return [
                { id: 'home', label: 'Home' },
                { id: 'about', label: 'About' },
                { id: 'login', label: 'Login' },
            ];
        }

        if (isAdmin(user)) {
            // Admin navigation
            return [
                { id: 'dashboard', label: 'Analytics Dashboard' },
                { id: 'about', label: 'About' },
            ];
        }

        if (isFarmer(user)) {
            // Farmer navigation
            return [
                { id: 'farmer-dashboard', label: 'My Dashboard' },
                { id: 'predict', label: 'Get Prediction' },
                { id: 'about', label: 'About' },
            ];
        }

        return [];
    };

    const navItems = getNavItems();

    return (
        <nav className="bg-white shadow-md border-b-2 border-green-600">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    {/* Logo/Brand */}
                    <div 
                        className="flex items-center gap-3 cursor-pointer group"
                        onClick={() => onNavigate(user ? (isAdmin(user) ? 'dashboard' : 'farmer-dashboard') : 'home')}
                    >
                        <div className="bg-green-600 p-2 rounded-lg group-hover:bg-green-700 transition-colors">
                            <Leaf className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <span className="text-green-800 block">SoSens</span>
                            <span className="text-gray-500 text-xs">Rwanda</span>
                        </div>
                    </div>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center space-x-1">
                        {navItems.map((item) => (
                            <button
                                key={item.id}
                                onClick={() => onNavigate(item.id)}
                                className={`px-4 py-2 rounded-lg transition-all ${
                                    currentPage === item.id
                                        ? 'bg-green-600 text-white shadow-md'
                                        : 'text-gray-700 hover:bg-green-50 hover:text-green-700'
                                }`}
                            >
                                {item.label}
                            </button>
                        ))}
                        
                        {user && (
                            <div className="flex items-center gap-3 ml-4 pl-4 border-l border-gray-200">
                                <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg">
                                    <User className="w-4 h-4 text-gray-600" />
                                    <div>
                                        <p className="text-xs text-gray-600">{user.role === 'admin' ? 'Admin' : 'Farmer'}</p>
                                        <p className="text-sm text-gray-900">{user.name}</p>
                                    </div>
                                </div>
                                <Button
                                    onClick={onLogout}
                                    variant="outline"
                                    size="sm"
                                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                >
                                    <LogOut className="w-4 h-4 mr-2" />
                                    Logout
                                </Button>
                            </div>
                        )}
                    </div>

                    {/* Mobile menu button */}
                    <div className="md:hidden">
                        <button
                            onClick={() => setIsMenuOpen(!isMenuOpen)}
                            className="text-gray-700 hover:text-green-600 p-2"
                        >
                            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
                        </button>
                    </div>
                </div>

                {/* Mobile Navigation */}
                {isMenuOpen && (
                    <div className="md:hidden pb-4 border-t border-gray-200 mt-2 pt-2">
                        <div className="flex flex-col space-y-1">
                            {navItems.map((item) => (
                                <button
                                    key={item.id}
                                    onClick={() => {
                                        onNavigate(item.id);
                                        setIsMenuOpen(false);
                                    }}
                                    className={`px-4 py-3 rounded-lg text-left transition-all ${
                                        currentPage === item.id
                                            ? 'bg-green-600 text-white shadow-md'
                                            : 'text-gray-700 hover:bg-green-50 hover:text-green-700'
                                    }`}
                                >
                                    {item.label}
                                </button>
                            ))}
                            
                            {user && (
                                <>
                                    <div className="px-4 py-3 bg-gray-100 rounded-lg mt-2">
                                        <p className="text-xs text-gray-600">{user.role === 'admin' ? 'Admin' : 'Farmer'}</p>
                                        <p className="text-sm text-gray-900">{user.name}</p>
                                    </div>
                                    <Button
                                        onClick={() => {
                                            onLogout();
                                            setIsMenuOpen(false);
                                        }}
                                        variant="outline"
                                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                    >
                                        <LogOut className="w-4 h-4 mr-2" />
                                        Logout
                                    </Button>
                                </>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </nav>
    );
}
