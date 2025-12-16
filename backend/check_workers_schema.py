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
try:
    cursor.execute("DESCRIBE workers")
    columns = cursor.fetchall()
    print("Workers Table Schema:")
    for col in columns:
        print(col)
except Exception as e:
    print(f"Error: {e}")

conn.close()
