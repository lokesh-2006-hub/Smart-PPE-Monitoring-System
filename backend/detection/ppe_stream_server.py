"""
Flask server to stream PPE detection video feed to web UI
Integrates with the PPE detection system
"""
from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import threading
import time
from datetime import datetime
import os
import sys
from ultralytics import YOLO
import requests

# Import AttendanceSystem from the main script
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    face_recognition = None
    FACE_RECOGNITION_AVAILABLE = False

# Default API URL
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# --- AttendanceSystem class (copied from main script) ---
class AttendanceSystem:
    def __init__(self, known_faces_dir, attendance_file_name=None, use_lbph_fallback=False):
        self.known_faces_dir = known_faces_dir
        self.attendance_file = attendance_file_name or datetime.now().strftime("%Y-%m-%d_Attendance.csv")
        self.marked_attendance = set()
        self.skip_recognition = not FACE_RECOGNITION_AVAILABLE or use_lbph_fallback

        self.known_face_encodings = []
        self.known_face_names = []

        self.lbph_recognizer = None
        self.inv_label_map = {}
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        self._initialize_recognizer()

    def _initialize_recognizer(self):
        if not self.skip_recognition:
            print("Initializing with face_recognition (dlib)...")
            self._load_known_faces_dlib()
        else:
            print("Initializing with OpenCV LBPH recognizer...")
            self._prepare_lbph_fallback()

    def _load_known_faces_dlib(self):
        if not os.path.exists(self.known_faces_dir):
            print(f"Warning: Known faces directory '{self.known_faces_dir}' not found.")
            return

        for person_name in os.listdir(self.known_faces_dir):
            person_folder = os.path.join(self.known_faces_dir, person_name)
            if not os.path.isdir(person_folder):
                continue
            for img_file in os.listdir(person_folder):
                if img_file.lower().endswith((".jpg", ".jpeg", ".png")):
                    image_path = os.path.join(person_folder, img_file)
                    try:
                        image = face_recognition.load_image_file(image_path)
                        encs = face_recognition.face_encodings(image)
                        if encs:
                            self.known_face_encodings.append(encs[0])
                            self.known_face_names.append(person_name)
                    except Exception as e:
                        print(f"Error processing {image_path}: {e}")
        if not self.known_face_names:
            print("Warning: No faces loaded for dlib recognizer.")
        else:
            print(f"Successfully loaded {len(self.known_face_names)} faces for dlib.")

    def _prepare_lbph_fallback(self):
        if not hasattr(cv2, "face") or not hasattr(cv2.face, "LBPHFaceRecognizer_create"):
            print("Error: OpenCV-contrib is required for LBPH.")
            self.lbph_recognizer = None
            return

        self.lbph_recognizer = cv2.face.LBPHFaceRecognizer_create()
        label_map = {}
        training_images = []
        training_labels = []

        if not os.path.exists(self.known_faces_dir):
            print(f"Warning: Known faces directory '{self.known_faces_dir}' not found.")
            return

        for entry in os.listdir(self.known_faces_dir):
            path = os.path.join(self.known_faces_dir, entry)
            if os.path.isdir(path):
                person_name = entry
                for img_file in os.listdir(path):
                    if img_file.lower().endswith((".jpg",".jpeg",".png")):
                        image_path = os.path.join(path, img_file)
                        self._process_lbph_image(image_path, person_name, training_images, training_labels, label_map)

        if training_images:
            self.lbph_recognizer.train(training_images, np.array(training_labels))
            self.inv_label_map = {v: k for k, v in label_map.items()}
            print(f"LBPH trained with {len(training_images)} images for {len(label_map)} people.")
        else:
            print("Warning: No training data for LBPH recognizer.")
            self.lbph_recognizer = None

    def _process_lbph_image(self, image_path, person_name, training_images, training_labels, label_map):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None: return
        faces = self.face_cascade.detectMultiScale(img, scaleFactor=1.05, minNeighbors=3)
        if len(faces) > 0:
            x, y, w, h = faces[0]
            face_roi = cv2.resize(img[y:y+h, x:x+w], (200, 200))
        else:
            face_roi = cv2.resize(img, (200, 200))
        
        if person_name not in label_map:
            label_map[person_name] = len(label_map)
        training_images.append(face_roi)
        training_labels.append(label_map[person_name])

    def mark_attendance(self, name):
        if name in self.marked_attendance:
            return
        self.marked_attendance.add(name)
        print(f"Attendance Marked: {name}")

    def _process_frame_dlib(self, small_frame, distance_threshold=0.60):
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            if True in matches:
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index] and face_distances[best_match_index] < distance_threshold:
                    name = self.known_face_names[best_match_index]
            face_names.append(name)
        return face_locations, face_names

    def _process_frame_lbph(self, small_frame, recent_predictions, confirmation_frames=3):
        gray_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray_small, scaleFactor=1.08, minNeighbors=4, minSize=(30, 30))
        face_locations, face_names = [], []
        for (x, y, w, h) in faces:
            face_locations.append((y, x + w, y + h, x))
            name = "Unknown"
            if self.lbph_recognizer:
                face_roi = cv2.resize(gray_small[y:y+h, x:x+w], (200, 200))
                label, confidence = self.lbph_recognizer.predict(face_roi)
                if confidence < 90 and label in self.inv_label_map:
                    name = self.inv_label_map[label]
            face_names.append(name)
        return face_locations, face_names

