"""
Utility functions for generating CSV reports
"""
import csv
import io
from datetime import datetime


def generate_attendance_csv(records):
    """Generate CSV content for attendance records"""
    output = io.StringIO()
    if not records:
        return ""
    
    writer = csv.DictWriter(output, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)
    
    return output.getvalue()


def generate_workers_csv(workers):
    """Generate CSV content for workers list"""
    output = io.StringIO()
    if not workers:
        return ""
    
    writer = csv.DictWriter(output, fieldnames=workers[0].keys())
    writer.writeheader()
    writer.writerows(workers)
    
    return output.getvalue()


def generate_compliance_csv(start_date, end_date, conn):
    """Generate CSV content for compliance report"""
    cursor = conn.cursor(dictionary=True)
    
    # Get compliance data for the date range
    cursor.execute("""
        SELECT 
            person_name,
            detected_at,
            overall_status,
            ppe_status,
            location,
            source
        FROM attendance
        WHERE DATE(detected_at) BETWEEN %s AND %s
        ORDER BY detected_at DESC
    """, (start_date, end_date))
    
    records = cursor.fetchall()
    cursor.close()
    
    output = io.StringIO()
    if not records:
        return ""
    
    writer = csv.DictWriter(output, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)
    
    return output.getvalue()
