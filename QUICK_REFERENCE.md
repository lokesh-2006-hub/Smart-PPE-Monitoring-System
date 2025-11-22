# Quick Reference Guide

## 🚀 Starting the System

### Option 1: Full System (Recommended)

**Terminal 1 - Backend API:**
```bash
cd d:\SIH1
python -m uvicorn backend_app:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend Dashboard:**
```bash
cd d:\SIH1\frontend
npm run dev
```

**Terminal 3 - Detection & Streaming:**
```bash
cd d:\SIH1
# For IP camera
python ppe_stream_server.py --source http://10.48.36.219:8080/video

# For webcam
python ppe_stream_server.py --source 0
```

**Access Dashboard:**
- Open browser: http://localhost:5173

---

### Option 2: Standalone Detection (No Web UI)

```bash
cd d:\SIH1
# For IP camera
python ppe_attendance_combined_optionB_fullframe.py --source http://10.48.36.219:8080/video

# For webcam
python ppe_attendance_combined_optionB_fullframe.py --source 0

# Press 'q' to quit
```

---

## 🔧 Configuration

### Change Monitoring Duration
Edit `ppe_stream_server.py` line 286:
```python
TIME_WINDOW = 10.0  # Change to 60.0 for production
```

### Change PPE Confirmation Threshold
Edit `ppe_stream_server.py` line 289:
```python
PPE_CONFIRM_RATIO = 0.6  # 60% - increase for stricter checking
```

### Change Model Path
```bash
python ppe_stream_server.py --model "path/to/your/model.pt" --source 0
```

### Change Known Faces Directory
```bash
python ppe_stream_server.py --known-faces "path/to/faces" --source 0
```

---

## 👤 Adding New Workers

1. **Create folder for worker:**
   ```bash
   mkdir "D:\sf\my_model\known_faces\worker_name"
   ```

2. **Add 2-5 clear face photos:**
   - Front-facing photos
   - Good lighting
   - Different angles
   - Formats: .jpg, .jpeg, .png

3. **Restart detection server**

---

## 📊 API Testing

### Get Latest Detection
```bash
curl http://localhost:8000/attendance/latest
```

### Get Daily Report
```bash
curl http://localhost:8000/reports/daily
```

### Get Person History
```bash
curl http://localhost:8000/attendance/deepak
```

### Manual Attendance Update
```bash
curl -X POST http://localhost:8000/update_attendance \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_user",
    "status": "pass",
    "helmet": true,
    "glows": true,
    "sheao": true,
    "jacket": true,
    "glass": true
  }'
```

---

## 🐛 Troubleshooting

### Video Feed Not Showing

**Check if streaming server is running:**
```bash
curl http://localhost:5000/status
```

**Expected response:**
```json
{"running": true, "has_frame": true}
```

**If not running, start it:**
```bash
python ppe_stream_server.py --source http://10.48.36.219:8080/video
```

---

### Database Connection Error

**Check MySQL is running:**
```bash
# Windows
net start MySQL

# Or check services
services.msc
```

**Test database connection:**
```bash
mysql -u root -p
# Enter password: Lokesh@sql
USE ppe;
SHOW TABLES;
```

---

### Face Recognition Not Working

**Install face_recognition:**
```bash
pip install face_recognition
```

**If fails, use LBPH fallback:**
```bash
pip install opencv-contrib-python
```

---

### YOLO Model Not Found

**Check model path exists:**
```bash
dir "D:\sf\my_model\my_model.pt"
```

**If missing, specify correct path:**
```bash
python ppe_stream_server.py --model "correct/path/to/model.pt" --source 0
```

---

### Frontend Not Connecting to Backend

**Check CORS settings in `backend_app.py`:**
```python
allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"]
```

**Check API client in `frontend/src/api/client.js`:**
```javascript
baseURL: 'http://localhost:8000'
```

---

## 📝 Common Tasks

### View Database Records

```sql
-- Connect to MySQL
mysql -u root -p

-- Use database
USE ppe;

-- View all persons
SELECT * FROM persons;

-- View today's attendance
SELECT * FROM attendance 
WHERE DATE(detected_at) = CURDATE() 
ORDER BY detected_at DESC;

-- View compliance stats
SELECT 
    overall_status, 
    COUNT(*) as count 
FROM attendance 
WHERE DATE(detected_at) = CURDATE() 
GROUP BY overall_status;

