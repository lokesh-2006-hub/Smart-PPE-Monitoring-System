import requests

# Test attendance logs API
print("Testing /api/attendance/logs endpoint...")
response = requests.get("http://localhost:8000/api/attendance/logs", params={"limit": 5})

if response.status_code == 200:
    logs = response.json()
    print(f"\n✅ Got {len(logs)} attendance logs")
    
    if logs:
        print("\nFirst log fields:")
        first_log = logs[0]
        for key in first_log.keys():
            print(f"  - {key}: {first_log[key]}")
        
        print(f"\n📋 Employee ID present? {'employee_id' in first_log}")
        print(f"📋 Worker ID present? {'worker_id' in first_log}")
        
        if 'employee_id' in first_log:
            print(f"✅ Employee ID value: {first_log['employee_id']}")
        else:
            print("❌ Employee ID NOT in response!")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

# Test alerts API
print("\n" + "="*50)
print("Testing /api/alerts endpoint...")
response = requests.get("http://localhost:8000/api/alerts", params={"limit": 5})

if response.status_code == 200:
    alerts = response.json()
    print(f"\n✅ Got {len(alerts)} alerts")
    
    if alerts:
        print("\nFirst alert fields:")
        first_alert = alerts[0]
        for key in first_alert.keys():
            print(f"  - {key}: {first_alert[key]}")
        
        print(f"\n📋 Employee ID present? {'employee_id' in first_alert}")
        print(f"📋 Worker ID present? {'worker_id' in first_alert}")
        
        if 'employee_id' in first_alert:
            print(f"✅ Employee ID value: {first_alert['employee_id']}")
        else:
            print("❌ Employee ID NOT in response!")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
