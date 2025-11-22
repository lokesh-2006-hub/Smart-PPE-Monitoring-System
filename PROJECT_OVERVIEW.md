# Smart PPE Compliance Monitoring System

## 🎯 Project Overview

This is an **AI-powered Smart PPE (Personal Protective Equipment) Compliance Monitoring System** designed for industrial safety monitoring. The system automatically detects workers, identifies them using facial recognition, monitors their PPE compliance in real-time, and maintains attendance records.

---

## 🚀 What Does This Project Do?

### Core Capabilities

1. **Real-Time Worker Detection & Identification**
   - Detects workers entering the monitored area using facial recognition
   - Identifies workers by name using pre-trained face encodings
   - Supports both `face_recognition` (dlib) and OpenCV LBPH fallback methods

2. **PPE Compliance Detection**
   - Monitors whether workers are wearing required safety equipment:
     - ✅ **Helmet/Hard Hat**
     - ✅ **Safety Jacket/Vest**
     - ✅ **Safety Shoes/Boots**
     - ✅ **Gloves**
     - ✅ **Safety Goggles/Glasses**
     - ✅ **Headphones** (for noise protection)
   - Uses YOLO (You Only Look Once) deep learning model for PPE detection

3. **Continuous Monitoring System**
   - Tracks each worker for a configurable time window (default: 10 seconds)
   - Requires consistent PPE presence (60% of frames) to pass compliance
   - Prevents false positives from temporary occlusions

4. **Automated Attendance & Compliance Recording**
   - Automatically marks attendance when a worker is detected
   - Records PPE compliance status (Pass/Fail) for each worker
   - Stores all data in MySQL database with timestamps

5. **Live Video Streaming**
   - Streams annotated video feed to web dashboard
   - Shows real-time detection boxes and labels on video
   - Displays monitoring status and countdown timers

6. **Web Dashboard Interface**
   - Modern React-based web interface
   - Shows live video feed with detection overlays
   - Displays latest scan results with worker details
   - Shows daily statistics (total entries, compliance rate, violations)
   - Real-time updates every 2 seconds

---

## 🏗️ System Architecture

The project consists of **4 main components**:

### 1. **Detection & Streaming Server** (`ppe_stream_server.py`)
- **Port:** 5000
- **Technology:** Flask + OpenCV + YOLO + face_recognition
- **Functions:**
  - Captures video from camera/IP camera
  - Performs face detection and recognition
  - Runs YOLO model for PPE detection
  - Associates PPE items with detected workers
  - Streams annotated video via MJPEG
  - Sends compliance data to backend API

### 2. **Backend API Server** (`backend_app.py`)
- **Port:** 8000
- **Technology:** FastAPI + MySQL
- **Functions:**
  - Provides REST API endpoints
  - Manages database operations
  - Stores person records and attendance data
  - Generates daily reports and statistics
  - Serves data to frontend dashboard

### 3. **Frontend Dashboard** (`frontend/`)
- **Port:** 5173
- **Technology:** React + Vite
- **Functions:**
  - Displays live video feed from streaming server
  - Shows latest detection results
  - Displays real-time statistics
  - Provides modern, responsive UI

### 4. **MySQL Database** (`ppe` database)
- **Tables:**
  - `persons` - Stores registered worker information
  - `attendance` - Records all detection events with PPE status

---

## 📊 How It Works - Step by Step

### Detection Flow

```
1. Video Input (IP Camera/Webcam)
   ↓
2. Face Detection & Recognition
   - Detects faces in frame
   - Identifies worker by name
   ↓
3. Body Box Estimation
   - Estimates worker's body area based on face location
   ↓
4. PPE Detection (YOLO)
   - Detects all PPE items in full frame
   - Checks if PPE overlaps with worker's body box
   ↓
5. Continuous Monitoring (10 seconds)
   - Tracks PPE presence over time
   - Requires 60% consistency to pass
   ↓
6. Result Finalization
   - Determines Pass/Fail status
   - Sends to API: POST /update_attendance
   - Marks attendance locally
   ↓
7. Database Storage
   - Stores in MySQL database
   - Creates/updates person record
   - Records attendance with timestamp
   ↓
8. Dashboard Display
   - Frontend polls API every 2 seconds
   - Fetches latest detection: GET /attendance/latest
   - Updates UI with worker info and PPE status
```

### Video Streaming Flow

```
Detection Server (Port 5000)
   ↓
Annotated frames with detection boxes
   ↓
MJPEG Stream: http://localhost:5000/video_feed
   ↓
Frontend Dashboard displays in <img> tag
   ↓
User sees live video with real-time detections
```

---

## 🔧 Key Features Explained

### 1. **Continuous Presence Monitoring**
Instead of making instant decisions, the system:
- Monitors each worker for 10 seconds (configurable)
- Records PPE status in each frame
- Requires PPE to be present in 60% of frames
- This prevents false failures due to temporary occlusions

