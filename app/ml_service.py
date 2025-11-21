import joblib
import json
import os
import numpy as np
import pandas as pd
from typing import Dict, Optional, List
from .config import settings

class MLService:
    def __init__(self):
        """Initialize ML models"""
        self.model = None
        self.scaler = None
        self.encoder = None
        self.feature_names = None
        self.metadata = None
        self.model_loaded = False
        
        # Rwanda average environmental defaults (Crucial for model accuracy)
        self.defaults = {
            # Soil Defaults
            'Zn': 5.0,
            'S': 15.0,
            # Environmental Defaults (Rwanda Averages)
            'QV2M-W': 0.005,      'QV2M-Sp': 0.006,      'QV2M-Su': 0.007,      'QV2M-Au': 0.006,
            'T2M_MAX-W': 25.0,    'T2M_MAX-Sp': 26.0,    'T2M_MAX-Su': 27.0,    'T2M_MAX-Au': 26.0,
            'T2M_MIN-W': 15.0,    'T2M_MIN-Sp': 16.0,    'T2M_MIN-Su': 17.0,    'T2M_MIN-Au': 16.0,
            'PRECTOTCORR-W': 2.5, 'PRECTOTCORR-Sp': 3.0, 'PRECTOTCORR-Su': 2.0, 'PRECTOTCORR-Au': 2.5,
            'WD10M': 180.0,       'GWETTOP': 0.6,        'CLOUD_AMT': 50.0,     'WS2M_RANGE': 3.5,
            'PS': 85.0
        }
        
        self._load_models()
    
    def _load_models(self):
        """Load all ML models"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            possible_paths = [
                os.path.join(current_dir, 'models'),
                os.path.join(current_dir, '..', 'models'),
                '/app/models',
                './models',
            ]
            
            models_dir = None
            for path in possible_paths:
                if os.path.exists(path):
                    models_dir = path
                    break
            
            if not models_dir:
                print("CRITICAL: No models directory found")
                return
            
            # Load artifacts
            self.model = joblib.load(os.path.join(models_dir, 'rwanda_soil_model_random_forest.pkl'))
            self.scaler = joblib.load(os.path.join(models_dir, 'feature_scaler.pkl'))
            self.encoder = joblib.load(os.path.join(models_dir, 'label_encoder.pkl'))
            self.feature_names = joblib.load(os.path.join(models_dir, 'feature_names.pkl'))
            
            try:
                with open(os.path.join(models_dir, 'model_metadata.json'), 'r') as f:
                    self.metadata = json.load(f)
            except:
                pass

            self.model_loaded = True
            print("ML Models loaded successfully")
                    
        except Exception as e:
            print(f"Error loading models: {e}")
            self.model_loaded = False
    
    def predict(self, soil_data: Dict) -> Dict:
        """Make crop prediction based on soil data"""
        try:
            if not self.model_loaded:
                return self._fallback_prediction(soil_data)
            
            # 1. Prepare DataFrame (Fixes Feature Name Warning)
            input_df = self._prepare_input_dataframe(soil_data)
            
            # 2. Scale features using DataFrame (Fixes Scaler Warning)
            if self.scaler:
                features_scaled = self.scaler.transform(input_df)
            else:
                features_scaled = input_df.values
            
            # 3. Make prediction
            prediction_idx = self.model.predict(features_scaled)[0]
            
            # 4. Get confidence
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(features_scaled)[0]
                confidence = float(np.max(probabilities))
                
                # Get alternatives
                top_3_indices = np.argsort(probabilities)[-3:][::-1]
                alternatives = []
                for idx in top_3_indices[1:]:
                    if self.encoder:
                        alt_name = self.encoder.inverse_transform([idx])[0]
                    else:
                        alt_name = str(idx)
                    alternatives.append({
                        'crop': alt_name,
                        'confidence': float(probabilities[idx])
                    })
            else:
                confidence = 0.85
                alternatives = []
            
            # 5. Decode crop name
            if self.encoder:
                crop_name = self.encoder.inverse_transform([prediction_idx])[0]
            else:
                crop_name = str(prediction_idx)
            
            # Generate Response
            return {
                'success': True,
                'prediction': {
                    'crop': crop_name,
                    'confidence': confidence
                },
                'soil_health': self._assess_soil_health(soil_data),
                'recommendations': self._generate_recommendations(crop_name, soil_data),
                'alternatives': alternatives
            }
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _prepare_input_dataframe(self, soil_data: Dict) -> pd.DataFrame:
        """Creates a Pandas DataFrame with exact columns expected by the model"""
        input_data = soil_data.copy()
        
        # Fill defaults for environmental data
        for key, value in self.defaults.items():
            if key not in input_data:
                input_data[key] = value

        # Ensure all model features exist
        final_data = {}
        if self.feature_names:
            for feature in self.feature_names:
                final_data[feature] = input_data.get(feature, 0.0)
            return pd.DataFrame([final_data], columns=self.feature_names)
        else:
            return pd.DataFrame([input_data])

    def _assess_soil_health(self, soil_data: Dict) -> Dict:
        """Assess soil health status"""
        ph = soil_data.get('Ph', 6.5)
        n = soil_data.get('N', 40)
        
        issues = []
        if ph < 5.5: issues.append("Soil is too acidic (pH < 5.5) - apply lime")
        elif ph > 7.5: issues.append("Soil is too alkaline (pH > 7.5) - add organic matter")
        
        if n < 20: issues.append("Low nitrogen - apply manure")
        elif n > 80: issues.append("Excessive nitrogen - reduce fertilizer")
        
        status = "Good"
        if len(issues) >= 3: status = "Poor"
        elif len(issues) >= 1: status = "Fair"
        
        return {'status': status, 'issues': issues}
    
    def _generate_recommendations(self, crop: str, soil_data: Dict) -> Dict:
        """Generate farming recommendations"""
        season_map = {
            'Beans': 'Season A (Sep-Dec) & Season B (Feb-May)',
            'Maize': 'Season A (Sep-Dec) & Season B (Feb-May)',
            'Cassava': 'Year-round planting possible',
            'Potato': 'Season B (Feb-May) in highland areas',
            'Rice': 'Season A (Sep-Dec) in wetlands',
            'Wheat': 'Season B (Feb-May) in highland areas'
        }
        return {
            'fertilizer': self._calculate_fertilizer(crop, soil_data),
            'planting_season': season_map.get(crop, 'Consult local officer'),
            'spacing': 'Standard spacing for crop type'
        }
    
    def _calculate_fertilizer(self, crop: str, soil_data: Dict) -> str:
        n = soil_data.get('N', 40)
        p = soil_data.get('P', 20)
        k = soil_data.get('K', 200)
        
        recs = []
        if n < 40: recs.append("50kg Urea/ha")
        if p < 20: recs.append("50kg DAP/ha")
        if k < 100: recs.append("30kg Potash/ha")
        
        if not recs: return "Soil nutrients adequate"
        return " + ".join(recs)

    def _fallback_prediction(self, soil_data: Dict) -> Dict:
        """Fallback when model is unavailable"""
        ph = soil_data.get('Ph', 6.5)
        if ph < 5.5: crop = 'Cassava'
        elif ph > 6.0: crop = 'Maize'
        else: crop = 'Beans'
        
        return {
            'success': True,
            'prediction': {'crop': crop, 'confidence': 0.60},
            'soil_health': self._assess_soil_health(soil_data),
            'recommendations': self._generate_recommendations(crop, soil_data),
            'alternatives': []
        }

ml_service = MLService()