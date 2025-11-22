import requests
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Clear old alerts first
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME", "ppe")
)
cursor = conn.cursor()
cursor.execute("DELETE FROM alerts WHERE worker_id IN (SELECT id FROM workers WHERE name = 'lokesh')")
conn.commit()
print(f"Deleted old alerts\n")
cursor.close()
conn.close()

# Test PPE fail - should create alert
payload = {
    "name": "lokesh",
    "status": "fail",
    "helmet": False,
    "glass": False,
    "sheao": False,
    "glows": False,  
    "headphone": False,
    "jacket": False,
    "time": None,
    "source": "Main Gate"
}

print("Sending PPE fail request...")
response = requests.post("http://localhost:8000/update_attendance", json=payload)
print(f"Response: {response.status_code} - {response.json()}\n")

# Check alerts
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME", "ppe")
)
cursor = conn.cursor(dictionary=True)

cursor.execute("SELECT * FROM alerts WHERE worker_id IN (SELECT id FROM workers WHERE name = 'lokesh') ORDER BY created_at DESC LIMIT 1")
alert = cursor.fetchone()

if alert:
    print("🚨 ALERT CREATED!")
    print(f"   ID: {alert['id']}")
    print(f"   Worker ID: {alert['worker_id']}")
    print(f"   Message: {alert['message']}")
    print(f"   Severity: {alert['severity']}")
    print(f"   Location: {alert['location']}")
else:
    print("❌ NO ALERT in database")
    
    # Check if worker exists
    cursor.execute("SELECT * FROM workers WHERE name = 'lokesh'")
    worker = cursor.fetchone()
    if worker:
        print(f"\n✅ Worker 'lokesh' exists - ID: {worker['id']}, Status: {worker['status']}")
    else:
        print("\n❌ Worker 'lokesh' NOT FOUND in workers table!")

cursor.close()
conn.close()
