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
cursor.execute("SELECT * FROM alerts WHERE worker_name LIKE 'TestWorker_%' ORDER BY created_at DESC LIMIT 5")
alerts = cursor.fetchall()

print(f"Found {len(alerts)} alerts for TestWorkers")
for a in alerts:
    print(f"ID: {a['id']}, Worker: {a['worker_name']}, Msg: {a['message']}, Created: {a['created_at']}")

conn.close()
