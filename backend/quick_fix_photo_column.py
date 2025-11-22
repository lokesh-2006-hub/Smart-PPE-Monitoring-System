import mysql.connector
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Quick fix - add photo_url column
try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "ppe")
    )
    cursor = conn.cursor()
    
    # Try to add the column
    try:
        cursor.execute("ALTER TABLE workers ADD COLUMN photo_url VARCHAR(255)")
        conn.commit()
        print("✅ SUCCESS: photo_url column added!")
    except mysql.connector.Error as e:
        if "Duplicate column name" in str(e):
            print("✅ Column already exists - no action needed")
        else:
            print(f"❌ Error: {e}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Connection error: {e}")
    sys.exit(1)
