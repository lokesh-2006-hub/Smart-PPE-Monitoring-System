from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone
import mysql.connector
import json
import time
import csv
import io
import sys
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path to allow imports from utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import email sender utility
from utils.email_sender import send_alert_email


# --- Database Config ---
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "ppe")
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        # If database does not exist, try to create it
        if err.errno == 1049: # Unknown database
            temp_config = DB_CONFIG.copy()
            del temp_config["database"]
            conn = mysql.connector.connect(**temp_config)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            conn.close()
            # Retry
            return mysql.connector.connect(**DB_CONFIG)
        raise err

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Persons table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS persons (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        employee_id VARCHAR(255),
        meta TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2. Workers table (New Redesign)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        employee_id VARCHAR(50) UNIQUE,
        name VARCHAR(255) NOT NULL,
        department VARCHAR(100),
        rfid_tag VARCHAR(50) UNIQUE,
        status ENUM('active', 'inactive') DEFAULT 'active',
        phone VARCHAR(20),
        email VARCHAR(255),
        photo_url LONGTEXT,
        address VARCHAR(20),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_employee_id (employee_id),
        INDEX idx_status (status),
        INDEX idx_department (department)
    )
    """)
    
    # 3. Attendance table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        person_id INT,
        person_name VARCHAR(255) NOT NULL,
        detected_at DATETIME NOT NULL,
        time_in DATETIME,
        time_out DATETIME,
        source VARCHAR(100),
        location VARCHAR(100),
        gate VARCHAR(50),
        ppe_status TEXT NOT NULL,
        overall_status VARCHAR(50) NOT NULL,
        raw_payload TEXT,
        FOREIGN KEY (person_id) REFERENCES persons(id)
    )
    """)
    
    # 4. Alerts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        worker_id INT,
        worker_name VARCHAR(255),
        type VARCHAR(50),
        severity ENUM('critical', 'warning', 'info') DEFAULT 'warning',
        message TEXT,
        location VARCHAR(100),
        gate VARCHAR(50),
        status ENUM('active', 'resolved') DEFAULT 'active',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        resolved_at DATETIME,
        resolution_note TEXT,
        response_time INT,
        INDEX idx_status (status),
        INDEX idx_severity (severity),
        INDEX idx_worker_id (worker_id),
        INDEX idx_created_at (created_at)
    )
    """)

    # 5. Reports table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INT AUTO_INCREMENT PRIMARY KEY,
        report_type VARCHAR(100),
        title VARCHAR(255),
        start_date DATE,
        end_date DATE,
        file_path VARCHAR(255),
        file_format VARCHAR(10),
        total_records INT,
        total_violations INT,
        generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        generated_by VARCHAR(255),
        INDEX idx_report_type (report_type),
        INDEX idx_generated_at (generated_at)
    )
    """)
    
    # Settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        category VARCHAR(50) NOT NULL,
        setting_key VARCHAR(100) NOT NULL,
        setting_value TEXT NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY unique_setting (category, setting_key)
    )
    """)
    
    # Initialize default settings if table is empty
    cursor.execute("SELECT COUNT(*) as cnt FROM settings")
    count = cursor.fetchone()['cnt']
    
    if count == 0:
        default_settings = [
            ('system', 'ppe_items', json.dumps({'helmet': True, 'jacket': True, 'gloves': True, 'shoes': True, 'headphone': True})),
            ('system', 'detection_threshold', '0.5'),
            ('system', 'min_compliance', '100'),
            ('system', 'frame_rate', '30'),
            ('alerts', 'enable_email', 'true'),
            ('alerts', 'enable_sms', 'false'),
            ('alerts', 'enable_in_app', 'true'),
            ('alerts', 'severity', '"critical"'),
            ('alerts', 'auto_escalate', 'true'),
            ('alerts', 'escalation_time', '5'),
            ('alerts', 'alert_email_list', '"admin@example.com,safety@example.com"'),
            ('reports', 'frequency', '"daily"'),
            ('reports', 'format', '"pdf"'),
            ('reports', 'email_list', '"admin@example.com"'),
            ('reports', 'retention', '90'),
            ('notifications', 'smtp_host', '"smtp.gmail.com"'),
            ('notifications', 'smtp_port', '587'),
            ('notifications', 'smtp_user', '""'),
            ('notifications', 'smtp_password', '""'),
            ('notifications', 'sms_gateway', '""')
        ]
        
        cursor.executemany(
            "INSERT INTO settings (category, setting_key, setting_value) VALUES (%s, %s, %s)",
            default_settings
        )
    
    # Clean fallback for older installations that might be missing these columns in workers
    try:
        cursor.execute("ALTER TABLE workers ADD COLUMN department VARCHAR(100)")
        cursor.execute("ALTER TABLE workers ADD COLUMN address VARCHAR(20)")
    except mysql.connector.Error:
        pass
    
    # Render cloud: ensure photo_url is LONGTEXT to hold Base64 strings
    try:
        cursor.execute("ALTER TABLE workers MODIFY photo_url LONGTEXT")
    except mysql.connector.Error:
        pass
    
    conn.commit()
    cursor.close()
    conn.close()

# --- Pydantic schemas ---
class PPEPayload(BaseModel):
    name: str
    time: Optional[int] = None
    status: str
    source: Optional[str] = None  # camera, video, image, or folder
    helmet: Optional[bool] = None
    glows: Optional[bool] = None
    sheao: Optional[bool] = None
    glass: Optional[bool] = None
    jacket: Optional[bool] = None
    headphone: Optional[bool] = None
    extra: Optional[Dict[str, bool]] = None

class RegisterPersonPayload(BaseModel):
    name: str
    employee_id: Optional[str] = None
    meta: Optional[Dict] = None

class SettingsUpdate(BaseModel):
    category: str
    settings: Dict[str, Any]

class Announcement(BaseModel):
    content:str
    author:str
# --- FastAPI app ---
app = FastAPI(title="Smart PPE Compliance API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/announcement",response_model=Announcement)
def create_announcement(payload:Announcement):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("INSERT INTO announcement (content,author) VALUES (%s,%s)",(payload.content,payload.author))
    conn.commit()
    cursor.close()
    conn.close()
    return payload
@app.get("/announcement",response_model=List[Dict])
def get_announcement():
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM announcement ORDER BY created_at DESC")
    result=cursor.fetchall()
    cursor.close()
    conn.close()
    return result

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/register_person", response_model=Dict)
def register_person(payload: RegisterPersonPayload):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM persons WHERE name = %s", (payload.name,))
        person = cursor.fetchone()
        if person:
            return {"status": "exists", "id": person['id']}
        
        meta_json = json.dumps(payload.meta or {})
        cursor.execute(
            "INSERT INTO persons (name, employee_id, meta) VALUES (%s, %s, %s)",
            (payload.name, payload.employee_id, meta_json)
        )
        conn.commit()
        return {"status": "created", "id": cursor.lastrowid}
    finally:
        cursor.close()
        conn.close()

@app.post("/update_attendance", response_model=Dict)
def update_attendance(payload: PPEPayload):
    print(f"\n*** UPDATE_ATTENDANCE CALLED - Worker: {payload.name}, Status: {payload.status} ***\n")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        try:
            epoch = payload.time or int(time.time())
            ts = datetime.fromtimestamp(epoch)

            # Normalize payload -> ppe flags (standardized to 5 items)
            ppe_keys = {
                "helmet": payload.helmet,
                "jacket": payload.jacket,
                "gloves": payload.glows,  # Detection sends 'glows', store as 'gloves'
                "shoes": payload.sheao,   # Detection sends 'sheao', store as 'shoes'
                "headphone": payload.headphone
            }
            
            # Ensure boolean values (default to False if None)
            for k, v in ppe_keys.items():
                if v is None:
                    ppe_keys[k] = False
            
            # Fetch PPE requirements from settings to determine what should be checked
            cursor.execute("""
                SELECT setting_value FROM settings 
                WHERE category='system' AND setting_key='ppe_items'
            """)
            ppe_requirements_row = cursor.fetchone()
            
            if ppe_requirements_row:
                try:
                    ppe_requirements = json.loads(ppe_requirements_row['setting_value'])
                except:
                    # Fallback to all items if parsing fails
                    ppe_requirements = {item: True for item in ppe_keys.keys()}
            else:
                # Fallback to all items if no settings found
                ppe_requirements = {item: True for item in ppe_keys.keys()}
            
            # Recalculate overall status based on ONLY the required PPE items
            missing_required_items = []
            for item, is_required in ppe_requirements.items():
                if is_required and not ppe_keys.get(item, False):
                    missing_required_items.append(item)
            
            # Override the status from detection with calculated status
            calculated_status = "pass" if len(missing_required_items) == 0 else "fail"
            overall_status = calculated_status
            
            print(f"PPE Requirements from settings: {ppe_requirements}")
            print(f"PPE Detected: {ppe_keys}")
            print(f"Missing required items: {missing_required_items}")
            print(f"Calculated status: {calculated_status} (original from detection: {payload.status})")

            # 1. Find or Create Worker in workers table
            cursor.execute("SELECT id, status FROM workers WHERE name = %s", (payload.name,))
            worker = cursor.fetchone()
            
            worker_id = None
            if not worker:
                # Worker doesn't exist in workers table - create a basic entry
                cursor.execute("""
                    INSERT INTO workers (name, employee_id, status) 
                    VALUES (%s, %s, 'inactive')
                """, (payload.name, f"AUTO_{payload.name}"))
                conn.commit()
                worker_id = cursor.lastrowid
                print(f"⚠️  Auto-created worker '{payload.name}' with ID {worker_id}")
            else:
                worker_id = worker['id']

            # Also maintain persons table for compatibility (optional)
            cursor.execute("SELECT id FROM persons WHERE name = %s", (payload.name,))
            person = cursor.fetchone()
            if not person:
                cursor.execute("INSERT INTO persons (name, meta) VALUES (%s, '{}')", (payload.name,))
                conn.commit()
                person_id = cursor.lastrowid
            else:
                person_id = person['id']

            # Check if record exists for this worker today
            cursor.execute("""
                SELECT id FROM attendance 
                WHERE person_name = %s AND DATE(detected_at) = DATE(%s)
                ORDER BY detected_at DESC 
                LIMIT 1
            """, (payload.name, ts))
            existing_record = cursor.fetchone()
            
            if existing_record:
                # UPDATE existing record - use worker_id
                cursor.execute("""
                    UPDATE attendance 
                    SET person_id = %s, detected_at = %s, source = %s, ppe_status = %s, overall_status = %s, raw_payload = %s
                    WHERE id = %s
                """, (
                    worker_id,  # CHANGED: Use worker_id instead of person_id
                    ts,
                    payload.source,
                    json.dumps(ppe_keys),
                    overall_status,  # Use calculated status based on settings
                    json.dumps(payload.dict()),
                    existing_record['id']
                ))
                conn.commit()
                record_id = existing_record['id']
            else:
                # INSERT new record - use worker_id
                cursor.execute(
                    """
                    INSERT INTO attendance 
                    (person_id, person_name, detected_at, source, ppe_status, overall_status, raw_payload)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        worker_id,  # CHANGED: Use worker_id instead of person_id from persons table
                        payload.name,
                        ts,
                        payload.source,
                        json.dumps(ppe_keys),
                        overall_status,  # Use calculated status based on settings
                        json.dumps(payload.dict())
                    )
                )
                conn.commit()
                record_id = cursor.lastrowid
            
            # AUTOMATIC WORKER STATUS UPDATE BASED ON PPE COMPLIANCE
            # worker_id is already fetched above
            if overall_status == "pass":
                # PPE check passed - set worker to active
                cursor.execute("UPDATE workers SET status = 'active' WHERE id = %s", (worker_id,))
                print(f"✅ Worker {payload.name} set to ACTIVE (PPE passed)")
                
                # AUTO-RESOLVE ALERTS: If worker is now compliant, resolve any active alerts
                try:
                    cursor.execute("""
                        UPDATE alerts 
                        SET status = 'resolved', resolution_note = 'Auto-resolved: PPE compliance verified'
                        WHERE worker_id = %s AND status = 'active'
                    """, (worker_id,))
                    resolved_count = cursor.rowcount
                    if resolved_count > 0:
                        print(f"✅ Auto-resolved {resolved_count} active alerts for {payload.name}")
                        conn.commit()
                except Exception as resolve_err:
                    print(f"⚠️ Failed to auto-resolve alerts: {resolve_err}")
            else:
                # PPE check failed - set worker to inactive and create alert
                cursor.execute("UPDATE workers SET status = 'inactive' WHERE id = %s", (worker_id,))
                print(f"❌ Worker {payload.name} set to INACTIVE (PPE failed)")
                print(f"DEBUG: ppe_keys = {ppe_keys}")
                
                # Create alert for PPE violation
                # Use only missing REQUIRED items (from settings)
                missing_items = missing_required_items
                print(f"DEBUG: missing_items = {missing_items}")
                
                if missing_items:
                    alert_message = f"PPE Violation: Missing {', '.join(missing_items)}"
                    location = payload.source or "Unknown Location"
                    
                    print(f"DEBUG: Creating alert - worker_id={worker_id}, worker_name={payload.name}, message={alert_message}")
                    
                    # Insert alert into alerts table
                    try:
                        cursor.execute("""
                            INSERT INTO alerts 
                            (worker_id, worker_name, type, severity, message, location, gate, status, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                        """, (
                            worker_id,
                            payload.name,  # worker_name
                            'ppe_violation',
                            'critical',
                            alert_message,
                            location,
                            location,  # gate (same as location)
                            'active'
                        ))
                        print(f"🚨 Alert created: {alert_message}")
                        
                        # Send email alert
                        try:
                            email_sent = send_alert_email(payload.name, ppe_keys)
                            if email_sent:
                                print(f"📧 Email alert sent for {payload.name}")
                            else:
                                print(f"⚠️  Email alert not sent (check settings or logs)")
                        except Exception as email_err:
                            print(f"Warning: Could not send email alert: {email_err}")
                            # Email failure doesn't fail the whole request
                            
                    except mysql.connector.Error as alert_err:
                        # Alert creation failed but don't fail the whole request
                        print(f"Warning: Could not create alert: {alert_err}")
                else:
                    print(f"DEBUG: No missing items found, skipping alert creation")
            
            
            conn.commit()
            
            return {"status": "updated" if existing_record else "created", "record_id": record_id}
        except Exception as e:
            import traceback
            traceback.print_exc()
            conn.rollback()
            print(f"❌ Error in update_attendance: {e}")
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.get("/persons", response_model=List[Dict])
def list_persons(limit: int = 100):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM persons ORDER BY created_at DESC LIMIT %s", (limit,))
        rows = cursor.fetchall()
        out = []
        for p in rows:
            out.append({
                "id": p['id'],
                "name": p['name'],
                "employee_id": p['employee_id'],
                "meta": json.loads(p['meta']) if p['meta'] else {},
                "created_at": p['created_at'].isoformat() if p['created_at'] else None
            })
        return out
    finally:
        cursor.close()
        conn.close()

