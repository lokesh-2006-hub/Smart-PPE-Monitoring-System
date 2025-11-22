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

print("Testing direct alert insertion...")

try:
    cursor.execute("""
        INSERT INTO alerts 
        (worker_id, worker_name, type, severity, message, location, gate, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
    """, (
        7,  # lokesh's worker_id
        'lokesh',  # worker_name
        'ppe_violation',
        'high',
        'TEST: PPE Violation: Missing helmet, gloves',
        'Test Gate',
        'Test Gate',
        'active'
    ))
    conn.commit()
    print("✅ Alert inserted successfully!")
    
    # Check if it was created
    cursor.execute("SELECT * FROM alerts ORDER BY created_at DESC LIMIT 1")
    alert = cursor.fetchone()
    if alert:
        print(f"\n📋 Created Alert:")
        print(f"   ID: {alert['id']}")
        print(f"   Worker ID: {alert['worker_id']}")
        print(f"   Worker Name: {alert['worker_name']}")
        print(f"   Message: {alert['message']}")
        print(f"   Severity: {alert['severity']}")
        print(f"   Location: {alert['location']}")
        print(f"   Gate: {alert['gate']}")
        print(f"   Status: {alert['status']}")
    
except mysql.connector.Error as e:
    print(f"❌ ERROR: {e}")
finally:
    cursor.close()
    conn.close()
