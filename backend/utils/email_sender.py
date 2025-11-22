"""
Email Alert Utility for PPE Compliance System
Sends email notifications when PPE violations occur
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import mysql.connector
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_db_connection():
    """Get MySQL database connection"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "ppe")
    )


def get_smtp_settings():
    """Fetch SMTP settings from database"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT setting_key, setting_value 
            FROM settings 
            WHERE category='notifications'
        """)
        rows = cursor.fetchall()
        
        settings = {}
        for row in rows:
            key = row['setting_key']
            value = row['setting_value']
            
            # Parse JSON values
            try:
                parsed_value = json.loads(value)
            except:
                if value.replace('.', '', 1).isdigit():
                    parsed_value = int(value)
                else:
                    parsed_value = value
            
            settings[key] = parsed_value
        
        return settings
    finally:
        cursor.close()
        conn.close()


def get_alert_settings():
    """Fetch alert settings from database"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT setting_key, setting_value 
            FROM settings 
            WHERE category='alerts'
        """)
        rows = cursor.fetchall()
        
        settings = {}
        for row in rows:
            key = row['setting_key']
            value = row['setting_value']
            
            # Parse JSON values
            try:
                parsed_value = json.loads(value)
            except:
                if value.lower() == 'true':
                    parsed_value = True
                elif value.lower() == 'false':
                    parsed_value = False
                else:
                    parsed_value = value
            
            settings[key] = parsed_value
        
        return settings
    finally:
        cursor.close()
        conn.close()


def format_missing_ppe(ppe_status):
    """Extract list of missing PPE items"""
    missing = []
    for item, detected in ppe_status.items():
        if not detected:
            missing.append(item.capitalize())
    return missing


def send_alert_email(worker_name, ppe_status, timestamp=None):
    """
    Send PPE violation alert email to configured recipients
    
    Args:
        worker_name: Name of the worker
        ppe_status: Dictionary of PPE items and their detection status
        timestamp: Optional timestamp (defaults to now)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Get settings
        smtp_settings = get_smtp_settings()
        alert_settings = get_alert_settings()
        
        # Check if email notifications are enabled
        if not alert_settings.get('enable_email', False):
            print("Email notifications are disabled")
            return False
        
        # Get email configuration
        smtp_host = smtp_settings.get('smtp_host', 'smtp.gmail.com')
        smtp_port = smtp_settings.get('smtp_port', 587)
        smtp_user = smtp_settings.get('smtp_user', '')
        smtp_password = smtp_settings.get('smtp_password', '')
        alert_email_list = alert_settings.get('alert_email_list', '')
        
        # Validate configuration
        if not smtp_user or not smtp_password:
            print("SMTP credentials not configured")
            return False
        
        if not alert_email_list:
            print("No alert email recipients configured")
            return False
        
        # Get missing PPE items
        missing_ppe = format_missing_ppe(ppe_status)
        
        if not missing_ppe:
            print("No PPE violations detected")
            return False
        
        # Format timestamp
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = alert_email_list
        msg['Subject'] = f'⚠️ PPE Violation Alert - {worker_name}'
        
        # Email body
        body = f"""
PPE Compliance Violation Detected

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Worker Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Name: {worker_name}
Time: {timestamp}
Status: FAILED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Missing PPE Items:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{chr(10).join(['• ' + item for item in missing_ppe])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Action Required:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please ensure the worker is equipped with all required 
PPE items before allowing entry to the premises.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is an automated alert from the Smart PPE 
Compliance Monitoring System.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        print(f"Connecting to SMTP server: {smtp_host}:{smtp_port}")
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        
        print(f"Logging in as: {smtp_user}")
        server.login(smtp_user, smtp_password)
        
        print(f"Sending alert email to: {alert_email_list}")
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Alert email sent successfully for {worker_name}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP Authentication Error: {e}")
        print("Check your SMTP username and password in Settings")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


if __name__ == "__main__":
    # Test email sending
    test_ppe_status = {
        'helmet': True,
        'jacket': False,
        'gloves': False,
        'shoes': True,
        'headphone': True
    }
    
    success = send_alert_email("Test Worker", test_ppe_status)
    print(f"Email sent: {success}")
