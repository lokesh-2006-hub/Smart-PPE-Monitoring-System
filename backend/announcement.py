import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST","localhost"),
    user=os.getenv("DB_USER","root"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME","ppe")
)
cur =conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS announcement (id INT AUTO_INCREMENT PRIMARY KEY,content TEXT NOT NULL,author VARCHAR(255),created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
conn.commit()