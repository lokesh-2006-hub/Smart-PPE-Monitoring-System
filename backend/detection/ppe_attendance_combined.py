"""
Combined PPE + Attendance script with full-frame PPE detection
- Option B: require continuous presence for TIME_WINDOW seconds (default 60s).
- PPE detection runs on the full frame, but PPE is accepted only when it overlaps
  the tracked person's bounding box (derived from face detection).
- If the person disappears for > PERSON_TIMEOUT seconds, the monitoring resets.
- After successful continuous monitoring, one final result is sent to API and attendance is marked.

Requires:
- ultralytics YOLO model installed and a trained model path
- face_recognition (optional) or OpenCV-contrib for LBPH fallback
- OpenCV, numpy, requests
"""
import os
import sys
import argparse
import time
import cv2
import numpy as np
import csv
from datetime import datetime
from ultralytics import YOLO
import requests

# --- AttendanceSystem class ---
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    face_recognition = None
    FACE_RECOGNITION_AVAILABLE = False

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
        # (optional) create attendance file if not exists
        if not os.path.exists(self.attendance_file) or os.stat(self.attendance_file).st_size == 0:
            with open(self.attendance_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Time", "Status"])

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
            print("Error: OpenCV-contrib is required for LBPH. Install with 'pip install opencv-contrib-python'")
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
            elif entry.lower().endswith((".jpg",".jpeg",".png")):
                person_name = os.path.splitext(entry)[0]
                self._process_lbph_image(path, person_name, training_images, training_labels, label_map)

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
        # We don't strictly need local CSV if we send to API, but good for backup
        if name in self.marked_attendance:
            return
        current_time = datetime.now().strftime("%H:%M:%S")
        with open(self.attendance_file, "a+", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([name, current_time, "Present"])
        self.marked_attendance.add(name)
        print(f"Attendance Marked locally: {name} at {current_time}")

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
            face_locations.append((y, x + w, y + h, x)) # top, right, bottom, left
            name = "Unknown"
            if self.lbph_recognizer:
                face_roi = cv2.resize(gray_small[y:y+h, x:x+w], (200, 200))
                label, confidence = self.lbph_recognizer.predict(face_roi)
                if confidence < 90 and label in self.inv_label_map:
                    name = self.inv_label_map[label]
            face_names.append(name)
        return face_locations, face_names

# -------------------------
# Helper: send_to_api
# -------------------------
def send_to_api(name, status, ppe_data):
    # UPDATED: Point to the correct endpoint
    url = "http://127.0.0.1:8000/update_attendance"
    data = {
        "name": name,
        "time": int(time.time()),
        "status": status,
        **ppe_data
    }
    try:
        r = requests.post(url, json=data, timeout=5)
        r.raise_for_status()
        print("API response:", r.json())
    except Exception as e:
        print("Failed to send to API:", e)

# -------------------------
# Helper: Body Box Estimation
# -------------------------
def get_body_box(face_box, frame_w, frame_h):
    """
    Estimate body bounding box based on face box.
    face_box: (x1, y1, x2, y2)
    Returns: (bx1, by1, bx2, by2)
    """
    fx1, fy1, fx2, fy2 = face_box
    fw = fx2 - fx1
    fh = fy2 - fy1
    
    # Estimate body:
    # Wider than face (e.g., 3x face width)
    # Extends from top of head (or slightly above) to bottom of frame
    
    bx1 = max(0, fx1 - fw)
    bx2 = min(frame_w, fx2 + fw)
    by1 = max(0, fy1 - int(fh * 0.5)) # Include some space above head for helmet
    by2 = frame_h # Assume body goes to bottom of frame
    
    return (bx1, by1, bx2, by2)

def box_overlap(a, b):
    """Return True if rectangles a and b overlap."""
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    if ax2 < bx1 or bx2 < ax1 or ay2 < by1 or by2 < ay1:
        return False
    return True

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Use relative paths from backend directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_root = os.path.dirname(script_dir)  # Go up to backend/
    
    parser.add_argument('--model', default=os.path.join(backend_root, 'models', 'my_model.pt'), required=False)
    parser.add_argument('--source', default='0', help='video file or camera index (0)')
    parser.add_argument('--thresh', default=0.5, type=float, help='confidence threshold')
    parser.add_argument('--scale', default=0.5, type=float, help='face recognition resize factor')
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()

    model_path = args.model
    img_source = args.source
    CONF_THRESH = float(args.thresh)
    FACE_SCALE = float(args.scale)
    record = args.record

    # Load YOLO
    if not os.path.exists(model_path):
        print(f"WARNING: Model path {model_path} not found. YOLO will fail if not fixed.")
        # For demo purposes, we might continue or exit. 
        # sys.exit(0) 
    
    try:
        model = YOLO(model_path, task='detect')
        labels = model.names
    except Exception as e:
        print(f"Error loading YOLO model: {e}")
        sys.exit(1)

    # Video Capture
    if img_source.isdigit():
        cap = cv2.VideoCapture(int(img_source))
    else:
        cap = cv2.VideoCapture(img_source)

    if not cap.isOpened():
        print(f"Error: Cannot open source {img_source}")
        sys.exit(1)

    if record:
        recorder = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'MJPG'), 20, (640,480))

    bbox_colors = [(164,120,87), (68,148,228), (93,97,209), (178,182,133), (88,159,106)]

    # Initialize Attendance (using relative path from backend directory)
    KNOWN_FACES_DIR = os.path.join(backend_root, 'data', 'known_faces')
    attendance = AttendanceSystem(known_faces_dir=KNOWN_FACES_DIR)

    # Tracking
    current_person = None
    last_seen_time = 0
    PERSON_TIMEOUT = 2.0
    TIME_WINDOW = 10.0 # Reduced for testing, set to 60.0 for prod
    person_start_time = None
    person_ppe_history = []
    PPE_CONFIRM_RATIO = 0.6

    LABEL_TO_KEY = {
        "helmet": "helmet", "hard_hat": "helmet",
        "glove": "glows", "gloves": "glows",
        "shoe": "sheao", "shoes": "sheao",
        "safety_jacket": "jacket", "vest": "jacket",
        "headphone": "headphone"
    }

    print("Starting detection...")

    while True:
        ret, frame = cap.read()
        if not ret: break

        display_frame = frame.copy()
        h, w = frame.shape[:2]

        # 1. Face Detection
        small_for_face = cv2.resize(frame, (0,0), fx=FACE_SCALE, fy=FACE_SCALE)
        if not attendance.skip_recognition:
            face_locations, face_names = attendance._process_frame_dlib(small_for_face)
        else:
            face_locations, face_names = attendance._process_frame_lbph(small_for_face, {})

        # 2. Identify Primary Person
        chosen_name = None
        chosen_face_box_full = None
        
        for idx, name in enumerate(face_names):
            if name != "Unknown":
                chosen_name = name
                top, right, bottom, left = face_locations[idx]
                # Scale back up
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

        # 3. PPE Detection & Association
        if current_person and chosen_face_box_full:
            # Estimate body box
            body_box = get_body_box(chosen_face_box_full, w, h)
            bx1, by1, bx2, by2 = body_box
            
            # Draw body box for debug
            cv2.rectangle(display_frame, (bx1, by1), (bx2, by2), (255, 255, 0), 1)

            results = model(frame, verbose=False)
            detections = results[0].boxes
            
            ppe_status = {k: False for k in set(LABEL_TO_KEY.values())}

            for box in detections:
                conf = float(box.conf.item())
                if conf < CONF_THRESH: continue
                
                cls_idx = int(box.cls.item())
                raw_label = labels[cls_idx] if isinstance(labels, (list, dict)) else str(labels.get(cls_idx, cls_idx))
                label_norm = raw_label.strip().lower().replace(" ", "_")
                mapped = LABEL_TO_KEY.get(label_norm)
                
                if not mapped: continue

                xyxy = box.xyxy.cpu().numpy().squeeze().astype(int)
                ppe_box = tuple(xyxy)

                # Check overlap with BODY box, not just face
                if box_overlap(ppe_box, body_box):
                    ppe_status[mapped] = True
                    cv2.rectangle(display_frame, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), (0, 255, 0), 2)
                    cv2.putText(display_frame, raw_label, (xyxy[0], xyxy[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

            person_ppe_history.append(ppe_status)
            
            # Status logic
            elapsed = now - person_start_time
            cv2.putText(display_frame, f"Monitoring {current_person}: {int(elapsed)}s", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            if elapsed >= TIME_WINDOW:
                # Finalize
                counts = {k: 0 for k in ppe_status.keys()}
                for snap in person_ppe_history:
                    for k, v in snap.items():
                        if v: counts[k] += 1
                
                total = len(person_ppe_history)
                final_present = {k: (c/total >= PPE_CONFIRM_RATIO) for k, c in counts.items()}
                final_status = "pass" if all(final_present.values()) else "fail"
                
                print(f"Result for {current_person}: {final_status}")
                send_to_api(current_person, final_status, final_present)
                attendance.mark_attendance(current_person)
                
                # Reset
                current_person = None
                person_start_time = None
                person_ppe_history = []
        
        # Display frame
        cv2.imshow('PPE Detection', display_frame)
        
        # Record if enabled
        if record:
            recorder.write(cv2.resize(display_frame, (640, 480)))
        
        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cap.release()
    if record:
        recorder.release()
    cv2.destroyAllWindows()
    print("Detection stopped.")

