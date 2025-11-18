    import React, { ReactNode } from 'react';
    import { AlertCircle } from 'lucide-react';

        interface ErrorBoundaryState {
        hasError: boolean;
        error: Error | null;
        }

        interface ErrorBoundaryProps {
        children: ReactNode;
        }

        export class ErrorBoundary extends React.Component<
        ErrorBoundaryProps,
        ErrorBoundaryState
        > {
        constructor(props: ErrorBoundaryProps) {
            super(props);
            this.state = { hasError: false, error: null };
        }

        static getDerivedStateFromError(error: Error): ErrorBoundaryState {
            return { hasError: true, error };
        }

        componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
            console.error('Error caught:', error, errorInfo);
        }

        render() {
            if (this.state.hasError) {
            return (
                <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
                <div className="max-w-md text-center">
                    <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
                    <h2 className="text-gray-800 mb-2">Something went wrong</h2>
                    <p className="text-gray-600 mb-4">{this.state.error?.message}</p>
                    <button
                    onClick={() => window.location.reload()}
                    className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
                    >
                    Reload Page
                    </button>
                </div>
                </div>
            );
            }

            return this.props.children;
        }
        }