@app.get("/reports/daily", response_model=Dict)
def daily_report(date: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if date:
            day_str = date
        else:
            day_str = datetime.now().strftime("%Y-%m-%d")

        # Total
        cursor.execute("SELECT COUNT(*) as cnt FROM attendance WHERE DATE(detected_at) = %s", (day_str,))
        total = cursor.fetchone()['cnt']

        # Pass
        cursor.execute("SELECT COUNT(*) as cnt FROM attendance WHERE DATE(detected_at) = %s AND overall_status = 'pass'", (day_str,))
        pass_count = cursor.fetchone()['cnt']

        # Fail
        cursor.execute("SELECT COUNT(*) as cnt FROM attendance WHERE DATE(detected_at) = %s AND overall_status = 'fail'", (day_str,))
        fail_count = cursor.fetchone()['cnt']

        # Top offenders
        cursor.execute("""
            SELECT person_name, COUNT(*) as fails 
            FROM attendance 
            WHERE DATE(detected_at) = %s AND overall_status = 'fail'
            GROUP BY person_name 
            ORDER BY fails DESC 
            LIMIT 10
        """, (day_str,))
        offenders = cursor.fetchall()
        
        return {
            "date": day_str,
            "total": total,
            "pass": pass_count,
            "fail": fail_count,
            "top_offenders": [{"name": r['person_name'], "fails": r['fails']} for r in offenders]
        }
    finally:
        cursor.close()
        conn.close()

@app.get("/attendance/latest", response_model=Dict)
def get_latest_attendance():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT * FROM attendance 
            ORDER BY detected_at DESC 
            LIMIT 1
        """)
        r = cursor.fetchone()
        if not r:
            return {}
        return {
            "id": r['id'],
            "person_name": r['person_name'],
            "detected_at": r['detected_at'].isoformat() if r['detected_at'] else None,
            "source": r['source'],
            "ppe_status": json.loads(r['ppe_status']) if r['ppe_status'] else {},
            "status": r['overall_status']
        }
    finally:
        cursor.close()
        conn.close()

@app.get("/attendance/{person_name}", response_model=List[Dict])
def person_attendance(person_name: str, limit: int = 100):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT * FROM attendance 
            WHERE person_name = %s 
            ORDER BY detected_at DESC 
            LIMIT %s
        """, (person_name, limit))
        rows = cursor.fetchall()
        out = []
        for r in rows:
            out.append({
                "id": r['id'],
                "person_name": r['person_name'],
                "detected_at": r['detected_at'].isoformat() if r['detected_at'] else None,
                "source": r['source'],
                "ppe_status": json.loads(r['ppe_status']) if r['ppe_status'] else {},
                "status": r['overall_status']
            })
        return out
    finally:
        cursor.close()
        conn.close()

