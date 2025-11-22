# System Architecture Diagram

## Complete System Flow

```mermaid
graph TB
    subgraph "Input Layer"
        CAM[IP Camera/Webcam<br/>10.48.36.219:8080]
    end
    
    subgraph "Detection Server - Port 5000"
        FLASK[Flask Server<br/>ppe_stream_server.py]
        FACE[Face Recognition<br/>dlib/LBPH]
        YOLO[YOLO PPE Detection<br/>my_model.pt]
        TRACK[Person Tracking<br/>10s monitoring]
        STREAM[MJPEG Streamer<br/>/video_feed]
    end
    
    subgraph "Backend API - Port 8000"
        API[FastAPI Server<br/>backend_app.py]
        DB[(MySQL Database<br/>ppe)]
    end
    
    subgraph "Frontend - Port 5173"
        REACT[React Dashboard<br/>Vite + React]
        VIDEO[Live Video Feed]
        STATS[Statistics Panel]
        LATEST[Latest Scan Panel]
    end
    
    CAM -->|Video Stream| FLASK
    FLASK --> FACE
    FLASK --> YOLO
    FACE --> TRACK
    YOLO --> TRACK
    TRACK -->|Annotated Frames| STREAM
    TRACK -->|POST /update_attendance| API
    API -->|Store Records| DB
    STREAM -->|MJPEG Stream| VIDEO
    REACT -->|GET /attendance/latest| API
    REACT -->|GET /reports/daily| API
    API -->|JSON Response| STATS
    API -->|JSON Response| LATEST
    
    style CAM fill:#e1f5ff
    style FLASK fill:#fff3cd
    style API fill:#d4edda
    style REACT fill:#f8d7da
    style DB fill:#d1ecf1
```

## Data Flow Sequence

```mermaid
sequenceDiagram
    participant Camera
    participant Detection as Detection Server<br/>(Port 5000)
    participant API as Backend API<br/>(Port 8000)
    participant DB as MySQL Database
    participant UI as Web Dashboard<br/>(Port 5173)
    
    Camera->>Detection: Video Stream
    Detection->>Detection: Detect Face
    Detection->>Detection: Identify Person (deepak)
    Detection->>Detection: Detect PPE (YOLO)
    Detection->>Detection: Monitor for 10s
    Detection->>Detection: Calculate Pass/Fail
    Detection->>API: POST /update_attendance<br/>{name, status, ppe_data}
    API->>DB: INSERT attendance record
    DB-->>API: record_id: 41
    API-->>Detection: {status: ok, record_id: 41}
    
    loop Every 2 seconds
        UI->>API: GET /attendance/latest
        API->>DB: SELECT latest record
        DB-->>API: Latest attendance data
        API-->>UI: {person_name, status, ppe_status}
        UI->>UI: Update dashboard
    end
    
    UI->>Detection: GET /video_feed
    Detection-->>UI: MJPEG Stream
    UI->>UI: Display live video
```

## Component Interaction Map

```mermaid
graph LR
    subgraph "Detection & Recognition"
        A[Video Frame] --> B[Face Detection]
        B --> C{Known Person?}
        C -->|Yes| D[Track Person]
        C -->|No| E[Show as Unknown]
        D --> F[Estimate Body Box]
        F --> G[Run YOLO on Frame]
        G --> H[Check PPE Overlap]
        H --> I[Record PPE Status]
        I --> J{10s Elapsed?}
        J -->|No| D
        J -->|Yes| K[Calculate Final Status]
        K --> L{60% PPE Present?}
        L -->|Yes| M[PASS]
        L -->|No| N[FAIL]
        M --> O[Send to API]
        N --> O
    end
    
    style M fill:#90EE90
    style N fill:#FFB6C6
```

## Database Schema

```mermaid
erDiagram
    PERSONS ||--o{ ATTENDANCE : has
    PERSONS {
        int id PK
        string name UK
        string employee_id
        text meta
        datetime created_at
    }
    ATTENDANCE {
        int id PK
        int person_id FK
        string person_name
        datetime detected_at
        text ppe_status
        string overall_status
        text raw_payload
    }
```

## PPE Detection Logic

```mermaid
flowchart TD
    START[New Frame] --> FACE_DET[Detect Face]
    FACE_DET --> KNOWN{Known Person?}
    KNOWN -->|No| SKIP[Skip PPE Check]
    KNOWN -->|Yes| BODY[Estimate Body Box]
    BODY --> YOLO[Run YOLO Detection]
    YOLO --> ITEMS[Get All PPE Items]
    ITEMS --> CHECK[Check Each Item]
    CHECK --> OVERLAP{Overlaps Body?}
    OVERLAP -->|Yes| MARK_YES[Mark PPE as Present]
    OVERLAP -->|No| MARK_NO[Ignore Item]
    MARK_YES --> HISTORY[Add to History]
    MARK_NO --> HISTORY
    HISTORY --> TIME{10s Passed?}
    TIME -->|No| CONTINUE[Continue Monitoring]
    TIME -->|Yes| CALC[Calculate Percentages]
    CALC --> RATIO{Each PPE >= 60%?}
    RATIO -->|All Yes| PASS[Status: PASS]
    RATIO -->|Any No| FAIL[Status: FAIL]
    PASS --> API[Send to API]
    FAIL --> API
    API --> RESET[Reset Tracking]
    CONTINUE --> START
    SKIP --> START
    RESET --> START
    
    style PASS fill:#90EE90
    style FAIL fill:#FFB6C6
```

## System Ports & Services

| Service | Port | Technology | Purpose |
|---------|------|------------|---------|
| Detection Server | 5000 | Flask | Video streaming & PPE detection |
| Backend API | 8000 | FastAPI | Data management & REST API |
| Frontend | 5173 | Vite/React | Web dashboard UI |
| Database | 3306 | MySQL | Data persistence |

## File Structure

```
d:\SIH1\
├── backend_app.py              # FastAPI backend server
├── ppe_stream_server.py        # Flask streaming + detection
├── ppe_attendance_combined_optionB_fullframe.py  # Standalone detection
├── requirements.txt            # Python dependencies
├── PROJECT_OVERVIEW.md         # This documentation
├── README.md                   # Project readme
│
├── frontend\                   # React frontend
│   ├── src\
│   │   ├── pages\
│   │   │   └── Dashboard.jsx   # Main dashboard component
│   │   └── api\
│   │       └── client.js       # API client
│   └── package.json
│
└── D:\sf\my_model\            # Model & training data
    ├── my_model.pt            # YOLO PPE detection model
    └── known_faces\           # Face recognition dataset
        ├── deepak\
        ├── augustin\
        └── ...
```
