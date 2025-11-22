"""
Add photo_url column to workers table
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
        
        print("Adding photo_url column to workers table...")
        
        # Check if column already exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'ppe' 
            AND TABLE_NAME = 'workers' 
            AND COLUMN_NAME = 'photo_url'
        """)
        
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE workers 
                ADD COLUMN photo_url VARCHAR(255) AFTER email
            """)
            conn.commit()
            print("✓ photo_url column added successfully")
        else:
            print("- photo_url column already exists")
        
        cursor.close()
        conn.close()
        print("\n✅ Migration completed!")
        return True
        
    except mysql.connector.Error as err:
        print(f"\n❌ Error: {err}")
        return False

if __name__ == "__main__":
    migrate()
