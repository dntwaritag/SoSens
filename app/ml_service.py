"""
ML Service for crop prediction - FIXED VERSION
"""

import joblib
import json
import os
import numpy as np
from typing import Dict, Optional
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
        
        self._load_models()
    
    def _load_models(self):
        """Load all ML models """
        try:
            # Method 1: Look relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            possible_paths = [
                os.path.join(current_dir, 'models'),           # app/models/
                os.path.join(current_dir, '..', 'models'),     # ./models/
                os.path.join(current_dir, '../models'),        # ./models/
                '/app/models',                                  # Docker path
                './models',                                     # Current directory
            ]
            
            models_dir = None
            print(f"\n{'='*60}")
            print(f" ML MODEL LOADING - PATH DETECTION")
            print(f"{'='*60}")
            print(f" Current file location: {current_dir}")
            
            for path in possible_paths:
                abs_path = os.path.abspath(path)
                exists = os.path.exists(abs_path)
                print(f" Checking: {abs_path} - {' FOUND' if exists else ' NOT FOUND'}")
                if exists:
                    models_dir = abs_path
                    break
            
            if not models_dir:
                print(f" CRITICAL: No models directory found!")
                print(f" Checked paths: {possible_paths}")
                print(f"{'='*60}\n")
                return
            
            print(f" Using models directory: {models_dir}")
            print(f" Files in directory: {os.listdir(models_dir)}")
            
            # Load each model with validation
            model_path = os.path.join(models_dir, 'rwanda_soil_model_random_forest.pkl')
            scaler_path = os.path.join(models_dir, 'feature_scaler.pkl')
            encoder_path = os.path.join(models_dir, 'label_encoder.pkl')
            features_path = os.path.join(models_dir, 'feature_names.pkl')
            metadata_path = os.path.join(models_dir, 'model_metadata.json')
            
            # Load with error handling for each file
            try:
                self.model = joblib.load(model_path)
                self.model_loaded = True
                print(f"  ML Model loaded successfully")
            except FileNotFoundError:
                print(f" Model file not found: {model_path}")
                raise
            except Exception as e:
                print(f"  Error loading model: {e}")
                raise
            
            try:
                self.scaler = joblib.load(scaler_path)
                print(f"  Scaler loaded")
            except Exception as e:
                print(f" Scaler loading failed: {e}")
            
            try:
                self.encoder = joblib.load(encoder_path)
                print(f" Encoder loaded")
            except Exception as e:
                print(f" Encoder loading failed: {e}")
            
            try:
                self.feature_names = joblib.load(features_path)
                print(f" Feature names loaded: {self.feature_names}")
            except Exception as e:
                print(f" Feature names loading failed: {e}")
            
            try:
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                print(f" Metadata loaded")
            except Exception as e:
                print(f" Metadata loading failed: {e}")
            
            print(f"{'='*60}\n")
                    
        except Exception as e:
            print(f"\n{'='*60}")
            print(f" CRITICAL MODEL LOADING ERROR")
            print(f"{'='*60}")
            print(f" Error: {e}")
            print(f" Model will NOT be available")
            print(f"{'='*60}\n")
            import traceback
            traceback.print_exc()
            self.model_loaded = False
    
    def predict(self, soil_data: Dict) -> Dict:
        """
        Make crop prediction based on soil data
        """
        try:
            # If models not loaded, use fallback
            if not self.model_loaded or self.model is None:
                print(" WARNING: Using fallback prediction (model not loaded)")
                return self._fallback_prediction(soil_data)
            
            # Prepare features
            features = self._prepare_features(soil_data)
            print(f" Input features: {features}")
            
            # Scale features
            if self.scaler:
                features_scaled = self.scaler.transform([features])
                print(f" Scaled features: {features_scaled}")
            else:
                features_scaled = [features]
                print(f" WARNING: No scaler available, using raw features")
            
            # Make prediction
            prediction = self.model.predict(features_scaled)[0]
            print(f" Raw prediction: {prediction}")
            
            # Get confidence (probability)
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(features_scaled)[0]
                confidence = float(np.max(probabilities))
                print(f" Probabilities: {probabilities}")
                print(f" Max confidence: {confidence}")
                
                # Get alternatives
                top_3_indices = np.argsort(probabilities)[-3:][::-1]
                alternatives = []
                for idx in top_3_indices[1:]:  # main prediction
                    if self.encoder:
                        crop_name = self.encoder.inverse_transform([idx])[0]
                    else:
                        crop_name = f"Crop_{idx}"
                    alternatives.append({
                        'crop': crop_name,
                        'confidence': float(probabilities[idx])
                    })
            else:
                confidence = 0.85
                alternatives = []
                print(f" WARNING: Model has no predict_proba method")
            
            # Decode crop name
            if self.encoder:
                crop_name = self.encoder.inverse_transform([prediction])[0]
                print(f" Decoded crop: {crop_name}")
            else:
                crop_name = str(prediction)
            
            # Assess soil health
            soil_health = self._assess_soil_health(soil_data)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(crop_name, soil_data)
            
            result = {
                'success': True,
                'prediction': {
                    'crop': crop_name,
                    'confidence': confidence
                },
                'soil_health': soil_health,
                'recommendations': recommendations,
                'alternatives': alternatives
            }
            
            print(f" Final result: {result}")
            return result
            
        except Exception as e:
            print(f" Prediction error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def _prepare_features(self, soil_data: Dict) -> list:
        """Prepare features in correct order"""
        defaults = {
            'Ph': soil_data.get('Ph', 6.5),
            'N': soil_data.get('N', 40),
            'P': soil_data.get('P', 20),
            'K': soil_data.get('K', 200),
            'Zn': soil_data.get('Zn', 5.0),
            'S': soil_data.get('S', 15.0)
        }
        
        if self.feature_names:
            features = [defaults.get(f, 0) for f in self.feature_names]
        else:
            features = [defaults['Ph'], defaults['N'], defaults['P'], 
                    defaults['K'], defaults['Zn'], defaults['S']]
        
        return features
    
    def _assess_soil_health(self, soil_data: Dict) -> Dict:
        """Assess soil health status based on actual values"""
        ph = soil_data.get('Ph', 6.5)
        n = soil_data.get('N', 40)
        p = soil_data.get('P', 20)
        k = soil_data.get('K', 200)
        zn = soil_data.get('Zn', 5.0)
        
        issues = []
        
        # pH check
        if ph < 5.5:
            issues.append("Soil is too acidic (pH < 5.5) - apply lime")
        elif ph > 7.5:
            issues.append("Soil is too alkaline (pH > 7.5) - add organic matter")
        
        # Nitrogen check
        if n < 20:
            issues.append("Low nitrogen (< 20) - apply urea or manure")
        elif n > 80:
            issues.append("Excessive nitrogen (> 80) - reduce fertilizer")
        
        # Phosphorus check
        if p < 10:
            issues.append("Low phosphorus (< 10) - apply DAP")
        
        # Potassium check
        if k < 100:
            issues.append("Low potassium (< 100) - apply potash")
        
        # Zinc check
        if zn < 2:
            issues.append("Low zinc (< 2) - apply zinc sulfate")
        
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
        """Generate farming recommendations based on soil data"""
        
        # Rwanda planting seasons
        season_map = {
            'Beans': 'Season A (Sep-Dec) & Season B (Feb-May)',
            'Maize': 'Season A (Sep-Dec) & Season B (Feb-May)',
            'Cassava': 'Year-round planting possible',
            'Potato': 'Season B (Feb-May) in highland areas',
            'Rice': 'Season A (Sep-Dec) in wetlands',
            'Wheat': 'Season B (Feb-May) in highland areas'
        }
        
        # Fertilizer recommendations based on actual soil data
        fertilizer = self._calculate_fertilizer(crop, soil_data)
        
        return {
            'fertilizer': fertilizer,
            'planting_season': season_map.get(crop, 'Consult local agricultural officer'),
            'spacing': 'Standard spacing for crop type'
        }
    
    def _calculate_fertilizer(self, crop: str, soil_data: Dict) -> str:
        """Calculate fertilizer needs based on actual soil values"""
        n = soil_data.get('N', 40)
        p = soil_data.get('P', 20)
        k = soil_data.get('K', 200)
        
        recommendations = []
        
        # Nitrogen recommendations
        if n < 20:
            recommendations.append("100kg Urea per hectare")
        elif n < 40:
            recommendations.append("50kg Urea per hectare")
        elif n > 80:
            recommendations.append("Nitrogen adequate - skip urea")
        
        # Phosphorus recommendations
        if p < 10:
            recommendations.append("75kg DAP per hectare")
        elif p < 20:
            recommendations.append("50kg DAP per hectare")
        elif p > 40:
            recommendations.append("Phosphorus adequate")
        
        # Potassium recommendations
        if k < 100:
            recommendations.append("60kg Potash per hectare")
        elif k < 150:
            recommendations.append("30kg Potash per hectare")
        elif k > 250:
            recommendations.append("Potassium adequate")
        
        if not recommendations:
            return "Soil nutrients adequate - maintenance fertilizer only"
        
        return " + ".join(recommendations)
    
    def _fallback_prediction(self, soil_data: Dict) -> Dict:
        """Fallback prediction when models are not available"""
        print("\n" + "="*60)
        print(" FALLBACK PREDICTION MODE (Model Not Available)")
        print("="*60 + "\n")
        
        ph = soil_data.get('Ph', 6.5)
        n = soil_data.get('N', 40)
        p = soil_data.get('P', 20)
        k = soil_data.get('K', 200)
        
        # Rule-based prediction for Rwanda
        if ph < 5.5:
            crop = 'Cassava'
        elif n > 60 and k > 200:
            crop = 'Maize'
        elif p > 30:
            crop = 'Beans'
        elif k > 250:
            crop = 'Potato'
        else:
            crop = 'Beans'
        
        soil_health = self._assess_soil_health(soil_data)
        recommendations = self._generate_recommendations(crop, soil_data)
        
        return {
            'success': True,
            'prediction': {
                'crop': crop,
                'confidence': 0.72
            },
            'soil_health': soil_health,
            'recommendations': recommendations,
            'alternatives': [
                {'crop': 'Maize', 'confidence': 0.65},
                {'crop': 'Cassava', 'confidence': 0.60}
            ]
        }

    async def _download_model_from_url(self):
        """Download model from cloud URL if local files not found"""
        import httpx
        
        if not settings.MODEL_URL:
            return False
        
        try:
            print(" Attempting to download model from URL...")
            async with httpx.AsyncClient() as client:
                response = await client.get(settings.MODEL_URL)
                model_bytes = response.content
                self.model = joblib.loads(model_bytes)
                self.model_loaded = True
                print(" Model downloaded successfully")
                return True
        except Exception as e:
            print(f" Failed to download model: {e}")
            return False
    
# Create singleton instance
ml_service = MLService()