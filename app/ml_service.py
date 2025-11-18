"""
ML Service for crop prediction
"""

import joblib
import json
import os
import numpy as np
from typing import Dict, Optional
from config import settings

class MLService:
    def __init__(self):
        """Initialize ML models"""
        self.model = None
        self.scaler = None
        self.encoder = None
        self.feature_names = None
        self.metadata = None
        
        self._load_models()
    
    def _load_models(self):
        """Load all ML models and preprocessors"""
        try:
            # Check if model files exist
            if os.path.exists(settings.MODEL_PATH):
                self.model = joblib.load(settings.MODEL_PATH)
                print(f" ML Model loaded from {settings.MODEL_PATH}")
            else:
                print(f" Model file not found: {settings.MODEL_PATH}")
            
            if os.path.exists(settings.SCALER_PATH):
                self.scaler = joblib.load(settings.SCALER_PATH)
                print(f" Scaler loaded")
            
            if os.path.exists(settings.ENCODER_PATH):
                self.encoder = joblib.load(settings.ENCODER_PATH)
                print(f" Encoder loaded")
            
            if os.path.exists(settings.FEATURES_PATH):
                self.feature_names = joblib.load(settings.FEATURES_PATH)
                print(f" Feature names loaded")
            
            if os.path.exists(settings.METADATA_PATH):
                with open(settings.METADATA_PATH, 'r') as f:
                    self.metadata = json.load(f)
                print(f" Metadata loaded")
                
        except Exception as e:
            print(f" Error loading ML models: {e}")
            print("Using fallback prediction mode")
    
    def predict(self, soil_data: Dict) -> Dict:
        """
        Make crop prediction based on soil data
        
        Args:
            soil_data: Dictionary with Ph, N, P, K, Zn, S
        
        Returns:
            Dictionary with prediction results
        """
        try:
            # If models not loaded, use fallback
            if self.model is None:
                return self._fallback_prediction(soil_data)
            
            # Prepare features
            features = self._prepare_features(soil_data)
            
            # Scale features
            if self.scaler:
                features_scaled = self.scaler.transform([features])
            else:
                features_scaled = [features]
            
            # Make prediction
            prediction = self.model.predict(features_scaled)[0]
            
            # Get confidence (probability)
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(features_scaled)[0]
                confidence = float(np.max(probabilities))
                
                # Get alternatives
                top_3_indices = np.argsort(probabilities)[-3:][::-1]
                alternatives = []
                for idx in top_3_indices[1:]:  # Skip first (main prediction)
                    crop_name = self.encoder.inverse_transform([idx])[0] if self.encoder else f"Crop_{idx}"
                    alternatives.append({
                        'crop': crop_name,
                        'confidence': float(probabilities[idx])
                    })
            else:
                confidence = 0.85
                alternatives = []
            
            # Decode crop name
            if self.encoder:
                crop_name = self.encoder.inverse_transform([prediction])[0]
            else:
                crop_name = str(prediction)
            
            # Assess soil health
            soil_health = self._assess_soil_health(soil_data)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(crop_name, soil_data)
            
            return {
                'success': True,
                'prediction': {
                    'crop': crop_name,
                    'confidence': confidence
                },
                'soil_health': soil_health,
                'recommendations': recommendations,
                'alternatives': alternatives
            }
            
        except Exception as e:
            print(f" Prediction error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _prepare_features(self, soil_data: Dict) -> list:
        """Prepare features in correct order"""
        # Default environmental values for Rwanda
        defaults = {
            'Ph': soil_data.get('Ph', 6.5),
            'N': soil_data.get('N', 40),
            'P': soil_data.get('P', 20),
            'K': soil_data.get('K', 200),
            'Zn': soil_data.get('Zn', 5.0),
            'S': soil_data.get('S', 15.0)
        }
        
        if self.feature_names:
            return [defaults.get(f, 0) for f in self.feature_names]
        else:
            return [defaults['Ph'], defaults['N'], defaults['P'], 
                    defaults['K'], defaults['Zn'], defaults['S']]
    
    def _assess_soil_health(self, soil_data: Dict) -> Dict:
        """Assess soil health status"""
        ph = soil_data.get('Ph', 6.5)
        n = soil_data.get('N', 40)
        p = soil_data.get('P', 20)
        k = soil_data.get('K', 200)
        
        issues = []
        
        # pH check
        if ph < 5.5:
            issues.append("Soil is too acidic - apply lime")
        elif ph > 7.5:
            issues.append("Soil is too alkaline - add organic matter")
        
        # Nitrogen check
        if n < 20:
            issues.append("Low nitrogen - apply urea or manure")
        elif n > 80:
            issues.append("Excessive nitrogen - reduce fertilizer")
        
        # Phosphorus check
        if p < 10:
            issues.append("Low phosphorus - apply DAP")
        
        # Potassium check
        if k < 100:
            issues.append("Low potassium - apply potash")
        
        # Overall status
        if len(issues) >= 3:
            status = "Poor"
        elif len(issues) >= 1:
            status = "Fair"
        else:
            status = "Good"
        
        return {
            'status': status,
            'issues': issues
        }
    
    def _generate_recommendations(self, crop: str, soil_data: Dict) -> Dict:
        """Generate farming recommendations"""
        
        # Rwanda planting seasons
        season_map = {
            'Beans': 'Season A (Sep-Dec) & Season B (Feb-May)',
            'Maize': 'Season A (Sep-Dec) & Season B (Feb-May)',
            'Cassava': 'Year-round planting possible',
            'Potato': 'Season B (Feb-May) in highland areas',
            'Rice': 'Season A (Sep-Dec) in wetlands',
            'Wheat': 'Season B (Feb-May) in highland areas'
        }
        
        # Fertilizer recommendations
        fertilizer = self._calculate_fertilizer(crop, soil_data)
        
        return {
            'fertilizer': fertilizer,
            'planting_season': season_map.get(crop, 'Consult local agricultural officer'),
            'spacing': 'Standard spacing for crop type'
        }
    
    def _calculate_fertilizer(self, crop: str, soil_data: Dict) -> str:
        """Calculate fertilizer needs"""
        n = soil_data.get('N', 40)
        p = soil_data.get('P', 20)
        k = soil_data.get('K', 200)
        
        recommendations = []
        
        if n < 40:
            recommendations.append("50kg Urea per hectare")
        if p < 20:
            recommendations.append("50kg DAP per hectare")
        if k < 150:
            recommendations.append("30kg Potash per hectare")
        
        if not recommendations:
            return "Soil nutrients adequate - maintenance fertilizer only"
        
        return " + ".join(recommendations)
    
    def _fallback_prediction(self, soil_data: Dict) -> Dict:
        """Fallback prediction when models are not available"""
        ph = soil_data.get('Ph', 6.5)
        n = soil_data.get('N', 40)
        p = soil_data.get('P', 20)
        k = soil_data.get('K', 200)
        
        # Simple rule-based prediction for Rwanda
        if ph < 5.5:
            crop = 'Cassava'  # Tolerates acidic soil
        elif n > 60 and k > 200:
            crop = 'Maize'  # High nutrient demand
        elif p > 30:
            crop = 'Beans'  # Good for phosphorus-rich soil
        elif k > 250:
            crop = 'Potato'  # High potassium need
        else:
            crop = 'Beans'  # Default safe crop
        
        soil_health = self._assess_soil_health(soil_data)
        recommendations = self._generate_recommendations(crop, soil_data)
        
        return {
            'success': True,
            'prediction': {
                'crop': crop,
                'confidence': 0.75
            },
            'soil_health': soil_health,
            'recommendations': recommendations,
            'alternatives': [
                {'crop': 'Maize', 'confidence': 0.65},
                {'crop': 'Cassava', 'confidence': 0.60}
            ]
        }

# Create singleton instance
ml_service = MLService()