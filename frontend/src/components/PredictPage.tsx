import React, { useState } from 'react';

// Helper component for a consistent input field
const InputField = ({ label, name, value, onChange, type = 'number', placeholder, step = "0.01" }) => (
    <div className="w-full">
        <label htmlFor={name} className="block mb-1">{label}</label>
        <input
            type={type}
            id={name}
            name={name}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            step={step}
            className="w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition duration-300"
        />
    </div>
);

// Helper component for a section header
const SectionHeader = ({ title }) => (
    <h3 className="border-b-2 border-green-200 pb-2 mb-4">{title}</h3>
);

export function PredictPage() {
    const [formData, setFormData] = useState({
        Ph: '6.5',
        K: '140',
        P: '60',
        N: '80',
        Zn: '3.0',
        S: '12.0',
        Soilcolor: 'brown',
        'T2M_MAX-W': '25',
        'T2M_MIN-W': '5',
        'PRECTOTCORR-W': '2.5',
        'T2M_MAX-Sp': '28',
        'T2M_MIN-Sp': '10',
        'PRECTOTCORR-Sp': '5.0',
        'T2M_MAX-Su': '24',
        'T2M_MIN-Su': '12',
        'PRECTOTCORR-Su': '12.0',
        'T2M_MAX-Au': '23',
        'T2M_MIN-Au': '6',
        'PRECTOTCORR-Au': '4.0',
    });
    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setPrediction(null);

        // Basic validation
        for (const key in formData) {
            if (formData[key] === '') {
                setError('Please fill out all fields.');
                setLoading(false);
                return;
            }
        }
        
        // Mock API call to the backend
        setTimeout(() => {
            const crops = ['Maize', 'Wheat', 'Beans', 'Potatoes', 'Cassava', 'Sorghum'];
            const randomCrop = crops[Math.floor(Math.random() * crops.length)];
            setPrediction({
                crop: randomCrop,
                confidence: (Math.random() * (0.98 - 0.85) + 0.85).toFixed(2),
            });
            setLoading(false);
        }, 2000);
    };

    return (
        <div className="min-h-screen bg-gray-50 font-sans text-gray-900 py-8">
            <div className="container mx-auto p-4 sm:p-6 md:p-8">
                <header className="text-center mb-8">
                    <h1 className="text-green-700">Get Your Crop Recommendation</h1>
                    <p className="text-gray-600 mt-2">Enter your soil and weather data below to receive a personalized crop recommendation.</p>
                </header>

                <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-lg p-6 sm:p-8">
                    <form onSubmit={handleSubmit}>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
                            {/* Soil Properties Section */}
                            <div className="md:col-span-2">
                                <SectionHeader title="Soil Properties" />
                            </div>
                            <InputField label="Soil pH" name="Ph" value={formData.Ph} onChange={handleChange} placeholder="e.g., 5.8" />
                            <InputField label="Potassium (K) (mg/kg)" name="K" value={formData.K} onChange={handleChange} placeholder="e.g., 738.23" />
                            <InputField label="Phosphorus (P) (mg/kg)" name="P" value={formData.P} onChange={handleChange} placeholder="e.g., 5.40" />
                            <InputField label="Nitrogen (N) (%)" name="N" value={formData.N} onChange={handleChange} placeholder="e.g., 0.23" />
                            <InputField label="Zinc (Zn) (mg/kg)" name="Zn" value={formData.Zn} onChange={handleChange} placeholder="e.g., 2.97" />
                            <InputField label="Sulphur (S) (mg/kg)" name="S" value={formData.S} onChange={handleChange} placeholder="e.g., 13.81" />
                            <div>
                                <label htmlFor="Soilcolor" className="block mb-1">Soil Color</label>
                                <select 
                                    id="Soilcolor" 
                                    name="Soilcolor" 
                                    value={formData.Soilcolor} 
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                                >
                                    <option value="brown">Brown</option>
                                    <option value="black">Black</option>
                                    <option value="Yellowish brown">Yellowish Brown</option>
                                    <option value="red">Red</option>
                                </select>
                            </div>

                             {/* Weather Data Section */}
                            <div className="md:col-span-2 mt-6">
                                <SectionHeader title="Seasonal Weather Data" />
                            </div>

                            {['W', 'Sp', 'Su', 'Au'].map(season => {
                                const seasonName = {W: 'Winter', Sp: 'Spring', Su: 'Summer', Au: 'Autumn'}[season];
                                return (
                                    <div key={season} className="md:col-span-2 grid grid-cols-1 sm:grid-cols-3 gap-x-6 gap-y-4 p-4 border rounded-lg bg-green-50/50">
                                        <h4 className="sm:col-span-3 text-green-800">{seasonName}</h4>
                                        <InputField label={`Max Temp (°C)`} name={`T2M_MAX-${season}`} value={formData[`T2M_MAX-${season}`]} onChange={handleChange} placeholder="e.g., 26.8" />
                                        <InputField label={`Min Temp (°C)`} name={`T2M_MIN-${season}`} value={formData[`T2M_MIN-${season}`]} onChange={handleChange} placeholder="e.g., 5.4" />
                                        <InputField label={`Precipitation (mm)`} name={`PRECTOTCORR-${season}`} value={formData[`PRECTOTCORR-${season}`]} onChange={handleChange} placeholder="e.g., 2.1" />
                                    </div>
                                );
                            })}
                        </div>
                        
                        <div className="mt-8 text-center">
                            <button 
                                type="submit"
                                className="w-full sm:w-auto bg-green-600 text-white py-3 px-12 rounded-lg shadow-md hover:bg-green-700 disabled:bg-gray-400 transition-transform transform hover:scale-105 duration-300"
                                disabled={loading}
                            >
                                {loading ? 'Analyzing...' : 'Get Recommendation'}
                            </button>
                        </div>
                    </form>

                    {error && <div className="mt-6 p-4 bg-red-100 text-red-700 rounded-lg text-center">{error}</div>}

                    {loading && (
                         <div className="mt-8 text-center">
                            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-4 border-green-600"></div>
                            <p className="text-gray-600 mt-2">Our AI is analyzing your data...</p>
                        </div>
                    )}

                    {prediction && (
                        <div className="mt-8 p-6 bg-green-100 border-l-4 border-green-500 rounded-r-lg shadow-lg animate-fade-in">
                            <h3 className="text-gray-800">Recommendation Result</h3>
                            <div className="mt-4 text-center">
                                <p className="text-gray-700">The most suitable crop for your conditions is:</p>
                                <p className="text-green-700 my-3">{prediction.crop}</p>
                                <div className="w-full bg-gray-200 rounded-full h-4 mt-4">
                                    <div className="bg-green-500 h-4 rounded-full" style={{ width: `${prediction.confidence * 100}%` }}></div>
                                </div>
                                <p className="text-gray-600 mt-2">Confidence: {Math.round(prediction.confidence * 100)}%</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
