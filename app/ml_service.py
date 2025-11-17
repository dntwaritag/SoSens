import joblib
import json
import numpy as np
from typing import Dict, Optional
from config import settings

class MLPredictionService:
    def __init__(self):
        try:
            self.model = joblib.load(settings.MODEL_PATH)
            self.scaler = joblib.load(settings.SCALER_PATH)
            self.label_encoder = joblib.load(settings.ENCODER_PATH)
            with open(settings.FEATURES_PATH, 'rb') as f:
                self.feature_names = joblib.load(f)
            with open(settings.METADATA_PATH, 'r') as f:
                self.metadata = json.load(f)
            print("✓ ML Model loaded successfully")
        except Exception as e:
            print(f"⚠ ML Model load failed: {e}")
            raise

    def predict(self, soil_data: Dict) -> Dict:
        try:
            # Default values for missing features
            defaults = {
                'Zn': 5.0, 'S': 15.0,
                'QV2M-W': 0.005, 'QV2M-Sp': 0.006, 'QV2M-Su': 0.007, 'QV2M-Au': 0.006,
                'T2M_MAX-W': 25.0, 'T2M_MAX-Sp': 26.0, 'T2M_MAX-Su': 27.0, 'T2M_MAX-Au': 26.0,
                'T2M_MIN-W': 15.0, 'T2M_MIN-Sp': 16.0, 'T2M_MIN-Su': 17.0, 'T2M_MIN-Au': 16.0,
                'PRECTOTCORR-W': 2.5, 'PRECTOTCORR-Sp': 3.0, 'PRECTOTCORR-Su': 2.0, 'PRECTOTCORR-Au': 2.5,
                'WD10M': 180.0, 'GWETTOP': 0.6, 'CLOUD_AMT': 50.0, 'WS2M_RANGE': 3.5, 'PS': 85.0
            }
            full_data = {**defaults, **soil_data}
            
            import pandas as pd
            input_df = pd.DataFrame([full_data], columns=self.feature_names)
            
            # Scale and predict
            if self.metadata['model_name'] in ['K-Nearest Neighbors', 'Logistic Regression']:
                input_scaled = self.scaler.transform(input_df)
                prediction = self.model.predict(input_scaled)
                probabilities = self.model.predict_proba(input_scaled)[0]
            else:
                prediction = self.model.predict(input_df)
                probabilities = self.model.predict_proba(input_df)[0]
            
            # Decode
            predicted_crop = self.label_encoder.inverse_transform(prediction)[0]
            confidence = probabilities[prediction[0]]
            
            # Top 3 alternatives
            top_3 = np.argsort(probabilities)[-3:][::-1]
            alternatives = [
                {
                    'crop': self.label_encoder.inverse_transform([idx])[0],
                    'confidence': float(probabilities[idx])
                }
                for idx in top_3[1:]
            ]
            
            # Soil health
            ph, n, p, k = soil_data['Ph'], soil_data['N'], soil_data['P'], soil_data['K']
            issues = []
            if ph < 5.5:
                issues.append("Soil too acidic - apply lime")
            if n < 20:
                issues.append("Low nitrogen - apply urea")
            if p < 10:
                issues.append("Low phosphorus - apply DAP")
            if k < 100:
                issues.append("Low potassium - apply potash")
            
            status = "Good" if len(issues) == 0 else ("Fair" if len(issues) <= 2 else "Poor")
            
            # Fertilizer recommendation
            fertilizer = self._get_fertilizer(predicted_crop, n, p, k)
            season = self._get_season(predicted_crop)
            
            return {
                'success': True,
                'prediction': {
                    'crop': predicted_crop,
                    'confidence': float(confidence),
                    'confidence_percent': f"{confidence:.1%}"
                },
                'alternatives': alternatives,
                'soil_health': {
                    'status': status,
                    'issues': issues
                },
                'recommendations': {
                    'fertilizer': fertilizer,
                    'planting_season': season
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_fertilizer(self, crop: str, n: float, p: float, k: float) -> str:
        requirements = {
            'Beans': {'N': 30, 'P': 40, 'K': 20},
            'Maize': {'N': 80, 'P': 40, 'K': 40},
            'Potato': {'N': 100, 'P': 50, 'K': 150},
            'Rice': {'N': 80, 'P': 40, 'K': 40}
        }
        req = requirements.get(crop, {'N': 50, 'P': 30, 'K': 30})
        
        n_deficit = max(0, req['N'] - n)
        p_deficit = max(0, req['P'] - p)
        k_deficit = max(0, req['K'] - k)
        
        recs = []
        if n_deficit > 0:
            recs.append(f"{n_deficit/0.46:.0f}kg Urea")
        if p_deficit > 0:
            recs.append(f"{p_deficit/0.46:.0f}kg DAP")
        if k_deficit > 0:
            recs.append(f"{k_deficit/0.60:.0f}kg Potash")
        
        return " + ".join(recs) + " per hectare" if recs else "Soil nutrients adequate"
    
    def _get_season(self, crop: str) -> str:
        seasons = {
            'Beans': 'Season A (Sep-Dec) and Season B (Feb-May)',
            'Maize': 'Season A and Season B',
            'Potato': 'Season B (cooler conditions)',
            'Rice': 'Year-round with adequate water'
        }
        return seasons.get(crop, 'Consult local extension officer')
    
    def list_supported_crops(self):
        return self.metadata['classes']

ml_service = MLPredictionService()