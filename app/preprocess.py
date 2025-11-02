import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
import joblib
import json

class SoilDataPreprocessor:
    '''Handles all data preprocessing for soil quality predictions'''
    
    def __init__(self, scaler_path: str, feature_names_path: str):
        '''Initialize preprocessor with saved scaler and feature names'''
        self.scaler = joblib.load(scaler_path)
        with open(feature_names_path, 'rb') as f:
            self.feature_names = joblib.load(f)
        
        # Default values for missing environmental parameters
        # These should be calculated from training data or Rwanda-specific averages
        self.default_environmental_values = {
            'Zn': 5.0,
            'S': 15.0,
            'QV2M-W': 0.005,
            'QV2M-Sp': 0.006,
            'QV2M-Su': 0.007,
            'QV2M-Au': 0.006,
            'T2M_MAX-W': 25.0,
            'T2M_MAX-Sp': 26.0,
            'T2M_MAX-Su': 27.0,
            'T2M_MAX-Au': 26.0,
            'T2M_MIN-W': 15.0,
            'T2M_MIN-Sp': 16.0,
            'T2M_MIN-Su': 17.0,
            'T2M_MIN-Au': 16.0,
            'PRECTOTCORR-W': 2.5,
            'PRECTOTCORR-Sp': 3.0,
            'PRECTOTCORR-Su': 2.0,
            'PRECTOTCORR-Au': 2.5,
            'WD10M': 180.0,
            'GWETTOP': 0.6,
            'CLOUD_AMT': 50.0,
            'WS2M_RANGE': 3.5,
            'PS': 85.0
        }
    
    def validate_soil_parameters(self, data: Dict) -> Tuple[bool, List[str]]:
        '''
        Validate soil parameters are within acceptable ranges
        Returns: (is_valid, list_of_errors)
        '''
        errors = []
        
        # pH validation (acidic to alkaline range)
        if 'Ph' in data:
            if not (3.0 <= data['Ph'] <= 10.0):
                errors.append(f"pH must be between 3.0 and 10.0, got {data['Ph']}")
        else:
            errors.append("pH (Ph) is required")
        
        # Nitrogen validation (typical range in kg/ha)
        if 'N' in data:
            if not (0 <= data['N'] <= 200):
                errors.append(f"Nitrogen (N) must be between 0 and 200, got {data['N']}")
        else:
            errors.append("Nitrogen (N) is required")
        
        # Phosphorus validation
        if 'P' in data:
            if not (0 <= data['P'] <= 150):
                errors.append(f"Phosphorus (P) must be between 0 and 150, got {data['P']}")
        else:
            errors.append("Phosphorus (P) is required")
        
        # Potassium validation
        if 'K' in data:
            if not (0 <= data['K'] <= 600):
                errors.append(f"Potassium (K) must be between 0 and 600, got {data['K']}")
        else:
            errors.append("Potassium (K) is required")
        
        return len(errors) == 0, errors
    
    def prepare_input_data(self, soil_data: Dict, use_defaults: bool = True) -> pd.DataFrame:
        '''
        Prepare input data for model prediction
        
        Args:
            soil_data: Dictionary with soil parameters
            use_defaults: Whether to use default values for missing features
        
        Returns:
            DataFrame ready for model prediction
        '''
        # Start with defaults if needed
        if use_defaults:
            full_data = self.default_environmental_values.copy()
            full_data.update(soil_data)
        else:
            full_data = soil_data.copy()
        
        # Create DataFrame with features in correct order
        try:
            input_df = pd.DataFrame([full_data], columns=self.feature_names)
            return input_df
        except KeyError as e:
            missing_features = [f for f in self.feature_names if f not in full_data]
            raise ValueError(f"Missing required features: {missing_features}")
    
    def scale_data(self, data: pd.DataFrame) -> np.ndarray:
        '''Scale data using the saved scaler'''
        return self.scaler.transform(data)
    
    def assess_soil_health(self, ph: float, n: float, p: float, k: float) -> Dict:
        '''
        Assess overall soil health and provide specific recommendations
        
        Returns:
            Dictionary with status and list of issues/recommendations
        '''
        issues = []
        recommendations = []
        
        # pH Assessment (Critical for Rwanda's lateritic soils)
        if ph < 5.5:
            issues.append("Soil is too acidic")
            recommendations.append({
                'parameter': 'pH',
                'issue': 'Acidic soil (pH < 5.5)',
                'recommendation': 'Apply agricultural lime at 2-3 tonnes/hectare',
                'priority': 'HIGH'
            })
        elif ph > 7.5:
            issues.append("Soil is too alkaline")
            recommendations.append({
                'parameter': 'pH',
                'issue': 'Alkaline soil (pH > 7.5)',
                'recommendation': 'Add organic matter (compost/manure)',
                'priority': 'MEDIUM'
            })
        
        # Nitrogen Assessment
        if n < 20:
            issues.append("Low nitrogen content")
            recommendations.append({
                'parameter': 'Nitrogen',
                'issue': 'Nitrogen deficiency (< 20 kg/ha)',
                'recommendation': 'Apply 50kg Urea per hectare or use legume cover crops',
                'priority': 'HIGH'
            })
        elif n > 80:
            issues.append("Excessive nitrogen")
            recommendations.append({
                'parameter': 'Nitrogen',
                'issue': 'Excess nitrogen (> 80 kg/ha)',
                'recommendation': 'Reduce nitrogen fertilizer. Risk of crop lodging',
                'priority': 'MEDIUM'
            })
        
        # Phosphorus Assessment
        if p < 10:
            issues.append("Low phosphorus content")
            recommendations.append({
                'parameter': 'Phosphorus',
                'issue': 'Phosphorus deficiency (< 10 kg/ha)',
                'recommendation': 'Apply 50kg DAP (Diammonium Phosphate) per hectare',
                'priority': 'HIGH'
            })
        elif p > 50:
            issues.append("Excessive phosphorus")
            recommendations.append({
                'parameter': 'Phosphorus',
                'issue': 'Excess phosphorus (> 50 kg/ha)',
                'recommendation': 'Reduce phosphorus fertilizer application',
                'priority': 'LOW'
            })
        
        # Potassium Assessment
        if k < 100:
            issues.append("Low potassium content")
            recommendations.append({
                'parameter': 'Potassium',
                'issue': 'Potassium deficiency (< 100 kg/ha)',
                'recommendation': 'Apply potash fertilizer or wood ash',
                'priority': 'MEDIUM'
            })
        elif k > 300:
            issues.append("Excessive potassium")
            recommendations.append({
                'parameter': 'Potassium',
                'issue': 'Excess potassium (> 300 kg/ha)',
                'recommendation': 'Reduce potassium fertilizer',
                'priority': 'LOW'
            })
        
        # Overall Status
        high_priority_issues = [r for r in recommendations if r['priority'] == 'HIGH']
        if len(high_priority_issues) >= 2:
            status = "Poor"
        elif len(high_priority_issues) == 1 or len(issues) > 0:
            status = "Fair"
        else:
            status = "Good"
        
        return {
            'status': status,
            'issues': issues,
            'recommendations': recommendations,
            'summary': f"Soil health is {status}. {len(issues)} issue(s) detected."
        }
    
    def calculate_fertilizer_needs(self, crop: str, ph: float, n: float, 
                                   p: float, k: float) -> str:
        '''
        Calculate specific fertilizer recommendations based on crop and soil status
        '''
        # Crop-specific base requirements (kg/hectare)
        crop_requirements = {
            'Beans': {'N': 30, 'P': 40, 'K': 20},
            'Maize': {'N': 80, 'P': 40, 'K': 40},
            'Cassava': {'N': 50, 'P': 30, 'K': 50},
            'Potato': {'N': 100, 'P': 50, 'K': 150},
            'Rice': {'N': 80, 'P': 40, 'K': 40},
            'Wheat': {'N': 90, 'P': 40, 'K': 30}
        }
        
        if crop not in crop_requirements:
            return "Contact local extension officer for fertilizer recommendations"
        
        req = crop_requirements[crop]
        
        # Calculate deficits
        n_deficit = max(0, req['N'] - n)
        p_deficit = max(0, req['P'] - p)
        k_deficit = max(0, req['K'] - k)
        
        recommendations = []
        
        if n_deficit > 0:
            urea_kg = n_deficit / 0.46  # Urea is 46% N
            recommendations.append(f"{urea_kg:.0f}kg Urea")
        
        if p_deficit > 0:
            dap_kg = p_deficit / 0.46  # DAP is 46% P2O5
            recommendations.append(f"{dap_kg:.0f}kg DAP")
        
        if k_deficit > 0:
            kcl_kg = k_deficit / 0.60  # KCl is 60% K2O
            recommendations.append(f"{kcl_kg:.0f}kg Potash (KCl)")
        
        if not recommendations:
            return "Soil nutrients are adequate. Apply maintenance fertilizer only."
        
        return " + ".join(recommendations) + " per hectare"

