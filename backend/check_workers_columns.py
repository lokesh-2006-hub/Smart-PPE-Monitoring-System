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
    cursor.execute("SHOW COLUMNS FROM workers")
    columns = cursor.fetchall()
    print(f"{'Field':<20} {'Type':<20} {'Null':<10} {'Key':<10}")
    print("-" * 60)
    for col in columns:
        # col is a tuple: (Field, Type, Null, Key, Default, Extra)
        print(f"{col[0]:<20} {col[1]:<20} {col[2]:<10} {col[3]:<10}")
except Exception as e:
    print(f"Error: {e}")

conn.close()
