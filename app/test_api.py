#!/usr/bin/env python3
'''
API Testing Script for FastAPI
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
    assert response.status_code == 200

def test_register_farmer():
    '''Test farmer registration'''
    print("\n2. Testing Farmer Registration...")
    data = {
        'name': 'Test Farmer FastAPI',
        'phone_number': '+250788999888',
        'district': 'Kamonyi',
        'sector': 'Musambira',
        'farm_size': 0.5
    }
    response = requests.post(f'{BASE_URL}/api/farmers', json=data)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Farmer ID: {result.get('id')}")
    print(f"   Name: {result.get('name')}")
    return result.get('id')

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
    if response.status_code == 201:
        print(f" Soil reading saved")

def test_prediction(farmer_id):
    '''Test crop prediction'''
    print("\n4. Testing Crop Prediction...")
    data = {
        'farmer_id': farmer_id,
        'Ph': 6.5,
        'N': 40,
        'P': 20,
        'K': 200
    }
    response = requests.post(f'{BASE_URL}/api/predict', json=data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f" Recommended Crop: {result['prediction']['crop']}")
        print(f" Confidence: {result['prediction']['confidence_percent']}")
        print(f" Soil Health: {result['soil_health']['status']}")
        return result.get('recommendation_id')

def test_list_farmers():
    '''Test farmer listing'''
    print("\n5. Testing Farmer Listing...")
    response = requests.get(f'{BASE_URL}/api/farmers?limit=5')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        farmers = response.json()
        print(f" Retrieved {len(farmers)} farmers")

def test_list_crops():
    '''Test crop listing'''
    print("\n6. Testing Crop Listing...")
    response = requests.get(f'{BASE_URL}/api/crops')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f" Total Crops: {result.get('total_crops')}")
        print(f" Crops: {', '.join(result.get('crops', [])[:5])}...")

def test_analytics():
    '''Test analytics dashboard'''
    print("\n7. Testing Analytics Dashboard...")
    response = requests.get(f'{BASE_URL}/api/analytics/dashboard')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        summary = result.get('summary', {})
        print(f" Total Farmers: {summary.get('total_farmers')}")
        print(f" Total Recommendations: {summary.get('total_recommendations')}")

def test_feedback(farmer_id, recommendation_id):
    '''Test feedback submission'''
    print("\n8. Testing Feedback Submission...")
    data = {
        'farmer_id': farmer_id,
        'recommendation_id': recommendation_id,
        'action_taken': True,
        'satisfaction_rating': 5,
        'comments': 'Very helpful recommendation!'
    }
    response = requests.post(f'{BASE_URL}/api/feedback', json=data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        print(f"   ✓ Feedback submitted")

def test_api_docs():
    '''Test API documentation'''
    print("\n9. Testing API Documentation...")
    response = requests.get(f'{BASE_URL}/docs')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✓ API docs available at: {BASE_URL}/docs")

def run_all_tests():
    '''Run all API tests'''
    print("="*80)
    print("RWANDA SOIL QUALITY MONITORING - FASTAPI TESTS")
    print("="*80)
    
    try:
        test_health_check()
        farmer_id = test_register_farmer()
        
        if farmer_id:
            test_soil_reading(farmer_id)
            recommendation_id = test_prediction(farmer_id)
            
            if recommendation_id:
                test_feedback(farmer_id, recommendation_id)
        
        test_list_farmers()
        test_list_crops()
        test_analytics()
        test_api_docs()
        
        print("\n" + "="*80)
        print(" ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"\n View interactive API docs at: {BASE_URL}/docs")
        print(f" View ReDoc at: {BASE_URL}/redoc")
        print("="*80)
        
    except requests.exceptions.ConnectionError:
        print("\n ERROR: Cannot connect to API")
        print("Make sure the server is running:")
        print("  python app.py")
        print("  OR")
        print("  uvicorn app:app --reload")
    except Exception as e:
        print(f"\n ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_all_tests()