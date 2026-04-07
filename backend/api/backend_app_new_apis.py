
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

class WorkerUpdate(BaseModel):
    employee_id: Optional[str] = None
    name: Optional[str] = None
    department: Optional[str] = None
    rfid_tag: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    address:Optional[str]=None
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

# ==================== WORKERS MANAGEMENT APIs ====================

@app.get("/api/workers", response_model=Dict)
def list_workers(
    page: int = 1,
    limit: int = 100,
    search: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    address:Optional[str]=None
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
            INSERT INTO workers (employee_id, name, department, rfid_tag, phone, email, status,address)
            VALUES (%s, %s, %s, %s, %s, %s, %s,%s)
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
            params.append(worker.rfid_tag)
        if worker.phone is not None:
            updates.append("phone = %s")
            params.append(worker.phone)
        if worker.email is not None:
            updates.append("email = %s")
            params.append(worker.email)
        if worker.status is not None:
            updates.append("status = %s")
            params.append(worker.status)
        if worker.address is not None:
            updates.append("address =%s")
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
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/workers/{worker_id}", response_model=Dict)
def delete_worker(worker_id: int):
    """Delete/deactivate worker"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Soft delete - set status to inactive
        cursor.execute("UPDATE workers SET status = 'inactive' WHERE id = %s", (worker_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        return {"status": "success", "message": "Worker deactivated successfully"}
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
                id,
                person_name as worker_name,
                person_id as worker_id,
                time_in,
                time_out,
                overall_status as ppe_status,
                location,
                gate,
                source
            FROM attendance
            WHERE {where_sql}
            ORDER BY detected_at DESC
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
            where_clauses.append("status = %s")
            params.append(status)
        
        if severity:
            where_clauses.append("severity = %s")
            params.append(severity)
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        cursor.execute(f"""
            SELECT * FROM alerts
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT %s
        """, params + [limit])
        
        alerts = cursor.fetchall()
        
        # Format timestamps
        for alert in alerts:
            if alert['created_at']:
                alert['time_ago'] = format_time_ago(alert['created_at'])
        
        return alerts
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