-- View person's history
SELECT * FROM attendance 
WHERE person_name = 'deepak' 
ORDER BY detected_at DESC 
LIMIT 10;
```

---

### Clear Old Records

```sql
-- Delete old attendance records (older than 30 days)
DELETE FROM attendance 
WHERE detected_at < DATE_SUB(NOW(), INTERVAL 30 DAY);

-- Reset all attendance for today
DELETE FROM attendance 
WHERE DATE(detected_at) = CURDATE();
```

---

### Export Data

```bash
# Export today's attendance to CSV
mysql -u root -p -e "
SELECT 
    person_name, 
    detected_at, 
    overall_status, 
    ppe_status 
FROM ppe.attendance 
WHERE DATE(detected_at) = CURDATE()
" > attendance_export.csv
```

---

## 🎯 Performance Optimization

### Reduce CPU Usage

**Lower frame rate in `ppe_stream_server.py`:**
```python
time.sleep(0.03)  # Change to 0.1 for ~10 FPS
```

**Reduce face detection scale:**
```python
FACE_SCALE = 0.5  # Change to 0.25 for faster processing
```

---

### Improve Accuracy

**Increase monitoring window:**
```python
TIME_WINDOW = 60.0  # More samples = better accuracy
```

**Increase confirmation ratio:**
```python
PPE_CONFIRM_RATIO = 0.8  # Require 80% consistency
```

**Lower YOLO confidence threshold:**
```python
CONF_THRESH = 0.3  # Detect more items (may have false positives)
```

---

## 📱 Access from Other Devices

### Make servers accessible on network:

**Already configured for:**
- Backend: `0.0.0.0:8000` ✅
- Streaming: `0.0.0.0:5000` ✅

**Find your IP address:**
```bash
ipconfig
# Look for IPv4 Address
```

**Access from other devices:**
- Dashboard: `http://YOUR_IP:5173`
- Video Feed: `http://YOUR_IP:5000/video_feed`
- API: `http://YOUR_IP:8000/docs`

**Update frontend to use network IP:**
Edit `frontend/src/pages/Dashboard.jsx` line 62:
```javascript
src="http://YOUR_IP:5000/video_feed"
```

---

## 🔐 Security Notes

### For Production Deployment:

1. **Change database password**
2. **Enable HTTPS**
3. **Add authentication to API**
4. **Restrict CORS origins**
5. **Use environment variables for secrets**
6. **Deploy with Gunicorn/Nginx instead of development servers**

---

## 📞 Quick Commands Cheat Sheet

```bash
# Start everything
cd d:\SIH1
python -m uvicorn backend_app:app --host 0.0.0.0 --port 8000 --reload &
cd frontend && npm run dev &
python ppe_stream_server.py --source http://10.48.36.219:8080/video

# Stop everything
# Press Ctrl+C in each terminal

# Check what's running
netstat -ano | findstr "5000 8000 5173"

# View logs
# Check terminal outputs

# Restart detection only
# Ctrl+C in detection terminal
python ppe_stream_server.py --source http://10.48.36.219:8080/video

# Test API
curl http://localhost:8000/attendance/latest
curl http://localhost:8000/reports/daily
curl http://localhost:5000/status

# View database
mysql -u root -p
USE ppe;
SELECT * FROM attendance ORDER BY detected_at DESC LIMIT 10;
```

---

## 🎓 Understanding the Output

### Detection Server Output:
```
Initializing with face_recognition (dlib)...
Successfully loaded 14 faces for dlib.
Detection loop started...
New person: deepak                    # Worker detected
Result for deepak: fail               # PPE check failed
API response: {'status': 'ok', 'record_id': 41}  # Saved to DB
Attendance Marked: deepak             # Attendance recorded
127.0.0.1 - - [20/Nov/2025 12:00:00] "GET /video_feed HTTP/1.1" 200  # Video stream accessed
```

### What "fail" means:
- Worker detected but not wearing all required PPE
- Check which items are missing in database or dashboard

### What "pass" means:
- Worker detected with all required PPE items
- PPE present in ≥60% of monitored frames

---

## 💡 Tips

1. **Better lighting = better detection**
2. **Clear camera view = better tracking**
3. **Multiple face photos = better recognition**
4. **Longer monitoring window = more accurate results**
5. **Keep camera stable and at good angle**
6. **Ensure PPE items are visible to camera**
7. **Test with different workers before deployment**

---

## 📚 Additional Resources

- **YOLO Documentation:** https://docs.ultralytics.com/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **React Docs:** https://react.dev/
- **face_recognition:** https://github.com/ageitgey/face_recognition

---

**Need help? Check the logs in each terminal for error messages!**
