import requests

try:
    response = requests.get("http://localhost:8000/api/alerts")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        alerts = response.json()
        print(f"Got {len(alerts)} alerts")
        if len(alerts) > 0:
            print(alerts[0])
    else:
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
