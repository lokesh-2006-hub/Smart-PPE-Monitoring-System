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
cursor = conn.cursor()
cursor.execute("""
    SELECT CONSTRAINT_NAME, REFERENCED_TABLE_NAME 
    FROM information_schema.KEY_COLUMN_USAGE 
    WHERE TABLE_NAME = 'alerts' 
    AND COLUMN_NAME = 'worker_id' 
    AND REFERENCED_TABLE_NAME IS NOT NULL
""")
results = cursor.fetchall()
if results:
    print("Found FKs on alerts.worker_id:")
    for r in results:
        print(f"  - {r[0]} -> {r[1]}")
else:
    print("No FKs on alerts.worker_id")

conn.close()
