import mysql.connector
import requests
import sys
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
DB_CONFIG = {
    'host': os.getenv("DB_HOST", "localhost"),
    'user': os.getenv("DB_USER", "root"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME", "ppe")
}
API_BASE_URL = "http://localhost:8000"

def print_status(check_name, status, message=""):
    symbol = "✅" if status else "❌"
    print(f"{symbol} {check_name}: {message}")

def check_database():
    print("\n=== Database Checks ===")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print_status("Database Connection", True, "Connected successfully")
        
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [t[0] for t in cursor.fetchall()]
        
        required_tables = ['workers', 'attendance', 'alerts']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if not missing_tables:
            print_status("Table Structure", True, f"Found tables: {', '.join(tables)}")
        else:
            print_status("Table Structure", False, f"Missing tables: {', '.join(missing_tables)}")
            
        # Check row counts
        for table in required_tables:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   - {table}: {count} records")
                
        conn.close()
        return True
    except Exception as e:
        print_status("Database Connection", False, str(e))
        return False

def check_api():
    print("\n=== Backend API Checks ===")
    endpoints = [
        ("/api/workers", "Workers List"),
        ("/api/attendance/logs?limit=1", "Attendance Logs"),
        ("/api/alerts?limit=1", "Alerts List"),
        ("/api/dashboard/stats", "Dashboard Stats")
    ]
    
    all_passed = True
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                # Basic validation
                is_valid = True
                details = ""
                
                if "workers" in endpoint:
                    if isinstance(data, list):
                        details = f"{len(data)} workers found"
                    else:
                        is_valid = False
                elif "attendance" in endpoint:
                    if isinstance(data, list):
                        if len(data) > 0 and 'employee_id' in data[0]:
                            details = "employee_id field present ✅"
                        elif len(data) > 0:
                             details = "employee_id field MISSING ❌"
                    else:
                        is_valid = False
                
                print_status(name, is_valid, f"Status 200 OK - {details}")
            else:
                print_status(name, False, f"Status {response.status_code}")
                all_passed = False
        except requests.exceptions.ConnectionError:
            print_status(name, False, "Connection Refused - Is backend running?")
            all_passed = False
            break
        except Exception as e:
            print_status(name, False, str(e))
            all_passed = False
            
    return all_passed

if __name__ == "__main__":
    print("Starting System Health Check...")
    db_ok = check_database()
    api_ok = check_api()
    
    if db_ok and api_ok:
        print("\n✨ SYSTEM STATUS: HEALTHY ✨")
        sys.exit(0)
    else:
        print("\n⚠️ SYSTEM STATUS: ISSUES DETECTED ⚠️")
        sys.exit(1)
