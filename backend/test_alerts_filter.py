import requests

try:
    print("Testing GET /api/alerts?status=active")
    response = requests.get("http://localhost:8000/api/alerts", params={"status": "active", "limit": 50})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        alerts = response.json()
        print(f"Got {len(alerts)} active alerts")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
