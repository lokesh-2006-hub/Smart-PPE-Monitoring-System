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

# Add a test worker with an RFID tag
try:
    cursor.execute("""
        INSERT INTO workers (employee_id, name, department, rfid_tag, status)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE rfid_tag = VALUES(rfid_tag)
    """, ("TEST001", "Test Worker", "Engineering", "TEST_TAG_001", "inactive"))
    
    conn.commit()
    print("✅ Test worker added successfully!")
    print("   Employee ID: TEST001")
    print("   Name: Test Worker")
    print("   RFID Tag: TEST_TAG_001")
    
except mysql.connector.IntegrityError as e:
    if "employee_id" in str(e):
        print("Worker already exists. Updating RFID tag...")
        cursor.execute("UPDATE workers SET rfid_tag = 'TEST_TAG_001' WHERE employee_id = 'TEST001'")
        conn.commit()
        print("✅ Updated existing worker with RFID tag")
    else:
        print(f"Error: {e}")
        
finally:
    cursor.close()
    conn.close()
