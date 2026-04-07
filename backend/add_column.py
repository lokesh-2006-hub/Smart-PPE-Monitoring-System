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
cursor= conn.cursor()
cursor.execute("ALTER TABLE workers ADD COLUMN address VARCHAR(20)")