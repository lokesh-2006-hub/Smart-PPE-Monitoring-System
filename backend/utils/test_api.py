import requests
import json
import time

URL = "http://127.0.0.1:8000/update_attendance"

# Sample data mimicking a detection
payload = {
    "name": "TestWorker_01",
    "time": int(time.time()),
    "status": "pass",
    "source": "camera",  # can be: camera, video, image, or folder
    "helmet": True,
    "glows": True,
    "sheao": True,
    "glass": False,
    "jacket": True,
    "headphone": False
}

try:
    print(f"Sending POST request to {URL}...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(URL, json=payload)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("\nSUCCESS! The data was sent to the backend.")
        print("Check your Dashboard (http://localhost:5173) - 'TestWorker_01' should appear shortly.")
    else:
        print("\nFAILED. Check backend logs.")

except Exception as e:
    print(f"\nError: {e}")
    print("Is the backend running on port 8000?")
