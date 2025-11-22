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

print("=== Workers Table ===")
cursor.execute("SELECT id, name, employee_id FROM workers ORDER BY id")
workers = cursor.fetchall()

for w in workers:
    print(f"ID: {w['id']}, Name: {w['name']}, Employee ID: {w['employee_id']}")

print(f"\nTotal workers: {len(workers)}")

cursor.close()
conn.close()
