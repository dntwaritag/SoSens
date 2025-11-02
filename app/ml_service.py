import joblib
import json
import numpy as np
from typing import Dict, List, Tuple
from preprocess import SoilDataPreprocessor

class MLPredictionService:
    '''Machine Learning Prediction Service'''
    
    def __init__(self, model_path: str, scaler_path: str, 
                encoder_path: str, features_path: str, metadata_path: str):
        '''Initialize ML service with saved models'''
        
        print("Loading ML models...")
        self.model = joblib.load(model_path)
        self.label_encoder = joblib.load(encoder_path)
        
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)
        
        self.preprocessor = SoilDataPreprocessor(scaler_path, features_path)
        
        print(f"✓ Model loaded: {self.metadata['model_name']}")
        print(f"✓ Accuracy: {self.metadata['accuracy']:.2%}")
        print(f"✓ Supported crops: {len(self.metadata['classes'])}")
        
        # Load crop knowledge base
        self._load_crop_recommendations()
    
    def _load_crop_recommendations(self):
        '''Load crop-specific recommendations database'''
        self.crop_database = {
            'Beans': {
                'ph_range': '6.0-7.0',
                'ph_optimal': 6.5,
                'fertilizer_base': '50kg DAP + 25kg Urea per hectare',
                'planting_season': 'Season A (September-December) and Season B (February-May)',
                'spacing': '40cm between rows, 10cm within row',
                'planting_depth': '3-5cm',
                'maturity_days': '75-90 days',
                'tips': [
                    'Rotate with maize for better soil health',
                    'Apply manure 2 weeks before planting',
                    'First weeding at 2-3 weeks after planting'
                ],
                'common_pests': ['Bean fly', 'Aphids', 'Bean beetle'],
                'water_requirement': 'Moderate (400-500mm during season)'
            },
            'Maize': {
                'ph_range': '5.5-7.0',
                'ph_optimal': 6.0,
                'fertilizer_base': '100kg NPK 17:17:17 + 50kg Urea per hectare',
                'planting_season': 'Season A and Season B with adequate rainfall',
                'spacing': '75cm between rows, 25cm within row',
                'planting_depth': '5cm',
                'maturity_days': '90-120 days',
                'tips': [
                    'Top-dress with urea when plants are knee-high',
                    'Plant 2-3 seeds per hole, thin to 1 strongest plant',
                    'Requires good drainage'
                ],
                'common_pests': ['Stalk borer', 'Fall armyworm', 'Maize weevil'],
                'water_requirement': 'High (500-800mm during season)'
            },
            'Cassava': {
                'ph_range': '5.5-6.5',
                'ph_optimal': 6.0,
                'fertilizer_base': '20kg NPK + organic matter per hectare',
                'planting_season': 'Can be planted throughout the year',
                'spacing': '1m x 1m',
                'planting_depth': '10-15cm (stem cutting)',
                'maturity_days': '270-360 days (9-12 months)',
                'tips': [
                    'Very drought-resistant crop',
                    'Use healthy stem cuttings 20-25cm long',
                    'Minimal fertilizer needs - good for poor soils',
                    'Control weeds in first 3 months'
                ],
                'common_pests': ['Cassava mosaic virus', 'Mealybugs', 'Green mites'],
                'water_requirement': 'Low (400-600mm during season)'
            },
            'Potato': {
                'ph_range': '5.0-6.5',
                'ph_optimal': 5.5,
                'fertilizer_base': '150kg NPK 17:17:17 per hectare',
                'planting_season': 'Season B preferred (cooler conditions)',
                'spacing': '75cm between rows, 30cm within row',
                'planting_depth': '10cm',
                'maturity_days': '90-120 days',
                'tips': [
                    'Hill soil around plants as they grow',
                    'Watch for late blight disease',
                    'Harvest when leaves turn yellow'
                ],
                'common_pests': ['Late blight', 'Potato tuber moth', 'Aphids'],
                'water_requirement': 'Moderate to High (500-700mm)'
            },
            'Rice': {
                'ph_range': '5.5-6.5',
                'ph_optimal': 6.0,
                'fertilizer_base': '100kg NPK + 50kg Urea per hectare',
                'planting_season': 'Depends on water availability (marshlands)',
                'spacing': '20cm x 20cm',
                'planting_depth': '2-3cm',
                'maturity_days': '120-150 days',
                'tips': [
                    'Maintain water levels in paddy',
                    'Control weeds in first 40 days',
                    'Drain field 2 weeks before harvest'
                ],
                'common_pests': ['Rice blast', 'Stem borers', 'Birds'],
                'water_requirement': 'Very High (requires flooding)'
            },
            'Wheat': {
                'ph_range': '6.0-7.0',
                'ph_optimal': 6.5,
                'fertilizer_base': '100kg DAP + 50kg Urea per hectare',
                'planting_season': 'Season B (cooler, drier conditions)',
                'spacing': 'Broadcast or drill in 20cm rows',
                'planting_depth': '3-5cm',
                'maturity_days': '120-150 days',
                'tips': [
                    'Requires cooler temperatures',
                    'Good drainage essential',
                    'Top-dress with urea at tillering stage'
                ],
                'common_pests': ['Rust diseases', 'Aphids', 'Birds'],
                'water_requirement': 'Moderate (450-650mm)'
            },
            'Sorghum': {
                'ph_range': '5.5-7.5',
                'ph_optimal': 6.5,
                'fertilizer_base': '50kg NPK + 30kg Urea per hectare',
                'planting_season': 'Season A and B',
                'spacing': '75cm x 15cm',
                'planting_depth': '3-5cm',
                'maturity_days': '100-130 days',
                'tips': [
                    'Very drought tolerant',
                    'Good for marginal soils',
                    'Thin plants after 2-3 weeks'
                ],
                'common_pests': ['Sorghum midge', 'Stalk borer', 'Birds'],
                'water_requirement': 'Low to Moderate (400-600mm)'
            }
        }
    
    def predict(self, soil_data: Dict, get_alternatives: bool = True, 
                top_n: int = 3) -> Dict:
        '''
        Make crop prediction based on soil data
        
        Args:
            soil_data: Dictionary with soil parameters
            get_alternatives: Whether to return alternative crop suggestions
            top_n: Number of top alternatives to return
        
        Returns:
            Dictionary with prediction results and recommendations
        '''
        try:
            # Validate input
            is_valid, errors = self.preprocessor.validate_soil_parameters(soil_data)
            if not is_valid:
                return {
                    'success': False,
                    'error': 'Invalid soil parameters',
                    'details': errors
                }
            
            # Prepare data
            input_df = self.preprocessor.prepare_input_data(soil_data)
            
            # Scale data if needed
            model_name = self.metadata['model_name']
            if model_name in ['K-Nearest Neighbors', 'Logistic Regression']:
                input_scaled = self.preprocessor.scale_data(input_df)
                prediction_encoded = self.model.predict(input_scaled)
                probabilities = self.model.predict_proba(input_scaled)[0]
            else:
                prediction_encoded = self.model.predict(input_df)
                probabilities = self.model.predict_proba(input_df)[0]
            
            # Decode prediction
            predicted_crop = self.label_encoder.inverse_transform(prediction_encoded)[0]
            confidence = probabilities[prediction_encoded[0]]
            
            # Get alternatives
            alternatives = []
            if get_alternatives:
                top_indices = np.argsort(probabilities)[-top_n:][::-1]
                for idx in top_indices[1:]:  # Skip first (main prediction)
                    crop = self.label_encoder.inverse_transform([idx])[0]
                    alternatives.append({
                        'crop': crop,
                        'confidence': float(probabilities[idx]),
                        'confidence_percent': f"{probabilities[idx]:.1%}"
                    })
            
            # Assess soil health
            ph = soil_data.get('Ph', 6.0)
            n = soil_data.get('N', 0)
            p = soil_data.get('P', 0)
            k = soil_data.get('K', 0)
            
            soil_health = self.preprocessor.assess_soil_health(ph, n, p, k)
            
            # Get crop-specific recommendations
            crop_info = self.crop_database.get(predicted_crop, {})
            
            # Calculate fertilizer needs
            fertilizer_rec = self.preprocessor.calculate_fertilizer_needs(
                predicted_crop, ph, n, p, k
            )
            
            # Build response
            result = {
                'success': True,
                'prediction': {
                    'crop': predicted_crop,
                    'confidence': float(confidence),
                    'confidence_percent': f"{confidence:.1%}"
                },
                'alternatives': alternatives,
                'soil_health': soil_health,
                'recommendations': {
                    'fertilizer': fertilizer_rec,
                    'base_fertilizer': crop_info.get('fertilizer_base', 'Contact extension officer'),
                    'planting_season': crop_info.get('planting_season', 'Contact extension officer'),
                    'spacing': crop_info.get('spacing', 'Standard spacing recommended'),
                    'planting_depth': crop_info.get('planting_depth', 'As per standard practice'),
                    'maturity_days': crop_info.get('maturity_days', 'Varies by variety'),
                    'water_requirement': crop_info.get('water_requirement', 'Moderate'),
                    'tips': crop_info.get('tips', []),
                    'common_pests': crop_info.get('common_pests', [])
                },
                'next_steps': self._generate_action_plan(predicted_crop, soil_health)
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_action_plan(self, crop: str, soil_health: Dict) -> List[str]:
        '''Generate step-by-step action plan for farmer'''
        steps = []
        
        # Soil improvement steps (if needed)
        if soil_health['status'] == 'Poor':
            steps.append("🚨 URGENT: Address soil issues before planting")
            for rec in soil_health['recommendations']:
                if rec['priority'] == 'HIGH':
                    steps.append(f"   → {rec['recommendation']}")
        
        # Crop-specific steps
        crop_info = self.crop_database.get(crop, {})
        
        steps.extend([
            f"1. Prepare land and apply {crop_info.get('fertilizer_base', 'recommended fertilizer')}",
            f"2. Plant {crop} during {crop_info.get('planting_season', 'appropriate season')}",
            f"3. Use spacing: {crop_info.get('spacing', 'as recommended')}",
            f"4. Monitor for common pests: {', '.join(crop_info.get('common_pests', ['various pests'])[:2])}",
            f"5. Harvest after approximately {crop_info.get('maturity_days', '90-120 days')}"
        ])
        
        return steps
    
    def get_crop_info(self, crop_name: str) -> Dict:
        '''Get detailed information about a specific crop'''
        if crop_name in self.crop_database:
            return {
                'success': True,
                'crop': crop_name,
                'details': self.crop_database[crop_name]
            }
        else:
            return {
                'success': False,
                'error': f'Crop {crop_name} not found in database'
            }
    
    def list_supported_crops(self) -> List[str]:
        '''List all supported crops'''
        return self.metadata['classes']