# Utility functions for data cleaning
def clean_phone_number(phone: str) -> str:
    '''Standardize phone number format for Rwanda'''
    # Remove spaces, dashes, parentheses
    cleaned = ''.join(filter(str.isdigit, phone))
    
    # Rwanda phone numbers: +250 XXX XXX XXX
    if cleaned.startswith('250'):
        return '+' + cleaned
    elif cleaned.startswith('0'):
        return '+250' + cleaned[1:]
    else:
        return '+250' + cleaned

def validate_location(district: str, sector: str = None) -> bool:
    '''Validate if location is in Rwanda'''
    # Rwanda districts (simplified list)
    RWANDA_DISTRICTS = [
        'Kamonyi', 'Rwamagana', 'Nyarugenge', 'Gasabo', 'Kicukiro',
        'Nyanza', 'Gisagara', 'Nyamagabe', 'Nyaruguru', 'Huye',
        'Muhanga', 'Ruhango', 'Bugesera', 'Gatsibo', 'Kayonza',
        'Kirehe', 'Ngoma', 'Rwamagan', 'Burera', 'Gakenke',
        'Gicumbi', 'Musanze', 'Rulindo', 'Karongi', 'Ngororero',
        'Nyabihu', 'Nyamasheke', 'Rubavu', 'Rusizi', 'Rutsiro'
    ]

    return district in RWANDA_DISTRICTS and (sector is None or sector in RWANDA_SECTORS)