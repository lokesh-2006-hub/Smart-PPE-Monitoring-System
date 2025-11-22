import mysql.connector
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

print("=== Checking Alerts ===\n")

# Check recent alerts
cursor.execute("SELECT * FROM alerts ORDER BY created_at DESC LIMIT 10")
alerts = cursor.fetchall()

if alerts:
    print(f"Found {len(alerts)} recent alerts:\n")
    for alert in alerts:
        print(f"ID: {alert['id']}")
        print(f"Worker ID: {alert['worker_id']}")
        print(f"Type: {alert['type']}")
        print(f"Severity: {alert['severity']}")
        print(f"Message: {alert['message']}")
        print(f"Status: {alert['status']}")
        print(f"Created: {alert['created_at']}")
        print("-" * 50)
else:
    print("❌ No alerts found in database!")

# Check workers table
print("\n=== Checking Workers ===\n")
cursor.execute("SELECT id, name, status FROM workers")
workers = cursor.fetchall()

if workers:
    print(f"Found {len(workers)} workers:\n")
    for worker in workers:
        print(f"ID: {worker['id']}, Name: {worker['name']}, Status: {worker['status']}")
else:
    print("❌ No workers found!")

cursor.close()
conn.close()
