#!/usr/bin/env python3
"""
Quick test script for the CreatureMind API

Run this after starting the server to test basic functionality.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api():
    """Test the CreatureMind API"""
    print("🧠 Testing CreatureMind API...")
    
    # 1. Health check
    print("\n1. Health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # 2. List templates
    print("\n2. Available templates...")
    response = requests.get(f"{BASE_URL}/templates")
    templates = response.json()["templates"]
    for template in templates:
        print(f"  - {template['id']}: {template['name']} ({template['species']})")
    
    # 3. Create a creature
    print("\n3. Creating a dog creature...")
    create_request = {
        "name": "Buddy",
        "template_id": "loyal_dog",
        "personality_traits": ["loyal", "playful", "energetic"],
        "custom_personality": "A friendly golden retriever who loves playing fetch"
    }
    
    response = requests.post(f"{BASE_URL}/creatures", json=create_request)
    creature_data = response.json()
    creature_id = creature_data["creature_id"]
    print(f"Created creature: {creature_data['name']} (ID: {creature_id})")
    print(f"Stats: {creature_data['stats']}")
    
    # 4. Send messages to the creature
    print("\n4. Chatting with the creature...")
    
    messages = [
        "Hello there, buddy!",
        "Want to play fetch?", 
        "Good dog! You're such a good boy!",
        "How are you feeling?"
    ]
    
    for message in messages:
        print(f"\n👤 User: {message}")
        
        message_request = {"message": message}
        response = requests.post(f"{BASE_URL}/creatures/{creature_id}/message", json=message_request)
        
        if response.status_code == 200:
            data = response.json()
            print(f"🐕 Creature: {data['creature_language']}")
            
            if data['can_translate'] and data['human_translation']:
                print(f"📝 Translation: {data['human_translation']}")
            else:
                print("📝 Translation: Not available (creature not in mood to translate)")
            
            print(f"😊 Emotion: {data['emotional_state']}")
            
            if data['stats_delta']:
                print(f"📊 Stats changed: {data['stats_delta']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
        
        time.sleep(1)  # Brief pause between messages
    
    # 5. Perform activities
    print("\n5. Performing activities...")
    
    activities = [
        {"activity": "pet", "parameters": {}},
        {"activity": "feed", "parameters": {"food_type": "treats"}},
        {"activity": "play", "parameters": {"toy": "ball"}}
    ]
    
    for activity_request in activities:
        activity_name = activity_request["activity"]
        print(f"\n🎮 Activity: {activity_name}")
        
        response = requests.post(f"{BASE_URL}/creatures/{creature_id}/activity", json=activity_request)
        
        if response.status_code == 200:
            data = response.json()
            print(f"🐕 Creature: {data['creature_language']}")
            
            if data['can_translate'] and data['human_translation']:
                print(f"📝 Translation: {data['human_translation']}")
            
            if data['stats_delta']:
                print(f"📊 Stats changed: {data['stats_delta']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
        
        time.sleep(1)
    
    # 6. Check final status
    print("\n6. Final creature status...")
    response = requests.get(f"{BASE_URL}/creatures/{creature_id}/status")
    status = response.json()
    print(f"Name: {status['name']}")
    print(f"Mood: {status['mood']}")
    print(f"Stats: {status['stats']}")
    print(f"Can translate: {status['can_translate']}")
    print(f"Memories: {status['memory_count']}")
    
    print("\n✅ API test completed!")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to CreatureMind API.")
        print("Make sure the server is running: python -m api.server")
    except Exception as e:
        print(f"❌ Test failed: {e}")