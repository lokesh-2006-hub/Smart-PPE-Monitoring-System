import serial
import time
import requests
import sys
import json
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000/api/attendance/rfid"
SERIAL_PORT = "COM3"  # Default, can be passed as argument
BAUD_RATE = 9600

def find_arduino_port():
    """Try to auto-detect Arduino port (Windows specific)"""
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "Arduino" in p.description or "CH340" in p.description:
            return p.device
    return None

def main():
    port = SERIAL_PORT
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        detected = find_arduino_port()
        if detected:
            print(f"Auto-detected Arduino on {detected}")
            port = detected
        else:
            print(f"No Arduino detected. Using default {port}")

    print(f"Connecting to {port} at {BAUD_RATE} baud...")
    
    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset
        print("Connected! Waiting for RFID tags...")
        print("Press Ctrl+C to exit.")

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print(f"Received: {line}")
                    
                    # Parse UID
                    if line.startswith("UID:"):
                        uid = line.replace("UID:", "").strip()
                        print(f"Processing Tag: {uid}")
                        
                        # Send to API
                        try:
                            payload = {
                                "rfid_tag": uid,
                                "timestamp": int(time.time()),
                                "gate": "Main Gate"
                            }
                            response = requests.post(API_URL, json=payload)
                            
                            if response.status_code == 200:
                                data = response.json()
                                if data.get("status") == "success":
                                    print(f"✅ Attendance Marked: {data.get('worker_name')}")
                                else:
                                    print(f"❌ Error: {data.get('message')}")
                            else:
                                print(f"❌ Server Error: {response.status_code} - {response.text}")
                                
                        except requests.exceptions.ConnectionError:
                            print("❌ Could not connect to backend API. Is it running?")
                        except Exception as e:
                            print(f"❌ Error sending data: {e}")
                            
            time.sleep(0.1)

    except serial.SerialException as e:
        print(f"Error opening serial port {port}: {e}")
        print("Check connection and port name.")
    except KeyboardInterrupt:
        print("\nExiting...")
        if 'ser' in locals() and ser.is_open:
            ser.close()
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
