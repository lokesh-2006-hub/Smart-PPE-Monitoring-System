import mysql.connector
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME", "ppe")
)

cursor = conn.cursor(dictionary=True)

print("=== BEFORE TEST REQUEST ===\n")

print("1. Workers Table:")
cursor.execute("SELECT id, name, status FROM workers")
for w in cursor.fetchall():
    print(f"   ID={w['id']}, Name='{w['name']}', Status={w['status']}")

print("\n2. Latest Attendance:")
cursor.execute("SELECT id, person_id, person_name FROM attendance WHERE person_name='lokesh' ORDER BY id DESC LIMIT 1")
att = cursor.fetchone()
if att:
    print(f"   Attendance ID={att['id']}, person_id={att['person_id']}, name='{att['person_name']}'")

print("\n3. Alerts Count:")
cursor.execute("SELECT COUNT(*) as cnt FROM alerts")
print(f"   Total alerts: {cursor.fetchone()['cnt']}")

print("\n" + "="*50)
print("SENDING TEST REQUEST...")
print("="*50 + "\n")

# Send test request
payload = {
    "name": "lokesh",
    "status": "fail",
    "helmet": False,
    "glass": False,
    "sheao": False,
    "glows": False,
    "headphone": False,
    "jacket": False,
    "source": "Test Gate"
}

print(f"Payload: {json.dumps(payload, indent=2)}\n")
response = requests.post("http://localhost:8000/update_attendance", json=payload)
print(f"Response: {response.status_code} - {response.json()}\n")

print("=== AFTER TEST REQUEST ===\n")

print("1. Workers Table:")
cursor.execute("SELECT id, name, status FROM workers")
for w in cursor.fetchall():
    print(f"   ID={w['id']}, Name='{w['name']}', Status={w['status']}")

print("\n2. Latest Attendance:")
cursor.execute("SELECT id, person_id, person_name FROM attendance WHERE person_name='lokesh' ORDER BY id DESC LIMIT 1")
att = cursor.fetchone()
if att:
    print(f"   Attendance ID={att['id']}, person_id={att['person_id']}, name='{att['person_name']}'")
    # Check if worker with that ID exists
    cursor.execute("SELECT id, name FROM workers WHERE id = %s", (att['person_id'],))
    worker = cursor.fetchone()
    if worker:
        print(f"   ✅ Worker with ID={worker['id']} exists: '{worker['name']}'")
    else:
        print(f"   ❌ No worker with ID={att['person_id']}")

print("\n3. Alerts:")
cursor.execute("SELECT id, worker_id, message FROM alerts ORDER BY created_at DESC LIMIT 3")
alerts = cursor.fetchall()
if alerts:
    for a in alerts:
        print(f"   Alert ID={a['id']}, worker_id={a['worker_id']}, Message='{a['message']}'")
else:
    print("   ❌ NO ALERTS")

cursor.close()
conn.close()