# ==================== SETTINGS API ENDPOINTS ====================

@app.get("/api/settings", response_model=Dict)
def get_settings():
    """Get all application settings grouped by category"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT category, setting_key, setting_value FROM settings ORDER BY category, setting_key")
        rows = cursor.fetchall()
        
        # Group by category
        settings = {}
        for row in rows:
            category = row['category']
            key = row['setting_key']
            value = row['setting_value']
            
            # Parse JSON values
            try:
                parsed_value = json.loads(value)
            except:
                # If not JSON, try to parse as boolean, number, or keep as string
                if value.lower() == 'true':
                    parsed_value = True
                elif value.lower() == 'false':
                    parsed_value = False
                elif value.replace('.', '', 1).isdigit():
                    parsed_value = float(value) if '.' in value else int(value)
                else:
                    parsed_value = value
            
            if category not in settings:
                settings[category] = {}
            settings[category][key] = parsed_value
        
        return settings
    finally:
        cursor.close()
        conn.close()

@app.put("/api/settings", response_model=Dict)
def update_settings(payload: SettingsUpdate):
    """Update settings for a specific category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        category = payload.category
        settings = payload.settings
        
        updated_count = 0
        for key, value in settings.items():
            # Convert value to JSON string for storage
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value)
            elif isinstance(value, bool):
                value_str = 'true' if value else 'false'
            elif isinstance(value, (int, float)):
                value_str = str(value)
            else:
                value_str = json.dumps(value) if isinstance(value, str) else str(value)
            
            # Insert or update
            cursor.execute("""
                INSERT INTO settings (category, setting_key, setting_value)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)
            """, (category, key, value_str))
            updated_count += 1
        
        conn.commit()
        
        return {
            "status": "success",
            "message": "Settings updated successfully",
            "updated_count": updated_count
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# ==================== NEW API ENDPOINTS FOR UI REDESIGN ====================


# --- Worker Management Schemas ---
class WorkerCreate(BaseModel):
    employee_id: str
    name: str
    department: Optional[str] = None
    rfid_tag: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = "active"
    address: Optional[str] = None

class WorkerUpdate(BaseModel):
    employee_id: Optional[str] = None
    name: Optional[str] = None
    department: Optional[str] = None
    rfid_tag: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    address: Optional[str] = None

# --- Alert Schemas ---
class AlertCreate(BaseModel):
    worker_id: Optional[int] = None
    worker_name: str
    type: str
    severity: str = "warning"
    message: str
    location: Optional[str] = None
    gate: Optional[str] = None

class AlertResolve(BaseModel):
    resolution_note: Optional[str] = None

class RFIDAttendancePayload(BaseModel):
    rfid_tag: str
    timestamp: Optional[int] = None
    gate: Optional[str] = "Main Gate"

# ==================== RFID ATTENDANCE API ====================

@app.post("/api/attendance/rfid", response_model=Dict)
def mark_rfid_attendance(payload: RFIDAttendancePayload):
    """Mark attendance using RFID tag"""
    print(f"\n*** RFID ATTENDANCE CALLED - Tag: {payload.rfid_tag} ***\n")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Find worker by RFID tag
        cursor.execute("SELECT * FROM workers WHERE rfid_tag = %s", (payload.rfid_tag,))
        worker = cursor.fetchone()
        
        if not worker:
            print(f"⚠️  Unknown RFID tag: {payload.rfid_tag}")
            # Optional: Log unknown tag attempt
            return {
                "status": "error", 
                "message": "Unknown RFID tag",
                "rfid_tag": payload.rfid_tag
            }
            
        worker_id = worker['id']
        worker_name = worker['name']
        
        # 2. Mark attendance
        epoch = payload.timestamp or int(time.time())
        ts = datetime.fromtimestamp(epoch)
        
        # Check if already checked in today
        cursor.execute("""
            SELECT id FROM attendance 
            WHERE person_id = %s AND DATE(detected_at) = DATE(%s)
            ORDER BY detected_at DESC LIMIT 1
        """, (worker_id, ts))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing record
            cursor.execute("""
                UPDATE attendance 
                SET detected_at = %s, source = 'rfid', overall_status = 'pass'
                WHERE id = %s
            """, (ts, existing['id']))
            record_id = existing['id']
            action = "updated"
        else:
            # Create new record
            # Create a dummy ppe_status for RFID (all passed or empty)
            ppe_status = json.dumps({
                "helmet": True, "jacket": True, "gloves": True, "shoes": True, "headphone": True
            })
            
            cursor.execute("""
                INSERT INTO attendance 
                (person_id, person_name, detected_at, source, ppe_status, overall_status, raw_payload)
                VALUES (%s, %s, %s, 'rfid', %s, 'pass', %s)
            """, (
                worker_id, 
                worker_name, 
                ts, 
                ppe_status,
                json.dumps(payload.dict())
            ))
            record_id = cursor.lastrowid
            action = "created"
            
        # 3. Update worker status to active
        cursor.execute("UPDATE workers SET status = 'active' WHERE id = %s", (worker_id,))
        conn.commit()
        
        print(f"✅ Attendance marked for {worker_name} ({action})")
        
        return {
            "status": "success",
            "message": f"Attendance marked for {worker_name}",
            "worker_name": worker_name,
            "action": action,
            "record_id": record_id
        }
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error in mark_rfid_attendance: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ==================== WORKERS MANAGEMENT APIs ====================

@app.get("/api/workers", response_model=Dict)
def list_workers(
    page: int = 1,
    limit: int = 100,
    search: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    address: Optional[str] = None
):
    """List all workers with pagination and filters"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Build query with filters
        where_clauses = []
        params = []
        
        if search:
            where_clauses.append("(name LIKE %s OR employee_id LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])
        
        if department:
            where_clauses.append("department = %s")
            params.append(department)
        
        if status:
            where_clauses.append("status = %s")
            params.append(status)
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) as total FROM workers WHERE {where_sql}", params)
        total = cursor.fetchone()['total']
        
        # Get paginated results
        offset = (page - 1) * limit
        cursor.execute(f"""
            SELECT * FROM workers 
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])
        
        workers = cursor.fetchall()
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "workers": workers
        }
    finally:
        cursor.close()
        conn.close()

