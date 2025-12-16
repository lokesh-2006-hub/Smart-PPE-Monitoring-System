import requests
import time
import json

API_URL = "http://localhost:8000/api/attendance/rfid"

def simulate_scan(tag_id):
    print(f"🔹 Simulating scan for Tag: {tag_id}")
    
    payload = {
        "rfid_tag": tag_id,
        "timestamp": int(time.time()),
        "gate": "Simulation Gate"
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print(f"✅ SUCCESS: Attendance Marked for {data.get('worker_name')}")
                print(f"   Action: {data.get('action')}")
            elif data.get("status") == "error":
                print(f"⚠️  UNKNOWN TAG: The backend received the tag but didn't find a worker.")
                print(f"   Message: {data.get('message')}")
        else:
            print(f"❌ Server Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    # 1. Simulate an unknown tag
    simulate_scan("UNKNOWN_TAG_123")
    
    print("\n--- To make this work, we need to link a tag to a worker ---\n")
    
    # 2. You would normally do this in the UI or DB, but let's pretend we have a valid tag
    # For this simulation to show 'SUCCESS', you need a worker with this tag in the DB.
    # I will try to scan a tag that might exist or just show the unknown one.
    simulate_scan("TEST_TAG_001")
