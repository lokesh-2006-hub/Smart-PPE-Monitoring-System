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

print("Checking alerts table structure...\n")

cursor.execute("SHOW COLUMNS FROM alerts")
columns = cursor.fetchall()

for col in columns:
    field_name = col[0]
    field_type = col[1]
    print(f"{field_name}: {field_type}")

cursor.close()
conn.close()