@app.post("/api/workers", response_model=Dict)
def create_worker(worker: WorkerCreate):
    """Create a new worker"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            INSERT INTO workers (employee_id, name, department, rfid_tag, phone, email, status, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            worker.employee_id,
            worker.name,
            worker.department,
            worker.rfid_tag,
            worker.phone,
            worker.email,
            worker.status,
            worker.address
        ))
        conn.commit()
        
        return {
            "status": "success",
            "id": cursor.lastrowid,
            "message": "Worker created successfully"
        }
    except mysql.connector.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Worker already exists: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.get("/api/workers/{worker_id}", response_model=Dict)
def get_worker(worker_id: int):
    """Get single worker details"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM workers WHERE id = %s", (worker_id,))
        worker = cursor.fetchone()
        
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        return worker
    finally:
        cursor.close()
        conn.close()

@app.put("/api/workers/{worker_id}", response_model=Dict)
def update_worker(worker_id: int, worker: WorkerUpdate):
    """Update worker information"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Build update query dynamically
        updates = []
        params = []
        
        if worker.employee_id is not None:
            updates.append("employee_id = %s")
            params.append(worker.employee_id)
        if worker.name is not None:
            updates.append("name = %s")
            params.append(worker.name)
        if worker.department is not None:
            updates.append("department = %s")
            params.append(worker.department)
        if worker.rfid_tag is not None:
            updates.append("rfid_tag = %s")
            # Convert empty string to NULL to avoid UNIQUE constraint issues
            params.append(worker.rfid_tag if worker.rfid_tag.strip() else None)
        if worker.phone is not None:
            updates.append("phone = %s")
            # Convert empty string to NULL to avoid UNIQUE constraint issues
            params.append(worker.phone if worker.phone.strip() else None)
        if worker.email is not None:
            updates.append("email = %s")
            # Convert empty string to NULL to avoid UNIQUE constraint issues
            params.append(worker.email if worker.email.strip() else None)
        if worker.status is not None:
            updates.append("status = %s")
            params.append(worker.status)
        if worker.address is not None:
            updates.append("address = %s")
            params.append(worker.address)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        params.append(worker_id)
        cursor.execute(f"""
            UPDATE workers 
            SET {', '.join(updates)}
            WHERE id = %s
        """, params)
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        return {"status": "success", "message": "Worker updated successfully"}
    except HTTPException:
        raise
    except mysql.connector.IntegrityError as e:
        conn.rollback()
        print(f"❌ Database integrity error: {e}")
        # Check if it's a duplicate rfid_tag error
        if "rfid_tag" in str(e):
            raise HTTPException(status_code=400, detail="RFID tag already exists. Please use a unique RFID tag or leave it empty.")
        elif "phone" in str(e):
            raise HTTPException(status_code=400, detail="Phone number already exists. Please use a unique phone number or leave it empty.")
        elif "email" in str(e):
            raise HTTPException(status_code=400, detail="Email already exists. Please use a unique email or leave it empty.")
        else:
            raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error updating worker: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update worker: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/workers/{worker_id}", response_model=Dict)
def delete_worker(worker_id: int):
    """Completely delete worker and all associated data"""
    import os
    import shutil
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # First, get worker details (especially name for deleting photos)
        cursor.execute("SELECT name FROM workers WHERE id = %s", (worker_id,))
        worker = cursor.fetchone()
        
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        worker_name = worker['name']
        
        # 1. Delete all alerts for this worker
        cursor.execute("DELETE FROM alerts WHERE worker_id = %s", (worker_id,))
        deleted_alerts = cursor.rowcount
        print(f"Deleted {deleted_alerts} alerts for worker {worker_name}")
        
        # 2. Delete all attendance records for this worker
        cursor.execute("DELETE FROM attendance WHERE person_id = %s", (worker_id,))
        deleted_attendance = cursor.rowcount
        print(f"Deleted {deleted_attendance} attendance records for worker {worker_name}")
        
        # 3. Delete worker from workers table
        cursor.execute("DELETE FROM workers WHERE id = %s", (worker_id,))
        
        # 4. Delete photos from known_faces directory
        known_faces_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'known_faces', worker_name)
        deleted_photos = 0
        
        if os.path.exists(known_faces_dir):
            try:
                # Count photos before deletion
                photo_files = [f for f in os.listdir(known_faces_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                deleted_photos = len(photo_files)
                
                # Remove entire directory
                shutil.rmtree(known_faces_dir)
                print(f"✅ Deleted known_faces directory: {known_faces_dir} ({deleted_photos} photos)")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete photos directory: {e}")
        else:
            print(f"⚠️ No photos directory found for worker {worker_name}")
        
        conn.commit()
        
        return {
            "status": "success",
            "message": f"Worker '{worker_name}' and all associated data deleted successfully",
            "details": {
                "alerts_deleted": deleted_alerts,
                "attendance_deleted": deleted_attendance,
                "photos_deleted": deleted_photos
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"❌ Error deleting worker: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete worker: {str(e)}")
        cursor.close()
        conn.close()

@app.post("/api/workers/sync-from-known-faces", response_model=Dict)
def sync_workers_from_known_faces():
    """
    Scan known_faces directory and sync workers to database.
    Clears existing workers and creates new ones with only name and photo info.
    """
    import os
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Path to known_faces directory
        known_faces_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'known_faces')
        
        if not os.path.exists(known_faces_dir):
            raise HTTPException(status_code=404, detail="known_faces directory not found")
        
        # Get all subdirectories (worker names)
        worker_folders = []
        for item in os.listdir(known_faces_dir):
            item_path = os.path.join(known_faces_dir, item)
            if os.path.isdir(item_path):
                # Count photos in this directory
                photo_files = [f for f in os.listdir(item_path) 
                              if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                if len(photo_files) > 0:  # Only include if has photos
                    worker_folders.append({
                        'name': item,
                        'photo_count': len(photo_files)
                    })
        
        print(f"Found {len(worker_folders)} workers in known_faces directory")
        
        # Clear existing workers table (COMPLETE RESET)
        cursor.execute("DELETE FROM workers")
        deleted_count = cursor.rowcount
        print(f"Deleted {deleted_count} existing workers from database")
        
        # Create new worker entries with minimal data
        created_workers = []
        for worker_info in worker_folders:
            worker_name = worker_info['name']
            
            cursor.execute("""
                INSERT INTO workers (name, employee_id, status, department, rfid_tag, phone, email)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                worker_name,
                f"AUTO_{worker_name[:10]}",  # Auto-generated employee ID
                'inactive',  # Default status
                '',  # Empty department (can be empty, not unique)
                None,  # NULL for rfid_tag (UNIQUE constraint - NULL allowed)
                None,  # NULL for phone (might have UNIQUE constraint)
                None   # NULL for email (might have UNIQUE constraint)
            ))
            
            worker_id = cursor.lastrowid
            created_workers.append({
                'id': worker_id,
                'name': worker_name,
                'photo_count': worker_info['photo_count']
            })
            
        conn.commit()
        
        print(f"✅ Created {len(created_workers)} workers from known_faces")
        
        return {
            "status": "success",
            "message": f"Synced {len(created_workers)} workers from known_faces directory",
            "workers": created_workers,
            "details": {
                "deleted_old_workers": deleted_count,
                "created_new_workers": len(created_workers)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"❌ Error syncing workers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to sync workers: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# ==================== ATTENDANCE MANAGEMENT APIs ====================

@app.get("/api/attendance/logs", response_model=List[Dict])
def get_attendance_logs(
    date: Optional[str] = None,
    worker_id: Optional[int] = None,
    status: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 100
):
    """Get attendance logs with filters"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        where_clauses = []
        params = []
        
        if date:
            where_clauses.append("DATE(detected_at) = %s")
            params.append(date)
        
        if worker_id:
            where_clauses.append("person_id = %s")
            params.append(worker_id)
        
        if status:
            where_clauses.append("overall_status = %s")
            params.append(status)
        
        if location:
            where_clauses.append("location = %s")
            params.append(location)
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        cursor.execute(f"""
            SELECT 
                a.id,
                a.person_name as worker_name,
                a.person_id as worker_id,
                w.employee_id,
                a.time_in,
                a.time_out,
                a.overall_status as ppe_status,
                a.location,
                a.gate,
                a.source
            FROM attendance a
            LEFT JOIN workers w ON a.person_name = w.name
            WHERE {where_sql}
            ORDER BY a.detected_at DESC
            LIMIT %s
        """, params + [limit])
        
        logs = cursor.fetchall()
        
        # Format datetime fields
        for log in logs:
            if log['time_in']:
                log['time_in'] = log['time_in'].strftime("%I:%M %p")
            if log['time_out']:
                log['time_out'] = log['time_out'].strftime("%I:%M %p")
            else:
                log['time_out'] = "-"
        
        return logs
    finally:
        cursor.close()
        conn.close()

@app.get("/api/attendance/today", response_model=Dict)
def get_today_attendance():
    """Get today's attendance summary"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Total check-ins
        cursor.execute("SELECT COUNT(*) as total FROM attendance WHERE DATE(detected_at) = %s", (today,))
        total = cursor.fetchone()['total']
        
        # Pass count
        cursor.execute("SELECT COUNT(*) as pass_count FROM attendance WHERE DATE(detected_at) = %s AND overall_status = 'pass'", (today,))
        pass_count = cursor.fetchone()['pass_count']
        
        # Fail count
        cursor.execute("SELECT COUNT(*) as fail_count FROM attendance WHERE DATE(detected_at) = %s AND overall_status = 'fail'", (today,))
        fail_count = cursor.fetchone()['fail_count']
        
        # Active workers (checked in but not checked out)
        cursor.execute("SELECT COUNT(*) as active FROM attendance WHERE DATE(detected_at) = %s AND time_out IS NULL", (today,))
        active = cursor.fetchone()['active']
        
        compliance_rate = round((pass_count / total * 100), 1) if total > 0 else 0
        
        return {
            "total_checkins": total,
            "compliance_rate": compliance_rate,
            "violations": fail_count,
            "active_workers": active
        }
    finally:
        cursor.close()
        conn.close()

@app.post("/api/attendance/checkout", response_model=Dict)
def manual_checkout(worker_id: int):
    """Manual checkout for worker"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now()
        
        cursor.execute("""
            UPDATE attendance 
            SET time_out = %s
            WHERE person_id = %s 
            AND DATE(detected_at) = %s 
            AND time_out IS NULL
            ORDER BY detected_at DESC
            LIMIT 1
        """, (now, worker_id, today))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="No active check-in found for this worker")
        
        return {"status": "success", "message": "Worker checked out successfully"}
    finally:
        cursor.close()
        conn.close()

# ==================== REPORTS APIs ====================

@app.get("/api/reports/summary/today", response_model=Dict)
def get_today_summary():
    """Get today's summary statistics"""
    return get_today_attendance()

@app.get("/api/reports/top-offenders", response_model=List[Dict])
def get_top_offenders(period: str = "month", limit: int = 10):
    """Get top offenders for period"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Determine date range
        if period == "day":
            date_filter = "DATE(detected_at) = CURDATE()"
        elif period == "week":
            date_filter = "detected_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
        else:  # month
            date_filter = "detected_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
        
        cursor.execute(f"""
            SELECT 
                person_name as name,
                COUNT(*) as violations,
                MAX(location) as department
            FROM attendance
            WHERE {date_filter} AND overall_status = 'fail'
            GROUP BY person_name
            ORDER BY violations DESC
            LIMIT %s
        """, (limit,))
        
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@app.get("/api/reports/most-compliant", response_model=List[Dict])
def get_most_compliant(period: str = "month", limit: int = 10):
    """Get most compliant workers"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Determine date range
        if period == "day":
            date_filter = "DATE(detected_at) = CURDATE()"
        elif period == "week":
            date_filter = "detected_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
        else:  # month
            date_filter = "detected_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
        
        cursor.execute(f"""
            SELECT 
                person_name as name,
                MAX(location) as department,
                ROUND(SUM(CASE WHEN overall_status = 'pass' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as compliance
            FROM attendance
            WHERE {date_filter}
            GROUP BY person_name
            HAVING COUNT(*) >= 5
            ORDER BY compliance DESC
            LIMIT %s
        """, (limit,))
        
        results = cursor.fetchall()
        
        # Format compliance as percentage string
        for r in results:
            r['compliance'] = f"{r['compliance']}%"
        
        return results
    finally:
        cursor.close()
        conn.close()

# ==================== ALERTS APIs ====================

@app.get("/api/alerts", response_model=List[Dict])
def get_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50
):
    """Get all alerts with filters"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        where_clauses = []
        params = []
        
        if status:
            where_clauses.append("a.status = %s")
            params.append(status)
        
        if severity:
            where_clauses.append("severity = %s")
            params.append(severity)
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        cursor.execute(f"""
            SELECT 
                a.*,
                w.employee_id
            FROM alerts a
            LEFT JOIN workers w ON a.worker_name = w.name
            WHERE {where_sql}
            ORDER BY a.created_at DESC
            LIMIT %s
        """, params + [limit])
        
        alerts = cursor.fetchall()
        
        # Format timestamps
        for alert in alerts:
            if alert['created_at']:
                alert['time_ago'] = format_time_ago(alert['created_at'])
        
        return alerts
    except Exception as e:
        print(f"❌ Error in get_alerts: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/alerts/stats", response_model=Dict)
def get_alert_stats():
    """Get alert statistics"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Active alerts
        cursor.execute("SELECT COUNT(*) as active FROM alerts WHERE status = 'active'")
        active = cursor.fetchone()['active']
        
        # Resolved today
        cursor.execute("SELECT COUNT(*) as resolved FROM alerts WHERE status = 'resolved' AND DATE(resolved_at) = CURDATE()")
        resolved = cursor.fetchone()['resolved']
        
        # Average response time (in minutes)
        cursor.execute("""
            SELECT AVG(TIMESTAMPDIFF(MINUTE, created_at, resolved_at)) as avg_time
            FROM alerts
            WHERE status = 'resolved' AND resolved_at IS NOT NULL
        """)
        result = cursor.fetchone()
        avg_time = result['avg_time'] if result['avg_time'] else 0
        
        return {
            "active_alerts": active,
            "resolved_today": resolved,
            "avg_response_time": f"{round(avg_time, 1)}m"
        }
    finally:
        cursor.close()
        conn.close()

@app.post("/api/alerts", response_model=Dict)
def create_alert(alert: AlertCreate):
    """Create new alert"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO alerts (worker_id, worker_name, type, severity, message, location, gate)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            alert.worker_id,
            alert.worker_name,
            alert.type,
            alert.severity,
            alert.message,
            alert.location,
            alert.gate
        ))
        conn.commit()
        
        return {
            "status": "success",
            "id": cursor.lastrowid,
            "message": "Alert created successfully"
        }
    finally:
        cursor.close()
        conn.close()

@app.put("/api/alerts/{alert_id}/resolve", response_model=Dict)
def resolve_alert(alert_id: int, resolution: AlertResolve):
    """Mark alert as resolved"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        now = datetime.now()
        
        # Get alert creation time to calculate response time
        cursor.execute("SELECT created_at FROM alerts WHERE id = %s", (alert_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        created_at = result[0]
        response_time = int((now - created_at).total_seconds() / 60)  # in minutes
        
        cursor.execute("""
            UPDATE alerts
            SET status = 'resolved',
                resolved_at = %s,
                resolution_note = %s,
                response_time = %s
            WHERE id = %s
        """, (now, resolution.resolution_note, response_time, alert_id))
        conn.commit()
        
        return {"status": "success", "message": "Alert resolved successfully"}
    finally:
        cursor.close()
        conn.close()

# Helper function
def format_time_ago(dt):
    """Format datetime as time ago string"""
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours} hours ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes} minutes ago"
    else:
        return "just now"

# ==================== EXPORT REPORTS APIs ====================

from fastapi.responses import StreamingResponse
from utils.report_utils import generate_attendance_csv, generate_workers_csv, generate_compliance_csv
import io

@app.get("/api/reports/export/csv")
def export_csv_report(
    report_type: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Export report as CSV"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        if report_type == "attendance":
            # Get attendance records
            query = "SELECT * FROM attendance"
            params = []
            
            if start_date and end_date:
                query += " WHERE DATE(detected_at) BETWEEN %s AND %s"
                params = [start_date, end_date]
            
            query += " ORDER BY detected_at DESC LIMIT 1000"
            cursor.execute(query, params)
            records = cursor.fetchall()
            
            csv_content = generate_attendance_csv(records)
            filename = f"attendance_report_{datetime.now().strftime('%Y%m%d')}.csv"
            
        elif report_type == "workers":
            # Get workers
            cursor.execute("SELECT * FROM workers ORDER BY created_at DESC")
            workers = cursor.fetchall()
            
            csv_content = generate_workers_csv(workers)
            filename = f"workers_report_{datetime.now().strftime('%Y%m%d')}.csv"
            
        elif report_type == "compliance":
            # Get compliance data
            if not start_date or not end_date:
                raise HTTPException(status_code=400, detail="start_date and end_date required for compliance report")
            
            csv_content = generate_compliance_csv(start_date, end_date, conn)
            filename = f"compliance_report_{start_date}_to_{end_date}.csv"
            
        else:
            raise HTTPException(status_code=400, detail="Invalid report type")
        
        # Return CSV as downloadable file
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    finally:
        cursor.close()
        conn.close()

@app.get("/api/reports/export/pdf")
def export_pdf_report(
    report_type: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Export report as PDF (placeholder - requires PDF library)"""
    # TODO: Implement PDF generation using reportlab or weasyprint
    raise HTTPException(status_code=501, detail="PDF export coming soon. Use CSV export for now.")

# ==================== DASHBOARD CHARTS APIs ====================

@app.get("/api/dashboard/compliance-trend", response_model=List[Dict])
def get_compliance_trend(days: int = 7):
    """Get compliance trend for last N days"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                DATE(detected_at) as date,
                COUNT(*) as total,
                SUM(CASE WHEN overall_status = 'pass' THEN 1 ELSE 0 END) as passed,
                ROUND(SUM(CASE WHEN overall_status = 'pass' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as rate
            FROM attendance
            WHERE detected_at >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            GROUP BY DATE(detected_at)
            ORDER BY date
        """, (days,))
        
        results = cursor.fetchall()
        
        # Format for charts
        return [
            {
                "date": str(r['date']),
                "compliance_rate": float(r['rate']) if r['rate'] else 0,
                "total_checks": r['total'],
                "passed": r['passed']
            }
            for r in results
        ]
    finally:
        cursor.close()
        conn.close()

@app.get("/api/dashboard/violations-by-item", response_model=List[Dict])
def get_violations_by_item(days: int = 30):
    """Get violations breakdown by PPE item"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT ppe_status
            FROM attendance
            WHERE detected_at >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            AND overall_status = 'fail'
        """, (days,))
        
        records = cursor.fetchall()
        
        # Count violations per item
        violations = {
            'helmet': 0,
            'glows': 0,
            'sheao': 0,
            'glass': 0,
            'jacket': 0,
            'headphone': 0
        }
        
        for record in records:
            try:
                ppe_status = json.loads(record['ppe_status'])
                for item, status in ppe_status.items():
                    if item in violations and status is False:
                        violations[item] += 1
            except:
                pass
        
        return [
            {"item": item, "count": count}
            for item, count in violations.items()
        ]
    finally:
        cursor.close()
        conn.close()

# ==================== WORKER PHOTOS APIs ====================

import os
from fastapi import UploadFile, File
from fastapi.responses import FileResponse

# Define known_faces directory path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.dirname(script_dir)
KNOWN_FACES_DIR = os.path.join(backend_root, 'data', 'known_faces')
os.makedirs(KNOWN_FACES_DIR, exist_ok=True)

@app.post("/api/workers/{worker_id}/photo")
async def upload_worker_photo(worker_id: int, file: UploadFile = File(...)):
    """Upload worker photo directly to Database securely as Base64 Text"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Get worker name from database to ensure they exist
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name FROM workers WHERE id = %s", (worker_id,))
        worker = cursor.fetchone()
        
        if not worker:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Worker not found")
        
        worker_name = worker['name']
        
        # Encode image directly to Base64 String
        import base64
        content = await file.read()
        encoded = base64.b64encode(content).decode('utf-8')
        mime_type = file.content_type
        photo_base64 = f"data:{mime_type};base64,{encoded}"
        
        # Save photo specifically inside the database
        try:
            cursor.execute("UPDATE workers SET photo_url = %s WHERE id = %s", (photo_base64, worker_id))
            conn.commit()
            db_updated = True
            message = "Photo saved directly to TiDB Cloud Database successfully."
        except mysql.connector.Error as db_err:
            print(f"Error updating photo in DB: {db_err}")
            db_updated = False
            conn.rollback()
            message = "Failed to save to database."
        
        # Optionally, still write it to known_faces to allow for local dev usage
        try:
            worker_face_dir = os.path.join(KNOWN_FACES_DIR, worker_name)
            os.makedirs(worker_face_dir, exist_ok=True)
            import time
            ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
            timestamp = int(time.time())
            filename = f"{worker_name}_{timestamp}.{ext}"
            filepath = os.path.join(worker_face_dir, filename)
            
            with open(filepath, "wb") as f:
                f.write(content)
        except Exception as e:
            print(f"Non-critical filesystem save error on Cloud: {e}")
            filename = None

        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "filename": filename,
            "message": message,
            "db_updated": db_updated
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import Response

@app.get("/api/workers/{worker_id}/photo")
def get_worker_photo(worker_id: int):
    """Get worker's primary photo"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT photo_url, name FROM workers WHERE id = %s", (worker_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        if not result['photo_url']:
            raise HTTPException(status_code=404, detail="No photo uploaded for this worker")
        
        # If it's a base64 encoded photo from DB:
        if result['photo_url'].startswith('data:image'):
            import base64
            header, encoded = result['photo_url'].split(",", 1)
            mime_type = header.split(":")[1].split(";")[0]
            img_bytes = base64.b64decode(encoded)
            return Response(content=img_bytes, media_type=mime_type)
        else:
            # Fallback for old file path based deployment
            filepath = os.path.join(KNOWN_FACES_DIR, result['photo_url'])
            if not os.path.exists(filepath):
                raise HTTPException(status_code=404, detail="Photo file not found")
            return FileResponse(filepath)
    finally:
        cursor.close()
        conn.close()

@app.get("/api/workers/{worker_id}/photos")
def get_worker_photos(worker_id: int):
    """Get all photos for a worker"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT name FROM workers WHERE id = %s", (worker_id,))
        worker = cursor.fetchone()
        
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        worker_name = worker['name']
        worker_face_dir = os.path.join(KNOWN_FACES_DIR, worker_name)
        
        if not os.path.exists(worker_face_dir):
            return {"photos": []}
        
        # List all photos for this worker
        photos = []
        for filename in os.listdir(worker_face_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                photos.append({
                    "filename": filename,
                    "url": f"/api/workers/{worker_id}/photo/{filename}",
                    "path": f"{worker_name}/{filename}"
                })
        
        return {"photos": photos, "count": len(photos)}
    finally:
        cursor.close()
        conn.close()

# ==================== BULK IMPORT APIs ====================

@app.post("/api/workers/bulk-import")
async def bulk_import_workers(file: UploadFile = File(...)):
    """Bulk import workers from CSV"""
    try:
        # Read CSV
        content = await file.read()
        csv_file = io.StringIO(content.decode('utf-8'))
        reader = csv.DictReader(csv_file)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        imported = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                cursor.execute("""
                    INSERT INTO workers (employee_id, name, department, rfid_tag, phone, email, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    row.get('employee_id'),
                    row.get('name'),
                    row.get('department'),
                    row.get('rfid_tag'),
                    row.get('phone'),
                    row.get('email'),
                    row.get('status', 'active')
                ))
                imported += 1
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "imported": imported,
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== EMAIL ALERTS (Placeholder) ====================

@app.post("/api/alerts/send-email")
def send_alert_email_api(alert_id: int):
    """Send email notification for alert (API endpoint)"""
    # TODO: Implement email sending using smtplib or SendGrid
    raise HTTPException(status_code=501, detail="Email alerts coming soon")
