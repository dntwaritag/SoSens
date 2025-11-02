#!/usr/bin/env python3
'''
API Testing Script
Test all endpoints to ensure they work correctly
'''

import requests
import json

BASE_URL = 'http://localhost:5000'

def test_health_check():
    '''Test health endpoint'''
    print("\n1. Testing Health Check...")
    response = requests.get(f'{BASE_URL}/api/health')
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

def test_register_farmer():
    '''Test farmer registration'''
    print("\n2. Testing Farmer Registration...")
    data = {
        'name': 'Test Farmer',
        'phone_number': '0788999999',
        'district': 'Kamonyi',
        'sector': 'Musambira',
        'farm_size': 0.5
    }
    response = requests.post(f'{BASE_URL}/api/farmers', json=data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    return response.json().get('farmer', {}).get('id')

def test_soil_reading(farmer_id):
    '''Test soil reading submission'''
    print("\n3. Testing Soil Reading Submission...")
    data = {
        'farmer_id': farmer_id,
        'ph': 6.5,
        'nitrogen': 40,
        'phosphorus': 20,
        'potassium': 200,
        'reading_source': 'manual'
    }
    response = requests.post(f'{BASE_URL}/api/soil-readings', json=data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

def test_prediction(farmer_id):
    '''Test crop prediction'''
    print("\n4. Testing Crop Prediction...")
    data = {
        'farmer_id': farmer_id,
        'ph': 6.5,
        'nitrogen': 40,
        'phosphorus': 20,
        'potassium': 200
    }
    response = requests.post(f'{BASE_URL}/api/predict', json=data)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Recommended Crop: {result.get('prediction', {}).get('crop')}")
    print(f"   Confidence: {result.get('prediction', {}).get('confidence_percent')}")
    print(f"   Soil Health: {result.get('soil_health', {}).get('status')}")

def test_list_crops():
    '''Test crop listing'''
    print("\n5. Testing Crop Listing...")
    response = requests.get(f'{BASE_URL}/api/crops')
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Total Crops: {result.get('total_crops')}")
    print(f"   Crops: {', '.join(result.get('crops', [])[:5])}...")

def test_analytics():
    '''Test analytics dashboard'''
    print("\n6. Testing Analytics Dashboard...")
    response = requests.get(f'{BASE_URL}/api/analytics/dashboard')
    print(f"   Status: {response.status_code}")
    result = response.json()
    if result.get('success'):
        summary = result.get('summary', {})
        print(f"   Total Farmers: {summary.get('total_farmers')}")
        print(f"   Total Recommendations: {summary.get('total_recommendations')}")

def run_all_tests():
    '''Run all API tests'''
    print("="*80)
    print("RWANDA SOIL QUALITY MONITORING - API TESTS")
    print("="*80)
    
    try:
        test_health_check()
        farmer_id = test_register_farmer()
        
        if farmer_id:
            test_soil_reading(farmer_id)
            test_prediction(farmer_id)
        
        test_list_crops()
        test_analytics()
        
        print("\n" + "="*80)
        print(" ALL TESTS COMPLETED")
        print("="*80)
        
    except requests.exceptions.ConnectionError:
        print("\n ERROR: Cannot connect to API")
        print("Make sure the server is running: python app.py")
    except Exception as e:
        print(f"\n ERROR: {str(e)}")

if __name__ == '__main__':
    run_all_tests()