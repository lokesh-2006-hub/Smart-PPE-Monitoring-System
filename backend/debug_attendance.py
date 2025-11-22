import requests
import json
import datetime

url = "http://localhost:8000/update_attendance"

# Test case 1: Existing worker
payload_existing = {
    "name": "augustin",
    "status": "pass",
    "ppe_status": {"helmet": True, "vest": True, "gloves": True, "boots": True},
    "source": "Test Script"
}

# Test case 2: New worker (should trigger auto-creation)
payload_new = {
    "name": "TestWorker_" + datetime.datetime.now().strftime("%H%M%S"),
    "status": "fail",
    "ppe_status": {"helmet": False, "vest": True},
    "source": "Test Script"
}

def send_update(payload):
    print(f"\nSending update for {payload['name']}...")
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
        else:
            print("Success!")
    except Exception as e:
        print(f"Error: {e}")

print("Testing update_attendance...")
send_update(payload_existing)
send_update(payload_new)
