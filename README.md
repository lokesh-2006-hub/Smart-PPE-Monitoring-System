# 🛡️ Smart PPE Compliance Monitoring System

> **AI-Powered Safety Monitoring for Industrial Environments**

An end-to-end intelligent system that automatically detects workers, monitors PPE compliance, and maintains attendance records using computer vision and deep learning.

---

## 🎯 What Does This System Do?

This project creates a **complete safety monitoring solution** that:

- ✅ **Automatically identifies workers** using facial recognition
- ✅ **Detects PPE compliance** (helmet, vest, boots, gloves, goggles, headphones)
- ✅ **Streams live video** with real-time detection overlays
- ✅ **Records attendance** automatically when workers are detected
- ✅ **Provides web dashboard** for monitoring and reporting
- ✅ **Stores compliance data** in MySQL database
- ✅ **Generates daily reports** with statistics and violations

**Perfect for:** Construction sites, manufacturing plants, warehouses, chemical facilities, mining operations

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** | Complete explanation of features and capabilities |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System architecture with visual diagrams |
| **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** | Commands, troubleshooting, and common tasks |
| **README.md** (this file) | Quick start guide |

---

## 🏗️ System Components

### 1. Detection & Streaming Server (Port 5000)
- **File:** `ppe_stream_server.py`
- **Tech:** Flask + OpenCV + YOLO + face_recognition
- **Purpose:** Video capture, PPE detection, face recognition, MJPEG streaming

### 2. Backend API (Port 8000)
- **File:** `backend_app.py`
- **Tech:** FastAPI + MySQL
- **Purpose:** REST API, database management, reporting

### 3. Frontend Dashboard (Port 5173)
- **Directory:** `frontend/`
- **Tech:** React + Vite
- **Purpose:** Live video display, statistics, worker information

### 4. Database
- **Type:** MySQL
- **Database:** `ppe`
- **Tables:** `persons`, `attendance`

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **MySQL Server**
- **Webcam or IP Camera**

### Installation

1. **Clone/Download the project**

2. **Install Python dependencies:**
   ```bash
   cd d:\SIH1
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure MySQL:**
   - Ensure MySQL is running
   - Database `ppe` will be created automatically
   - Update credentials in `backend_app.py` if needed (default: root/Lokesh@sql)

5. **Prepare face recognition data:**
   - Create folders in `D:\sf\my_model\known_faces\{worker_name}`
   - Add 2-5 clear face photos per worker

### Running the System

**Terminal 1 - Backend API:**
```bash
cd d:\SIH1
python -m uvicorn backend_app:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd d:\SIH1\frontend
npm run dev
```

**Terminal 3 - Detection Server:**
```bash
cd d:\SIH1
# For IP camera
python ppe_stream_server.py --source http://10.48.36.219:8080/video

# For webcam
python ppe_stream_server.py --source 0
```

**Access the Dashboard:**
- Open browser: **http://localhost:5173**

---

## 🎮 Usage

### What You'll See

1. **Live Video Feed** - Real-time camera view with detection boxes
2. **Latest Scan Panel** - Current worker info and PPE status
3. **Statistics** - Daily entries, compliance rate, violations

### How It Works

1. Worker enters camera view
2. System detects and identifies face
3. Monitors PPE for 10 seconds
4. Determines Pass/Fail based on PPE presence
5. Records attendance and compliance in database
6. Updates dashboard in real-time

### Adding New Workers

1. Create folder: `D:\sf\my_model\known_faces\{worker_name}`
2. Add 2-5 clear face photos (.jpg, .jpeg, .png)
3. Restart detection server

---

## 📊 API Endpoints

### Backend API (http://localhost:8000)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/update_attendance` | POST | Record detection with PPE status |
| `/attendance/latest` | GET | Get most recent detection |
| `/attendance/{name}` | GET | Get worker's history |
| `/persons` | GET | List all registered workers |
| `/reports/daily` | GET | Get daily statistics |
| `/docs` | GET | Interactive API documentation |

### Streaming Server (http://localhost:5000)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/video_feed` | GET | MJPEG video stream |
| `/status` | GET | Server status |

---

## 🔧 Configuration

### Detection Parameters

