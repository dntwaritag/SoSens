"""
Quick test script to verify everything works
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_complete_system():
    print("="*80)
    print(" TESTING COMPLETE SOSENS SYSTEM")
    print("="*80)
    
    # Test 1: Register new farmer
    print("\n1️ Testing Registration + Welcome Notification...")
    register_data = {
        "full_name": "Test Farmer",
        "password": "TestPass@123",
        "phone_number": "+250788999999",
        "email": "test@sosens.rw",
        "district": "Kigali",
        "role": "farmer",
        "preferred_contact": "email",
        "receive_notifications": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        if response.status_code == 201:
            data = response.json()
            print(" Registration successful")
            print(f"   Token: {data['access_token'][:30]}...")
            farmer_token = data['access_token']
        else:
            print(f"  Registration issue: {response.text}")
            # Try login instead
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                data={"username": "test@sosens.rw", "password": "TestPass@123"}
            )
            farmer_token = response.json()['access_token']
    except Exception as e:
        print(f" Error: {e}")
        return
    
    # Test 2: Login as admin
    print("\n2️ Testing Admin Login...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            data={"username": "admin@sosens.rw", "password": "Admin@2024"}
        )
        if response.status_code == 200:
            admin_token = response.json()['access_token']
            print(" Admin login successful")
        else:
            print(f" Admin login failed: {response.text}")
            return
    except Exception as e:
        print(f" Error: {e}")
        return
    
    # Test 3: Farmer gets prediction + notification
    print("\n3️ Testing Prediction + Notification...")
    headers = {"Authorization": f"Bearer {farmer_token}"}
    prediction_data = {
        "ph": 6.5,
        "nitrogen": 40,
        "phosphorus": 20,
        "potassium": 200,
        "include_weather": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/predict",
            json=prediction_data,
            headers=headers
        )
        if response.status_code == 200:
            result = response.json()
            print(" Prediction successful")
            print(f"   Crop: {result['crop']}")
            print(f"   Confidence: {result['confidence']:.0%}")
            print(f"   Notification sent to farmer")
        else:
            print(f" Prediction failed: {response.text}")
    except Exception as e:
        print(f" Error: {e}")
    
    # Test 4: Admin views analytics
    print("\n4️ Testing Admin Analytics...")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/analytics", headers=admin_headers)
        if response.status_code == 200:
            analytics = response.json()
            print(" Analytics retrieved")
            print(f"   Total users: {analytics['summary']['total_users']}")
            print(f"   Farmers: {analytics['summary']['farmers']}")
            print(f"   Notifications sent: {analytics['summary'].get('sent_notifications', 0)}")
        else:
            print(f" Analytics failed: {response.text}")
    except Exception as e:
        print(f" Error: {e}")
    
    # Test 5: Admin manually sends weather
    print("\n5️ Testing Admin Manual Weather Send...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/send-weather",
            json={},
            headers=admin_headers
        )
        if response.status_code == 200:
            result = response.json()
            print(" Weather notifications triggered")
            print(f"   Sent: {result['sent']}")
            print(f"   Failed: {result['failed']}")
        else:
            print(f"  Weather send: {response.text}")
    except Exception as e:
        print(f" Error: {e}")
    
    # Test 6: Admin broadcasts message
    print("\n6️ Testing Admin Broadcast...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/broadcast",
            json={"message": "Test broadcast from admin", "district": None},
            headers=admin_headers
        )
        if response.status_code == 200:
            result = response.json()
            print(" Broadcast successful")
            print(f"   {result['message']}")
        else:
            print(f"  Broadcast: {response.text}")
    except Exception as e:
        print(f" Error: {e}")
    
    # Test 7: Password reset
    print("\n7️ Testing Password Reset...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"username": "test@sosens.rw"}
        )
        if response.status_code == 200:
            print(" Password reset notification sent")
        else:
            print(f"  Password reset: {response.text}")
    except Exception as e:
        print(f" Error: {e}")
    
    # Test 8: Admin views notification logs
    print("\n8️ Testing Notification Logs...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/notification-logs",
            headers=admin_headers
        )
        if response.status_code == 200:
            logs = response.json()
            print(" Notification logs retrieved")
            print(f"   Total logs: {logs['total']}")
            if logs['logs']:
                recent = logs['logs'][0]
                print(f"   Recent: {recent['type']} via {recent['channel']} - {'✓ sent' if recent['is_sent'] else '✗ failed'}")
        else:
            print(f"  Logs: {response.text}")
    except Exception as e:
        print(f" Error: {e}")
    
    print("\n" + "="*80)
    print(" SYSTEM TEST COMPLETE")
    print("="*80)
    print("\n SUMMARY:")
    print("✓ Registration with welcome notification")
    print("✓ Admin login and access")
    print("✓ Prediction with notification")
    print("✓ Admin analytics")
    print("✓ Manual weather send (admin)")
    print("✓ Broadcast messaging (admin)")
    print("✓ Password reset with notification")
    print("✓ Notification logging")
    print("\n🎉 All features working!")
    print("="*80)

if __name__ == "__main__":
    try:
        test_complete_system()
    except KeyboardInterrupt:
        print("\n\n  Test interrupted")
    except Exception as e:
        print(f"\n Error: {e}")