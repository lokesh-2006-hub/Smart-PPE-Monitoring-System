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
    SELECT CONSTRAINT_NAME 
    FROM information_schema.KEY_COLUMN_USAGE 
    WHERE TABLE_NAME = 'attendance' 
    AND COLUMN_NAME = 'person_id' 
    AND REFERENCED_TABLE_NAME = 'persons'
""")
result = cursor.fetchone()
if result:
    print(f"Found FK: {result[0]}")
    # Drop it
    cursor.execute(f"ALTER TABLE attendance DROP FOREIGN KEY {result[0]}")
    conn.commit()
    print("FK dropped successfully")
else:
    print("No FK found")

conn.close()
