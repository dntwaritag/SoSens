import requests
import os
from typing import Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
import models

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
OPENWEATHER_BASE_URL = os.getenv('OPENWEATHER_BASE_URL', 'https://api.openweathermap.org/data/2.5')

# Rwanda district coordinates (major agricultural areas)
RWANDA_LOCATIONS = {
    'Kamonyi': {'lat': -2.04, 'lon': 29.92},
    'Rwamagana': {'lat': -1.95, 'lon': 30.43},
    'Kigali': {'lat': -1.95, 'lon': 30.06},
    'Huye': {'lat': -2.59, 'lon': 29.74},
    'Musanze': {'lat': -1.50, 'lon': 29.63}
}

class WeatherService:
    """Handle weather data fetching and caching"""
    
    def __init__(self, api_key: str = OPENWEATHER_API_KEY):
        self.api_key = api_key
        self.base_url = OPENWEATHER_BASE_URL
    
    def get_weather(self, district: str, db: Session) -> Optional[Dict]:
        """Get current weather for a district"""
        
        if not self.api_key:
            return self._get_default_weather(district)
        
        # Get coordinates
        coords = RWANDA_LOCATIONS.get(district, RWANDA_LOCATIONS['Kigali'])
        
        try:
            # Fetch current weather
            url = f"{self.base_url}/weather"
            params = {
                'lat': coords['lat'],
                'lon': coords['lon'],
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Parse weather data
            weather_info = {
                'location': district,
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'rainfall': data.get('rain', {}).get('1h', 0),
                'wind_speed': data['wind']['speed'],
                'advice': self._generate_advice(data)
            }
            
            # Cache in database
            self._cache_weather(db, district, weather_info, data)
            
            return weather_info
            
        except Exception as e:
            print(f"Weather API error: {e}")
            return self._get_cached_weather(db, district) or self._get_default_weather(district)
    
    def _generate_advice(self, weather_data: Dict) -> str:
        """Generate farming advice based on weather"""
        temp = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        rain = weather_data.get('rain', {}).get('1h', 0)
        
        advice = []
        
        if rain > 5:
            advice.append("Heavy rain expected. Delay planting if soil is waterlogged.")
        elif rain > 0:
            advice.append("Light rain expected. Good conditions for planting.")
        else:
            advice.append("No rain expected. Ensure adequate irrigation.")
        
        if temp > 28:
            advice.append("High temperatures. Water crops early morning or evening.")
        elif temp < 15:
            advice.append("Cool weather. Some crops may grow slower.")
        
        if humidity > 80:
            advice.append("High humidity. Watch for fungal diseases.")
        elif humidity < 40:
            advice.append("Low humidity. Increase watering frequency.")
        
        return " ".join(advice)
    
    def _cache_weather(self, db: Session, location: str, weather_info: Dict, raw_data: Dict):
        """Cache weather data in database"""
        try:
            weather_record = models.WeatherData(
                location=location,
                temperature=weather_info['temperature'],
                humidity=weather_info['humidity'],
                rainfall=weather_info.get('rainfall', 0),
                wind_speed=weather_info.get('wind_speed', 0),
                description=weather_info['description'],
                weather_data=raw_data,
                recorded_at=datetime.utcnow()
            )
            db.add(weather_record)
            db.commit()
        except:
            pass
    
    def _get_cached_weather(self, db: Session, location: str) -> Optional[Dict]:
        """Get cached weather data"""
        weather = db.query(models.WeatherData).filter(
            models.WeatherData.location == location
        ).order_by(models.WeatherData.recorded_at.desc()).first()
        
        if weather:
            return {
                'location': weather.location,
                'temperature': weather.temperature,
                'humidity': weather.humidity,
                'description': weather.description,
                'rainfall': weather.rainfall,
                'advice': "Using cached weather data."
            }
        return None
    
    def _get_default_weather(self, district: str) -> Dict:
        """Return default Rwanda weather"""
        return {
            'location': district,
            'temperature': 23.0,
            'humidity': 70.0,
            'description': 'Partly cloudy',
            'rainfall': 0.0,
            'advice': 'Weather data unavailable. Using typical Rwanda conditions.'
        }