# --- Helper functions ---
def send_to_api(name, status, ppe_data, source=None):
    url = f"{API_URL}/update_attendance"
    data = {
        "name": name,
        "time": int(time.time()),
        "status": status,
        "source": source,
        **ppe_data
    }
    try:
        r = requests.post(url, json=data, timeout=5)
        r.raise_for_status()
        print("API response:", r.json())
    except Exception as e:
        print("Failed to send to API:", e)

def get_body_box(face_box, frame_w, frame_h):
    fx1, fy1, fx2, fy2 = face_box
    fw = fx2 - fx1
    fh = fy2 - fy1
    
    bx1 = max(0, fx1 - fw)
    bx2 = min(frame_w, fx2 + fw)
    by1 = max(0, fy1 - int(fh * 0.5))
    by2 = frame_h
    
    return (bx1, by1, bx2, by2)

def box_overlap(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    if ax2 < bx1 or bx2 < ax1 or ay2 < by1 or by2 < ay1:
        return False
    return True

# --- Global state ---
class StreamState:
    def __init__(self):
        self.latest_frame = None
        self.lock = threading.Lock()
        self.running = False
        
stream_state = StreamState()

# --- Detection thread ---
def detection_loop(model_path, video_source, known_faces_dir):
    global stream_state
    
    # Load YOLO with GPU optimization
    try:
        model = YOLO(model_path, task='detect')
        labels = model.names
        
        # Check if GPU is available
        import torch
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model.to(device)
        print(f"YOLO model loaded on device: {device}")
    except Exception as e:
        print(f"Error loading YOLO model: {e}")
        return

    # Video Capture - support for camera, video, image, or folder
    is_image_mode = False
    image_list = []
    source_type = "camera"  # Default to camera
    
    if os.path.isfile(video_source) and video_source.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        # Single image
        is_image_mode = True
        image_list = [video_source]
        source_type = "image"
        print(f"Processing single image: {video_source}")
    elif os.path.isdir(video_source):
        # Folder of images
        is_image_mode = True
        source_type = "folder"
        for fname in os.listdir(video_source):
            if fname.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                image_list.append(os.path.join(video_source, fname))
        print(f"Processing {len(image_list)} images from folder")
    else:
        # Video or camera
        if video_source.isdigit():
            cap = cv2.VideoCapture(int(video_source))
            source_type = "camera"
        else:
            cap = cv2.VideoCapture(video_source)
            source_type = "video"

        if not cap.isOpened():
            print(f"Error: Cannot open source {video_source}")
            return

    # Initialize Attendance
    attendance = AttendanceSystem(known_faces_dir=known_faces_dir)

    # Tracking
    current_person = None
    last_seen_time = 0
    PERSON_TIMEOUT = 2.0
    TIME_WINDOW = 30.0  # Monitor each person for 30 seconds
    person_start_time = None
    person_ppe_history = []
    PPE_CONFIRM_RATIO = 0.6
    FACE_SCALE = 0.5
    CONF_THRESH = 0.5
    
    # Performance optimization settings
    YOLO_FRAME_SKIP = 5  # Run YOLO every 5 frames (faster)
    FACE_FRAME_SKIP = 3  # Run face detection every 3 frames (faster)
    YOLO_INPUT_WIDTH = 480  # Downscale for YOLO processing (faster)
    frame_counter = 0
    image_index = 0  # For image mode
    last_ppe_detections = []  # Cache last YOLO results
    last_face_results = ([], [])  # Cache last face detection results

    LABEL_TO_KEY = {
        "helmet": "helmet", "hard_hat": "helmet",
        "glove": "glows", "gloves": "glows", "glows": "glows",  # Added "glows" mapping
        "shoe": "sheao", "shoes": "sheao", "sheao": "sheao",  # Added "sheao" mapping
        "safety_jacket": "jacket", "vest": "jacket", "jacket": "jacket",  # Added "jacket" mapping
        "goggle": "glass", "glasses": "glass", "glass": "glass",  # Added "glass" mapping
        "headphone": "headphone", "headphones": "headphone", "head_phone": "headphone"  # Added "head_phone" mapping
    }

    print("Detection loop started with optimizations...")
    print(f"YOLO frame skip: {YOLO_FRAME_SKIP}, Face frame skip: {FACE_FRAME_SKIP}")
    stream_state.running = True

    while stream_state.running:
        frame_start_time = time.time()
        
        # Read frame from video/camera or load image
        if is_image_mode:
            if image_index >= len(image_list):
                print("All images processed.")
                time.sleep(1)
                image_index = 0  # Loop back
                continue
            frame = cv2.imread(image_list[image_index])
            if frame is None:
                print(f"Failed to load image: {image_list[image_index]}")
                image_index += 1
                continue
            ret = True
            # Hold each image for a bit to simulate video
            if frame_counter % 30 == 0:  # Change image every ~1 second
                image_index += 1
        else:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame, retrying...")
                time.sleep(0.1)
                continue

        display_frame = frame.copy()
        h, w = frame.shape[:2]
        frame_counter += 1

        # Face Detection (with frame skipping)
        if frame_counter % FACE_FRAME_SKIP == 0:
            small_for_face = cv2.resize(frame, (0,0), fx=FACE_SCALE, fy=FACE_SCALE)
            if not attendance.skip_recognition:
                face_locations, face_names = attendance._process_frame_dlib(small_for_face)
            else:
                face_locations, face_names = attendance._process_frame_lbph(small_for_face, {})
            last_face_results = (face_locations, face_names)
        else:
            # Reuse cached face detection results
            face_locations, face_names = last_face_results

        # Identify Primary Person
        chosen_name = None
        chosen_face_box_full = None
        
        for idx, name in enumerate(face_names):
            if name != "Unknown":
                chosen_name = name
                top, right, bottom, left = face_locations[idx]
                scale = 1.0 / FACE_SCALE
                chosen_face_box_full = (int(left*scale), int(top*scale), int(right*scale), int(bottom*scale))
                break
        
        now = time.time()

        if chosen_name:
            last_seen_time = now
            if current_person != chosen_name:
                print(f"New person: {chosen_name}")
                current_person = chosen_name
                person_start_time = now
                person_ppe_history = []
        else:
            if current_person and (now - last_seen_time) > PERSON_TIMEOUT:
                print("Person lost.")
                current_person = None
                person_start_time = None
                person_ppe_history = []

        # PPE Detection & Association (with frame skipping and downscaling)
        if current_person and chosen_face_box_full:
            body_box = get_body_box(chosen_face_box_full, w, h)
            bx1, by1, bx2, by2 = body_box
            
            cv2.rectangle(display_frame, (bx1, by1), (bx2, by2), (255, 255, 0), 1)

            # Run YOLO only every N frames
            if frame_counter % YOLO_FRAME_SKIP == 0:
                # Downscale frame for faster YOLO processing
                scale_factor = YOLO_INPUT_WIDTH / w
                yolo_frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)
                
                results = model(yolo_frame, verbose=False)
                detections = results[0].boxes
                
                # Debug: Print all detections
                print(f"\n=== YOLO Detections (Frame {frame_counter}) ===")
                
                # Scale detections back to original resolution
                last_ppe_detections = []
                for box in detections:
                    conf = float(box.conf.item())
                    cls_idx = int(box.cls.item())
                    raw_label = labels[cls_idx] if isinstance(labels, (list, dict)) else str(labels.get(cls_idx, cls_idx))
                    
                    # Debug output for all detections
                    print(f"  Detected: {raw_label} (confidence: {conf:.2f})")
                    
                    if conf < CONF_THRESH: 
                        print(f"    ❌ Skipped (confidence {conf:.2f} < {CONF_THRESH})")
                        continue
                    
                    label_norm = raw_label.strip().lower().replace(" ", "_")
                    mapped = LABEL_TO_KEY.get(label_norm)
                    
                    if not mapped:
                        print(f"    ⚠️  No mapping found for '{label_norm}'")
                        continue
                    
                    print(f"    ✓ Mapped to: {mapped}")
                    
                    xyxy = box.xyxy.cpu().numpy().squeeze().astype(int)
                    # Scale back to original resolution
                    xyxy_scaled = (xyxy / scale_factor).astype(int)
                    last_ppe_detections.append((xyxy_scaled, raw_label, mapped))
            
            # Process cached detections
            ppe_status = {k: False for k in set(LABEL_TO_KEY.values())}
            for xyxy, raw_label, mapped in last_ppe_detections:
                ppe_box = tuple(xyxy)
                if box_overlap(ppe_box, body_box):
                    ppe_status[mapped] = True
                    cv2.rectangle(display_frame, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), (0, 255, 0), 2)
                    cv2.putText(display_frame, raw_label, (xyxy[0], xyxy[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

            person_ppe_history.append(ppe_status)
            
            elapsed = now - person_start_time
            cv2.putText(display_frame, f"Monitoring {current_person}: {int(elapsed)}s", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            if elapsed >= TIME_WINDOW:
                counts = {k: 0 for k in ppe_status.keys()}
                for snap in person_ppe_history:
                    for k, v in snap.items():
                        if v: counts[k] += 1
                
                total = len(person_ppe_history)
                final_present = {k: (c/total >= PPE_CONFIRM_RATIO) for k, c in counts.items()}
                final_status = "pass" if all(final_present.values()) else "fail"
                
                print(f"\n=== Final Result for {current_person} ===")
                print(f"Status: {final_status}")
                print(f"PPE Items detected:")
                for item, present in final_present.items():
                    status_icon = "✓" if present else "✗"
                    print(f"  {status_icon} {item}: {present}")
                
                print(f"Result for {current_person}: {final_status}")
                send_to_api(current_person, final_status, final_present, source=source_type)
                attendance.mark_attendance(current_person)
                
                current_person = None
                person_start_time = None
                person_ppe_history = []

        # Update stream
        with stream_state.lock:
            stream_state.latest_frame = display_frame.copy()

        # Dynamic FPS control - maintain ~30 FPS
        frame_time = time.time() - frame_start_time
        target_frame_time = 1.0 / 30.0  # 30 FPS
        sleep_time = max(0.001, target_frame_time - frame_time)
        time.sleep(sleep_time)

    if not is_image_mode:
        cap.release()
    print("Detection loop stopped.")

# --- Flask app ---
app = Flask(__name__)
CORS(app)

def generate_frames():
    """Generator function for MJPEG stream"""
    while True:
        with stream_state.lock:
            if stream_state.latest_frame is None:
                time.sleep(0.1)
                continue
            frame = stream_state.latest_frame.copy()
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    """Status endpoint"""
    return jsonify({
        'running': stream_state.running,
        'has_frame': stream_state.latest_frame is not None
    })

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    # Use relative paths from backend directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_root = os.path.dirname(script_dir)  # Go up to backend/
    
    parser.add_argument('--model', default=os.path.join(backend_root, 'models', 'my_model.pt'), required=False)
    parser.add_argument('--source', default='0', help='video file or camera index (0)')
    parser.add_argument('--known-faces', default=os.path.join(backend_root, 'data', 'known_faces'), help='Known faces directory')
    parser.add_argument('--port', default=5000, type=int, help='Flask server port')
    parser.add_argument('--api-url', default=None, help='Backend API URL')
    args = parser.parse_args()

    if args.api_url:
        API_URL = args.api_url

    # Automated Sync from Cloud to Pi
    try:
        from sync_workers import sync_workers
        print("Checking for new worker photos...")
        sync_workers(API_URL, args.known_faces)
    except ImportError:
        print("Warning: sync_workers.py not found. Skipping auto-sync.")
    except Exception as e:
        print(f"Warning: Auto-sync failed: {e}")

    # Start detection thread
    detection_thread = threading.Thread(
        target=detection_loop,
        args=(args.model, args.source, args.known_faces),
        daemon=True
    )
    detection_thread.start()

    # Start Flask server
    print(f"Starting Flask server on port {args.port}...")
    app.run(host='0.0.0.0', port=args.port, threaded=True, debug=False)
