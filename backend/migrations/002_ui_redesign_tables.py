"""
Database migration script for UI redesign
Creates new tables: workers, alerts, reports
Enhances attendance table with additional fields
"""
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "ppe")
}

def migrate():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Starting database migration...")
        print("=" * 50)
        
        # 1. Create workers table
        print("\n1. Creating 'workers' table...")
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
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_employee_id (employee_id),
                INDEX idx_status (status),
                INDEX idx_department (department)
            )
        """)
        print("   ✓ Workers table created")
        
        # 2. Create alerts table
        print("\n2. Creating 'alerts' table...")
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
        print("   ✓ Alerts table created")
        
        # 3. Create reports table
        print("\n3. Creating 'reports' table...")
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
        print("   ✓ Reports table created")
        
        # 4. Add columns to attendance table
        print("\n4. Enhancing 'attendance' table...")
        
        # Check and add time_in column
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'ppe' 
            AND TABLE_NAME = 'attendance' 
            AND COLUMN_NAME = 'time_in'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE attendance ADD COLUMN time_in DATETIME AFTER detected_at")
            print("   ✓ Added 'time_in' column")
        else:
            print("   - 'time_in' column already exists")
        
        # Check and add time_out column
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'ppe' 
            AND TABLE_NAME = 'attendance' 
            AND COLUMN_NAME = 'time_out'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE attendance ADD COLUMN time_out DATETIME AFTER time_in")
            print("   ✓ Added 'time_out' column")
        else:
            print("   - 'time_out' column already exists")
        
        # Check and add location column
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'ppe' 
            AND TABLE_NAME = 'attendance' 
            AND COLUMN_NAME = 'location'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE attendance ADD COLUMN location VARCHAR(100) AFTER source")
            print("   ✓ Added 'location' column")
        else:
            print("   - 'location' column already exists")
        
        # Check and add gate column
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'ppe' 
            AND TABLE_NAME = 'attendance' 
            AND COLUMN_NAME = 'gate'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE attendance ADD COLUMN gate VARCHAR(50) AFTER location")
            print("   ✓ Added 'gate' column")
        else:
            print("   - 'gate' column already exists")
        
        # 5. Migrate existing persons data to workers table
        print("\n5. Migrating data from 'persons' to 'workers'...")
        cursor.execute("SELECT COUNT(*) FROM workers")
        worker_count = cursor.fetchone()[0]
        
        if worker_count == 0:
            cursor.execute("""
                INSERT INTO workers (employee_id, name, status, created_at)
                SELECT employee_id, name, 'active', created_at
                FROM persons
                WHERE name NOT IN (SELECT name FROM workers)
            """)
            migrated = cursor.rowcount
            print(f"   ✓ Migrated {migrated} records from persons to workers")
        else:
            print(f"   - Workers table already has {worker_count} records")
        
        # 6. Update attendance table with time_in from detected_at
        print("\n6. Updating attendance time_in from detected_at...")
        cursor.execute("""
            UPDATE attendance 
            SET time_in = detected_at 
            WHERE time_in IS NULL AND detected_at IS NOT NULL
        """)
        updated = cursor.rowcount
        print(f"   ✓ Updated {updated} attendance records")
        
        conn.commit()
        print("\n" + "=" * 50)
        print("✅ Migration completed successfully!")
        print("=" * 50)
        
        cursor.close()
        conn.close()
        return True
        
    except mysql.connector.Error as err:
        print(f"\n❌ Error: {err}")
        return False

if __name__ == "__main__":
    migrate()
