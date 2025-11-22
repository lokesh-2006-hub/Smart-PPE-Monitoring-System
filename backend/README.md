# Backend - Smart PPE Compliance Monitoring System

This directory contains all backend components for the Smart PPE Compliance Monitoring System, including API services, detection scripts, database migrations, and utilities.

## 📁 Directory Structure

```
backend/
├── api/                          # FastAPI applications
│   ├── backend_app.py           # Main API with all endpoints
│   └── backend_app_new_apis.py  # Additional UI redesign endpoints
├── detection/                    # PPE detection and video streaming
│   ├── ppe_stream_server.py     # Flask server for web UI streaming
│   └── ppe_attendance_combined.py # Standalone detection script
├── migrations/                   # Database migration scripts
│   ├── 001_add_source_column.py
│   └── 002_ui_redesign_tables.py
├── utils/                        # Utility scripts
│   ├── report_utils.py          # CSV report generation
│   └── test_api.py              # API testing script
├── models/                       # ML models
│   └── my_model.pt              # YOLO PPE detection model
├── data/                         # Data files
│   └── known_faces/             # Face recognition training data
│       ├── augustin/
│       ├── deepak/
│       ├── dharsan/
│       └── lokesh/
└── requirements.txt              # Python dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MySQL database
- CUDA-compatible GPU (optional, for faster detection)

### Installation

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set up database:**
   ```bash
   # Run migrations
   python migrations/001_add_source_column.py
   python migrations/002_ui_redesign_tables.py
   ```

3. **Configure database connection:**
   
   Edit the `DB_CONFIG` in `api/backend_app.py`:
   ```python
   DB_CONFIG = {
       "host": "localhost",
       "user": "root",
       "password": "your_password",
       "database": "ppe"
   }
   ```

## 🎯 Running the Backend

### Option 1: Full System (Web Dashboard)

Run all three components in separate terminals:

**Terminal 1 - FastAPI Backend:**
```bash
cd backend
python -m uvicorn api.backend_app:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend (from project root):**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Detection with Streaming:**
```bash
cd backend/detection
python ppe_stream_server.py --source 0
```

Access the web dashboard at: `http://localhost:5173`

### Option 2: Quick Testing (No Web UI)

**Terminal 1 - Backend API (optional):**
```bash
cd backend
python -m uvicorn api.backend_app:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Standalone Detection:**
```bash
cd backend/detection
python ppe_attendance_combined.py --source 0
```

View detection in OpenCV window (press 'q' to quit)

## 📡 API Endpoints

### Core Endpoints

#### Register Person
```http
POST /register_person
Content-Type: application/json

{
  "name": "John Doe",
  "employee_id": "EMP001",
  "meta": {}
}
```

#### Update Attendance
```http
POST /update_attendance
Content-Type: application/json

{
  "name": "John Doe",
  "time": 1234567890,
  "status": "pass",
  "source": "camera",
  "helmet": true,
  "glows": true,
  "sheao": true,
  "glass": false,
  "jacket": true,
  "headphone": false
}
```

#### List Persons
```http
GET /list_persons?limit=100
```

#### Daily Report
```http
GET /daily_report?date=2025-11-21
```

### Worker Management

```http
GET  /workers?page=1&limit=100
POST /workers
GET  /workers/{worker_id}
PUT  /workers/{worker_id}
DELETE /workers/{worker_id}
```

### Attendance Management

```http
GET /attendance/logs?date=2025-11-21
GET /attendance/today
POST /attendance/{worker_id}/checkout
```

### Alerts

```http
GET  /alerts?status=active&severity=critical
POST /alerts
PUT  /alerts/{alert_id}/resolve
GET  /alerts/stats
```

### Reports

```http
GET /reports/today-summary
GET /reports/top-offenders?period=month&limit=10
GET /reports/most-compliant?period=month&limit=10
```

## 🔧 Detection Scripts

### ppe_stream_server.py

**Purpose:** Streams PPE detection video feed to web UI

**Features:**
- MJPEG streaming to browser
- Face recognition integration
- Real-time PPE detection
- Sends data to backend API

**Command Line Options:**
```bash
python ppe_stream_server.py \
  --model ../models/my_model.pt \
  --source 0 \
  --known-faces ../data/known_faces \
  --port 5000
```

**Arguments:**
- `--model`: Path to YOLO model (default: `../models/my_model.pt`)
- `--source`: Video source (camera index, file, URL)
- `--known-faces`: Path to known faces directory (default: `../data/known_faces`)
- `--port`: Flask server port (default: 5000)

### ppe_attendance_combined.py

**Purpose:** Standalone PPE detection with local display

**Features:**
- OpenCV window display
- Face recognition
- PPE detection and tracking
- Local CSV attendance file
- API integration

**Command Line Options:**
```bash
python ppe_attendance_combined.py \
  --model ../models/my_model.pt \
  --source 0 \
  --thresh 0.5 \
  --scale 0.5 \
  --record
