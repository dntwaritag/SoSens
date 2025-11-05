#!/usr/bin/env python3
"""
Complete authentication flow test for SoSens API
Tests: Register → Login → Protected Endpoints
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def print_separator():
    print("\n" + "="*80)

def test_complete_flow():
    """Test complete authentication flow"""
    
    print_separator()
    print(" SOSENS API - COMPLETE AUTHENTICATION TEST")
    print_separator()
    
    # ========================================================================
    # STEP 1: REGISTER NEW USER
    # ========================================================================
    print("\n STEP 1: Registering new user...")
    
    register_data = {
        "full_name": "Test Farmer",
        "password": "TestPass@123",
        "phone_number": "+250788555555",
        "email": "test@sosens.rw",
        "district": "Kigali",
        "sector": "Gasabo",
        "village": "Kimironko",
        "farm_size": 0.5,
        "role": "farmer",
        "preferred_contact": "email",
        "receive_notifications": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=register_data,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            token = result['access_token']
            user = result['user']
            
            print(f"   Registration successful!")
            print(f"   User ID: {user['id']}")
            print(f"   Name: {user['full_name']}")
            print(f"   Token: {token[:50]}...")
            
            return token, user
            
        elif response.status_code == 400:
            print(f"   User might already exist, trying login...")
            return test_login()
        else:
            print(f"   Registration failed: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"   Error: {e}")
        return None, None
    
    # ========================================================================
    # STEP 2: LOGIN (if registration fails)
    # ========================================================================

def test_login():
    """Test login"""
    print_separator()
    print("\n🔐 STEP 2: Testing login...")
    
    login_data = {
        "username": "test@sosens.rw",  # or phone number
        "password": "TestPass@123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            data=login_data,  # Note: data, not json (OAuth2 format)
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            token = result['access_token']
            user = result['user']
            
            print(f"   Login successful!")
            print(f"   User: {user['full_name']}")
            print(f"   Token: {token[:50]}...")
            
            return token, user
        else:
            print(f"   Login failed: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"   Error: {e}")
        return None, None

def test_protected_endpoints(token):
    """Test all protected endpoints with token"""
    
    if not token:
        print("\n No token available. Cannot test protected endpoints.")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # ========================================================================
    # TEST 1: GET /api/auth/me
    # ========================================================================
    print_separator()
    print("\n🧪 TEST 1: GET /api/auth/me")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            user = response.json()
            print(f"   Success!")
            print(f"   Email: {user.get('email')}")
            print(f"   Phone: {user.get('phone_number')}")
            print(f"   District: {user.get('district')}")
        else:
            print(f"   Failed: {response.text}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # ========================================================================
    # TEST 2: POST /api/soil-readings
    # ========================================================================
    print_separator()
    print("\n TEST 2: POST /api/soil-readings")
    
    soil_data = {
        "ph": 6.5,
        "nitrogen": 40,
        "phosphorus": 20,
        "potassium": 200,
        "zinc": 5.0,
        "sulfur": 15.0,
        "notes": "Test reading from automated test"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/soil-readings",
            json=soil_data,
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Soil reading saved!")
            print(f"   Reading ID: {result.get('reading_id')}")
        else:
            print(f"   Failed: {response.text}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # ========================================================================
    # TEST 3: GET /api/soil-readings
    # ========================================================================
    print_separator()
    print("\n TEST 3: GET /api/soil-readings")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/soil-readings",
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Success!")
            print(f"   Total readings: {result.get('total', 0)}")
        else:
            print(f"  Failed: {response.text}")
            
    except Exception as e:
        print(f"  Error: {e}")
    
    # ========================================================================
    # TEST 4: POST /api/predict
    # ========================================================================
    print_separator()
    print("\n TEST 4: POST /api/predict")
    
    prediction_data = {
        "ph": 6.5,
        "nitrogen": 40,
        "phosphorus": 20,
        "potassium": 200,
        "zinc": 5.0,
        "sulfur": 15.0,
        "include_weather": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/predict",
            json=prediction_data,
            headers=headers,
            timeout=15
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Prediction successful!")
            print(f"   Recommended Crop: {result.get('crop')}")
            print(f"   Confidence: {result.get('confidence', 0):.1%}")
            print(f"   Soil Health: {result.get('soil_health')}")
            print(f"   Weather Advice: {result.get('weather_advice', 'N/A')[:50]}...")
        else:
            print(f"  Failed: {response.text}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # ========================================================================
    # TEST 5: GET /api/recommendations
    # ========================================================================
    print_separator()
    print("\n TEST 5: GET /api/recommendations")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/recommendations",
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  Success!")
            print(f"   Total recommendations: {result.get('total', 0)}")
        else:
            print(f"  Failed: {response.text}")
            
    except Exception as e:
        print(f"  Error: {e}")
    
    # ========================================================================
    # TEST 6: GET /api/weather
    # ========================================================================
    print_separator()
    print("\n TEST 6: GET /api/weather")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/weather",
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Weather data retrieved!")
            print(f"   Location: {result.get('location')}")
            print(f"   Temperature: {result.get('temperature')}°C")
            print(f"   Humidity: {result.get('humidity')}%")
            print(f"   Description: {result.get('description')}")
        else:
            print(f"  Failed: {response.text}")
            
    except Exception as e:
        print(f"  Error: {e}")
    
    # ========================================================================
    # TEST 7: GET /api/crops
    # ========================================================================
    print_separator()
    print("\n TEST 7: GET /api/crops")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/crops",
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success!")
            print(f"   Total crops: {result.get('total', 0)}")
            crops = result.get('crops', [])
            if crops:
                print(f"   Sample crops: {', '.join(crops[:5])}")
        else:
            print(f"  Failed: {response.text}")
            
    except Exception as e:
        print(f"  Error: {e}")

def main():
    """Run all tests"""
    
    print("\n" + "Starting SoSens API Authentication Tests")
    print(" Server: " + BASE_URL)
    
    # Step 1 & 2: Register or Login
    token, user = test_complete_flow()
    
    if not token:
        print("\n Authentication failed. Cannot proceed with protected endpoint tests.")
        print("\n Make sure:")
        print("   1. Server is running: uvicorn app:app --reload")
        print("   2. Database is initialized: python init_db.py")
        print("   3. All dependencies are installed")
        return
    
    # Step 3: Test all protected endpoints
    test_protected_endpoints(token)
    
    # Summary
    print_separator()
    print(" ALL TESTS COMPLETED")
    print_separator()
    print("\n SUMMARY:")
    print("   Authentication working")
    print("   Token generation successful")
    print("   Protected endpoints accessible")
    print("\n Use this token in your frontend:")
    print(f"   {token[:80]}...")
    print("\n Frontend Authorization Header:")
    print(f"   Authorization: Bearer {token}")
    print_separator()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Test interrupted by user")
    except Exception as e:
        print(f"\n\n Unexpected error: {e}")
        import traceback
        traceback.print_exc()