Edit `ppe_stream_server.py`:

```python
TIME_WINDOW = 10.0          # Monitoring duration (seconds)
PERSON_TIMEOUT = 2.0        # Reset timeout (seconds)
PPE_CONFIRM_RATIO = 0.6     # Required consistency (60%)
CONF_THRESH = 0.5           # YOLO confidence threshold
```

### Model Paths

```python
--model "D:\sf\my_model\my_model.pt"           # YOLO model
--known-faces "D:\sf\my_model\known_faces"     # Face dataset
```

---

## 📁 Project Structure

```
d:\SIH1\
├── backend_app.py                    # FastAPI backend
├── ppe_stream_server.py              # Detection + streaming server
├── ppe_attendance_combined_optionB_fullframe.py  # Standalone version
├── requirements.txt                  # Python dependencies
├── PROJECT_OVERVIEW.md               # Detailed documentation
├── ARCHITECTURE.md                   # System diagrams
├── QUICK_REFERENCE.md                # Command reference
├── README.md                         # This file
│
├── frontend\                         # React dashboard
│   ├── src\
│   │   ├── pages\Dashboard.jsx
│   │   └── api\client.js
│   └── package.json
│
└── D:\sf\my_model\                   # AI models & data
    ├── my_model.pt                   # YOLO PPE model
    └── known_faces\                  # Face recognition data
        ├── worker1\
        ├── worker2\
        └── ...
```

---

## 🐛 Troubleshooting

### Video feed not showing?
```bash
# Check streaming server status
curl http://localhost:5000/status

# Should return: {"running": true, "has_frame": true}
```

### Database connection error?
- Verify MySQL is running
- Check credentials in `backend_app.py`
- Ensure database `ppe` exists (created automatically on first run)

### Face recognition not working?
```bash
# Install face_recognition
pip install face_recognition

# Or use LBPH fallback
pip install opencv-contrib-python
```

### More help?
See **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** for detailed troubleshooting

---

## 🎯 Current Status

Based on your latest run, the system is:
- ✅ **Detection Server:** Running on port 5000
- ✅ **Backend API:** Running on port 8000
- ✅ **Frontend:** Running on port 5173
- ✅ **Video Streaming:** Active (GET /video_feed requests successful)
- ✅ **Face Recognition:** Working (detecting "deepak")
- ✅ **PPE Detection:** Working (YOLO model loaded)
- ✅ **Database:** Connected (records 41-48 created)
- ⚠️ **Compliance:** Currently failing (worker needs proper PPE!)

---

## 📈 Features

### Detection Features
- Multi-person face detection and recognition
- Real-time PPE detection (6 item types)
- Continuous monitoring with temporal consistency
- Body box estimation for accurate PPE association
- Automatic attendance marking

### Dashboard Features
- Live MJPEG video stream
- Real-time statistics (entries, compliance rate, violations)
- Latest scan details with PPE checklist
- Auto-refresh every 2 seconds
- Responsive modern UI

### Backend Features
- RESTful API with FastAPI
- MySQL database with automatic schema creation
- Daily compliance reports
- Person management
- Attendance history tracking

---

## 🔐 Security Notes

- Face data stored locally (not in cloud)
- Database on localhost
- Video stream on local network only
- No external data transmission

**For production:** Enable HTTPS, add authentication, use environment variables

---

## 📞 Support

For detailed information:
- **Features & Capabilities:** [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
- **Architecture & Flow:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Commands & Troubleshooting:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## 🎓 Technology Stack

| Component | Technology |
|-----------|------------|
| Detection | OpenCV, YOLO (Ultralytics), face_recognition |
| Backend | FastAPI, MySQL, mysql-connector-python |
| Frontend | React, Vite, Lucide Icons |
| Streaming | Flask, MJPEG |
| Database | MySQL 8.0+ |

---

## 📝 License

This project is for educational/industrial safety purposes.

---

## 🎉 Quick Test

After starting all services:

1. Open http://localhost:5173
2. You should see live video feed
3. Stand in front of camera
4. System will detect and identify you
5. Check PPE status in dashboard
6. View records in database

**That's it! Your Smart PPE Compliance System is ready!** 🚀

---

**Made with ❤️ for workplace safety**
