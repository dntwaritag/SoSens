import requests
from typing import Optional, Dict
from sqlalchemy.orm import Session
from .config import settings
from . import models

RWANDA_LOCATIONS = {
    'Kamonyi': {'lat': -2.04, 'lon': 29.92},
    'Rwamagana': {'lat': -1.95, 'lon': 30.43},
    'Kigali': {'lat': -1.95, 'lon': 30.06}
}

class WeatherService:
    def get_weather(self, district: str, db: Session) -> Optional[Dict]:
        if not settings.OPENWEATHER_API_KEY:
            return self._get_default_weather(district)
        
        coords = RWANDA_LOCATIONS.get(district, RWANDA_LOCATIONS['Kigali'])
        
        try:
            url = f"{settings.OPENWEATHER_BASE_URL}/weather"
            params = {
                'lat': coords['lat'],
                'lon': coords['lon'],
                'appid': settings.OPENWEATHER_API_KEY,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            weather_info = {
                'location': district,
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'rainfall_forecast': data.get('rain', {}).get('1h', 0),
                'advice': self._generate_advice(data)
            }
            
            return weather_info
        except:
            return self._get_default_weather(district)
    
    def _generate_advice(self, data: Dict) -> str:
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        rain = data.get('rain', {}).get('1h', 0)
        
        advice = []
        if rain > 5:
            advice.append("Heavy rain expected - delay planting if soil waterlogged")
        elif rain > 0:
            advice.append("Light rain expected - good for planting")
        else:
            advice.append("No rain expected - ensure irrigation")
        
        if temp > 28:
            advice.append("High temp - water crops early morning/evening")
        if humidity > 80:
            advice.append("High humidity - watch for fungal diseases")
        
        return ". ".join(advice)
    
    def _get_default_weather(self, district: str) -> Dict:
        return {
            'location': district,
            'temperature': 23.0,
            'humidity': 70.0,
            'description': 'Partly cloudy',
            'rainfall_forecast': 0.0,
            'advice': 'Weather data unavailable - using typical Rwanda conditions'
        }

weather_service = WeatherService()