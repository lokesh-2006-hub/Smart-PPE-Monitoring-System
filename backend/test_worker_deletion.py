import requests
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"

print("=== Testing Complete Worker Deletion ===\n")

# First, let's see what workers exist
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME", "ppe")
)
cursor = conn.cursor(dictionary=True)

print("1. Current Workers:")
cursor.execute("SELECT id, name, status FROM workers")
workers = cursor.fetchall()
for w in workers:
    print(f"   ID: {w['id']}, Name: {w['name']}, Status: {w['status']}")

if not workers:
    print("   No workers found!")
    cursor.close()
    conn.close()
    exit()

# Select the first worker for testing
test_worker = workers[0]
test_worker_id = test_worker['id']
test_worker_name = test_worker['name']

print(f"\n2. Testing deletion of Worker ID {test_worker_id} ({test_worker_name})")

# Check what data exists for this worker BEFORE deletion
cursor.execute("SELECT COUNT(*) as cnt FROM alerts WHERE worker_id = %s", (test_worker_id,))
alert_count = cursor.fetchone()['cnt']
print(f"   - Alerts: {alert_count}")

cursor.execute("SELECT COUNT(*) as cnt FROM attendance WHERE person_id = %s", (test_worker_id,))
attendance_count = cursor.fetchone()['cnt']
print(f"   - Attendance records: {attendance_count}")

cursor.close()
conn.close()

# Now delete via API
print(f"\n3. Calling DELETE API...")
response = requests.delete(f"{BASE_URL}/api/workers/{test_worker_id}")

if response.status_code == 200:
    result = response.json()
    print(f"   ✅ SUCCESS!")
    print(f"   Message: {result['message']}")
    print(f"   Details:")
    print(f"     - Alerts deleted: {result['details']['alerts_deleted']}")
    print(f"     - Attendance deleted: {result['details']['attendance_deleted']}")
    print(f"     - Photos deleted: {result['details']['photos_deleted']}")
else:
    print(f"   ❌ FAILED: {response.status_code}")
    print(f"   Error: {response.text}")

# Verify deletion
print(f"\n4. Verifying deletion...")
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME", "ppe")
)
cursor = conn.cursor(dictionary=True)

cursor.execute("SELECT COUNT(*) as cnt FROM workers WHERE id = %s", (test_worker_id,))
worker_exists = cursor.fetchone()['cnt']
print(f"   - Worker exists in DB: {'❌ YES (FAILED)' if worker_exists > 0 else '✅ NO (DELETED)'}")

cursor.execute("SELECT COUNT(*) as cnt FROM alerts WHERE worker_id = %s", (test_worker_id,))
alerts_exist = cursor.fetchone()['cnt']
print(f"   - Alerts exist: {'❌ YES (FAILED)' if alerts_exist > 0 else '✅ NO (DELETED)'}")

cursor.execute("SELECT COUNT(*) as cnt FROM attendance WHERE person_id = %s", (test_worker_id,))
attendance_exists = cursor.fetchone()['cnt']
print(f"   - Attendance exists: {'❌ YES (FAILED)' if attendance_exists > 0 else '✅ NO (DELETED)'}")

cursor.close()
conn.close()

print("\n✅ Test Complete!")