```

**Arguments:**
- `--model`: Path to YOLO model (default: `../models/my_model.pt`)
- `--source`: Video source
- `--thresh`: Confidence threshold (default: 0.5)
- `--scale`: Face recognition scale factor (default: 0.5)
- `--record`: Save output video

## 🗄️ Database Migrations

### Running Migrations

Migrations are numbered and should be run in order:

```bash
cd backend/migrations
python 001_add_source_column.py
python 002_ui_redesign_tables.py
```

### Migration 001: Add Source Column
Adds `source` column to `attendance` table to track detection source (camera, video, image, folder).

### Migration 002: UI Redesign Tables
Creates:
- `workers` table - Worker information
- `alerts` table - System alerts
- `reports` table - Generated reports
- Enhances `attendance` table with additional fields

## 🧪 Testing

### Test the API

```bash
cd backend/utils
python test_api.py
```

This sends a sample attendance update to verify the backend is working.

### Manual API Testing

Use curl or Postman:
```bash
curl -X POST http://localhost:8000/update_attendance \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TestWorker",
    "time": 1234567890,
    "status": "pass",
    "source": "camera",
    "helmet": true,
    "glows": true,
    "sheao": true,
    "glass": false,
    "jacket": true,
    "headphone": false
  }'
```

## 🎨 Adding Known Faces

To add a new person for face recognition:

1. Create a folder in `backend/data/known_faces/` with the person's name
2. Add multiple photos of the person (*.jpg, *.jpeg, *.png)
3. Restart the detection script

Example:
```
backend/data/known_faces/
└── john_doe/
    ├── photo1.jpg
    ├── photo2.jpg
    └── photo3.jpg
```

## ⚙️ Configuration

### Database Configuration

Edit `DB_CONFIG` in `api/backend_app.py`:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "database": "ppe"
}
```

### Detection Parameters

In the detection scripts, you can adjust:

**ppe_stream_server.py:**
- `TIME_WINDOW = 30.0` - Monitor each person for 30 seconds
- `PERSON_TIMEOUT = 2.0` - Reset if person disappears for 2 seconds
- `PPE_CONFIRM_RATIO = 0.6` - 60% of frames must show PPE item
- `YOLO_FRAME_SKIP = 5` - Run YOLO every 5 frames
- `FACE_FRAME_SKIP = 3` - Run face detection every 3 frames
- `CONF_THRESH = 0.5` - Confidence threshold for detections

**ppe_attendance_combined.py:**
- `TIME_WINDOW = 10.0` - Monitor duration (use 60.0 for production)
- `PERSON_TIMEOUT = 2.0` - Reset timeout
- `PPE_CONFIRM_RATIO = 0.6` - Confirmation ratio

## 📝 Utilities

### report_utils.py

Utility functions for generating CSV reports:
- `generate_attendance_csv(records)` - Generate attendance CSV
- `generate_workers_csv(workers)` - Generate workers CSV
- `generate_compliance_csv(start_date, end_date, conn)` - Generate compliance report

### test_api.py

Simple script to test the backend API is running and accepting requests.

## 🐛 Troubleshooting

### Backend won't start
- Check MySQL is running: `mysql -u root -p`
- Verify database exists: `SHOW DATABASES;`
- Run migrations if tables don't exist

### Face recognition not working
- Install dlib: `pip install dlib`
- Or use LBPH fallback (OpenCV-contrib required)
- Check known_faces directory exists and has photos

### YOLO model not found
- Verify `backend/models/my_model.pt` exists
- Use absolute path if relative path fails
- Check model file permissions

### Video stream not showing
- Verify Flask server is running on port 5000
- Check frontend is configured to connect to `http://localhost:5000`
- Ensure camera is not in use by another application

### Database connection errors
- Check MySQL credentials in `DB_CONFIG`
- Verify MySQL service is running
- Check firewall settings if using remote database

## 📚 Dependencies

See `requirements.txt` for full list:
- `fastapi` - API framework
- `uvicorn` - ASGI server
- `mysql-connector-python` - MySQL database
- `ultralytics` - YOLO  detection
- `opencv-python` - Computer vision
- `face-recognition` - Face recognition (optional)
- `flask` - Streaming server
- `flask-cors` - CORS middleware
- `requests` - HTTP requests

## 🔄 Workflow

1. **Detection Script** captures video and detects faces + PPE
2. **Face Recognition** identifies known persons
3. **PPE Detection** checks for required safety equipment
4. **Tracking Logic** monitors person for TIME_WINDOW seconds
5. **API Update** sends final result to backend
6. **Database Storage** stores attendance and PPE compliance
7. **Frontend Display** shows real-time data and statistics

## 📧 Support

For issues or questions, refer to the main project documentation in the parent directory.