### 2. **Body Box Association**
- The system estimates the worker's full body area based on detected face
- PPE items are only counted if they overlap with this body area
- This prevents counting PPE worn by other people in frame

### 3. **Person Timeout**
- If a worker disappears for >2 seconds, monitoring resets
- Prevents mixing data from different workers
- Ensures accurate per-person tracking

### 4. **Dual Recognition Methods**
- **Primary:** face_recognition (dlib) - More accurate
- **Fallback:** OpenCV LBPH - Works without dlib
- Automatically selects based on available libraries

---

## 📡 API Endpoints

### Backend API (Port 8000)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/update_attendance` | POST | Record new detection with PPE status |
| `/attendance/latest` | GET | Get most recent detection |
| `/attendance/{name}` | GET | Get history for specific person |
| `/persons` | GET | List all registered persons |
| `/reports/daily` | GET | Get daily statistics |
| `/register_person` | POST | Register new person |

### Streaming Server (Port 5000)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/video_feed` | GET | MJPEG video stream |
| `/status` | GET | Server status check |

---

## 💾 Database Schema

### `persons` Table
```sql
- id (INT, PRIMARY KEY)
- name (VARCHAR, UNIQUE)
- employee_id (VARCHAR)
- meta (TEXT, JSON)
- created_at (DATETIME)
```

### `attendance` Table
```sql
- id (INT, PRIMARY KEY)
- person_id (INT, FOREIGN KEY)
- person_name (VARCHAR)
- detected_at (DATETIME)
- ppe_status (TEXT, JSON) - Individual PPE items
- overall_status (VARCHAR) - 'pass' or 'fail'
- raw_payload (TEXT, JSON) - Full detection data
```

---

## 🎮 How to Use

### Starting the System

1. **Start Backend API:**
   ```bash
   cd d:\SIH1
   python -m uvicorn backend_app:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start Frontend Dashboard:**
   ```bash
   cd d:\SIH1\frontend
   npm run dev
   ```

3. **Start Detection & Streaming Server:**
   ```bash
   cd d:\SIH1
   # For webcam (camera 0)
   python ppe_stream_server.py --source 0
   
   # For IP camera
   python ppe_stream_server.py --source http://10.48.36.219:8080/video
   ```

4. **Access Dashboard:**
   - Open browser: http://localhost:5173
   - You'll see live video feed with detections
   - Latest scan results update automatically

### Adding New Workers

1. Create folder: `D:\sf\my_model\known_faces\{worker_name}`
2. Add 2-3 clear face photos of the worker
3. Restart the detection server
4. System will automatically recognize them

---

## 📈 What You See in the Dashboard

### Live Feed Section
- Real-time video with detection boxes
- Green boxes around detected PPE items
- Yellow box showing estimated body area
- Status text showing monitoring progress

### Statistics Cards
- **Entries Today:** Total detections today
- **Compliance Rate:** Percentage of workers who passed
- **Violations:** Number of failed compliance checks

### Latest Scan Panel
- Worker name and ID
- Detection timestamp
- Pass/Fail status badge
- PPE checklist with ✓/✗ for each item
- Allow/Deny action buttons (UI only)

---

## 🔍 Current Detection Results

Based on your logs, the system is currently:
- ✅ Successfully detecting worker "deepak"
- ✅ Streaming video to dashboard (GET /video_feed requests)
- ✅ Running PPE detection
- ✅ Sending results to API (record IDs: 41-48)
- ⚠️ Marking as "fail" - worker needs to wear proper PPE!

---

## 🛠️ Configuration Options

### Detection Parameters (in `ppe_stream_server.py`)
- `TIME_WINDOW = 10.0` - Monitoring duration (seconds)
- `PERSON_TIMEOUT = 2.0` - Time before resetting (seconds)
- `PPE_CONFIRM_RATIO = 0.6` - Required consistency (60%)
- `FACE_SCALE = 0.5` - Face detection resize factor
- `CONF_THRESH = 0.5` - YOLO confidence threshold

### Model Paths
- YOLO Model: `D:\sf\my_model\my_model.pt`
- Known Faces: `D:\sf\my_model\known_faces`

---

## 🎯 Use Cases

1. **Construction Sites** - Ensure workers wear helmets, vests, boots
2. **Manufacturing Plants** - Monitor PPE compliance at entry gates
3. **Chemical Facilities** - Verify protective equipment usage
4. **Warehouses** - Track safety compliance and attendance
5. **Mining Operations** - Ensure proper safety gear before entry

---

## 🔐 Security & Privacy

- Face data stored locally, not in cloud
- Database runs on localhost
- Video stream only accessible on local network
- No external data transmission

---

## 📝 Summary

This project creates a **complete end-to-end safety monitoring system** that:
1. ✅ Identifies workers automatically
2. ✅ Detects PPE compliance using AI
3. ✅ Records attendance automatically
4. ✅ Provides live video monitoring
5. ✅ Generates compliance reports
6. ✅ Offers modern web dashboard

**All working together seamlessly to improve workplace safety!** 🎉
