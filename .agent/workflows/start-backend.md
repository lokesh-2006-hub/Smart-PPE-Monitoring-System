---
description: how to start all backend services
---

# Starting the Complete Backend System

This workflow guides you through starting all backend services for the Smart PPE Compliance Monitoring System.

## Prerequisites

- MySQL server running
- Database migrations completed
- Python dependencies installed (`pip install -r backend/requirements.txt`)
- Frontend dependencies installed (`npm install` in `frontend/`)

## Full System Startup (3 Terminals)

### Terminal 1: Backend API

```bash
cd backend
python -m uvicorn api.backend_app:app --host 0.0.0.0 --port 8000 --reload
```

**Status**: Server should start on `http://0.0.0.0:8000`
**Check**: Open `http://localhost:8000/docs` to see API documentation

### Terminal 2: Frontend

```bash
cd frontend
npm run dev
```

**Status**: Development server should start on `http://localhost:5173`
**Check**: Open `http://localhost:5173` in your browser

### Terminal 3: Video Streaming Server

// turbo
```bash
cd backend/detection
python ppe_stream_server.py --source 0
```

**Options**:
- `--source 0` - Use webcam (default)
- `--source http://10.48.36.219:8080/video` - Use IP camera
- `--source video.mp4` - Use video file
- `--port 5000` - Flask server port (default: 5000)

**Status**: Flask server should start on `http://0.0.0.0:5000`
**Check**: Video feed should appear in the web dashboard

## Quick Test (No Video Streaming)

If you just want to test the backend API without video:

### Terminal 1: Backend API Only

```bash
cd backend
python -m uvicorn api.backend_app:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2: Test the API

```bash
cd backend/utils
python test_api.py
```

## Development Mode (Standalone Detection)

For testing detection locally without web UI:

### Backend API (Optional)

```bash
cd backend
python -m uvicorn api.backend_app:app --host 0.0.0.0 --port 8000 --reload
```

### Standalone Detection

// turbo
```bash
cd backend/detection
python ppe_attendance_combined.py --source 0
```

This shows the detection in an OpenCV window. Press 'q' to quit.

## Stopping the Services

1. Press `Ctrl+C` in each terminal window
2. Wait for graceful shutdown

## Troubleshooting

### Backend Won't Start
- **Check MySQL**: Is the database running?
- **Check migrations**: Have you run the migration scripts?
- **Check credentials**: Are database credentials correct in `backend/api/backend_app.py`?

### Frontend Won't Connect
- **Check backend**: Is it running on port 8000?
- **Check CORS**: Backend should allow `http://localhost:5173`

### Video Stream Not Working
- **Check camera**: Is camera connected and not in use?
- **Check Flask**: Is streaming server running on port 5000?
- **Check model**: Is `backend/models/my_model.pt` present?
- **Check faces**: Is `backend/data/known_faces/` populated?

## Next Steps

Once all services are running:
1. Open web dashboard at `http://localhost:5173`
2. Check that video feed is visible
3. Test face recognition with known faces
4. Verify PPE detection is working
5. Check that attendance data appears in dashboard
