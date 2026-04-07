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

print("=== Attendance vs Workers IDs ===\n")
cursor.execute("""
    SELECT a.id, a.person_id, a.person_name, w.id as worker_table_id, w.status
    FROM attendance a 
    LEFT JOIN workers w ON w.name = a.person_name 
    ORDER BY a.id DESC 
    LIMIT 10
""")

for row in cursor.fetchall():
    match = "✅ MATCH" if row['person_id'] == row['worker_table_id'] else "❌ MISMATCH"
    print(f"Attendance.id: {row['id']}, person_id: {row['person_id']}, name: '{row['person_name']}', worker.id: {row['worker_table_id']}, {match}")

print("\n=== Checking Alerts ===\n")
cursor.execute("SELECT * FROM alerts ORDER BY created_at DESC LIMIT 5")
alerts = cursor.fetchall()

if alerts:
    for alert in alerts:
        print(f"Alert ID: {alert['id']}, Worker: {alert['worker_id']}, Message: {alert['message']}")
else:
    print("❌ NO ALERTS FOUND")
query="UPDATE workers SET address = '2,gopal street' WHERE name='lokesh'"
cursor.execute(query)
conn.commit()
cursor.close()
conn.close()
