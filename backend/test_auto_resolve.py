import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"
WORKER_NAME = "Test_Worker_AutoResolve"

def create_worker_if_not_exists():
    print(f"Creating/Checking worker: {WORKER_NAME}")
    # We can just rely on update_attendance to auto-create, but let's be clean
    pass

def trigger_alert():
    print("\n--- Triggering Alert (FAIL) ---")
    payload = {
        "name": WORKER_NAME,
        "time": int(time.time()),
        "status": "fail",
        "source": "test_script",
        "helmet": False, # Missing helmet
        "jacket": True,
        "glows": True,
        "sheao": True,
        "headphone": True
    }
    try:
        r = requests.post(f"{BASE_URL}/update_attendance", json=payload)
        r.raise_for_status()
        print("Response:", r.json())
        return True
    except Exception as e:
        print(f"Failed to trigger alert: {e}")
        return False

def trigger_resolve():
    print("\n--- Triggering Resolution (PASS) ---")
    payload = {
        "name": WORKER_NAME,
        "time": int(time.time()),
        "status": "pass",
        "source": "test_script",
        "helmet": True, # All present
        "jacket": True,
        "glows": True,
        "sheao": True,
        "headphone": True
    }
    try:
        r = requests.post(f"{BASE_URL}/update_attendance", json=payload)
        r.raise_for_status()
        print("Response:", r.json())
        return True
    except Exception as e:
        print(f"Failed to trigger resolution: {e}")
        return False

def check_alerts():
    print("\n--- Checking Alerts ---")
    # We need to get the worker ID first to query alerts properly, 
    # but for now let's just check if we can list alerts or check the worker status
    
    # 1. Get Worker ID
    try:
        r = requests.get(f"{BASE_URL}/api/workers", params={"search": WORKER_NAME})
        data = r.json()
        workers = data.get("workers", [])
        if not workers:
            print("Worker not found!")
            return
        
        worker = workers[0]
        worker_id = worker['id']
        print(f"Worker ID: {worker_id}, Status: {worker['status']}")
        
        # NOTE: There isn't a direct public API to list alerts by worker in the snippets I saw,
        # but we can infer from worker status or if we had an alerts endpoint.
        # However, the user asked for the alert status to change.
        # Since I don't have direct DB access in this script easily without setup, 
        # I will rely on the console output of the backend or the worker status.
        
        # Actually, let's try to fetch alerts if there is an endpoint.
        # Looking at backend_app.py, I didn't see a "list alerts" endpoint in the snippets.
        # But I can check the worker status which should toggle between active/inactive.
        
        return worker['status']
        
    except Exception as e:
        print(f"Error checking status: {e}")
        return None

def main():
    # 1. Trigger Fail -> Should create alert and set inactive
    if trigger_alert():
        time.sleep(1)
        status = check_alerts()
        if status == 'inactive':
            print("SUCCESS: Worker is inactive (Alert Active)")
        else:
            print(f"FAILURE: Worker status is {status}, expected inactive")

    # 2. Trigger Pass -> Should resolve alert and set active
    if trigger_resolve():
        time.sleep(1)
        status = check_alerts()
        if status == 'active':
            print("SUCCESS: Worker is active (Alert Resolved)")
        else:
            print(f"FAILURE: Worker status is {status}, expected active")

if __name__ == "__main__":
    main()
