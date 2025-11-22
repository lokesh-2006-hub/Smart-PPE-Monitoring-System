"""
Migration script to add source column to attendance table
"""
import mysql.connector
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
        
        # Check if column exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'ppe' 
            AND TABLE_NAME = 'attendance' 
            AND COLUMN_NAME = 'source'
        """)
        
        exists = cursor.fetchone()[0]
        
        if exists == 0:
            print("Adding 'source' column to attendance table...")
            cursor.execute("""
                ALTER TABLE attendance 
                ADD COLUMN source VARCHAR(100) AFTER detected_at
            """)
            conn.commit()
            print("✓ Column added successfully!")
        else:
            print("✓ Column 'source' already exists.")
        
        cursor.close()
        conn.close()
        print("\nMigration completed successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    
    return True

if __name__ == "__main__":
    migrate()
