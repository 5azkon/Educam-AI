# Alert_program.py
import cv2
import numpy as np
import threading
import time
import requests
from ultralytics import YOLO

# Telegram configuration
TELEGRAM_BOT_TOKEN = "7626974749:AAFSfBcUqanynya1CRLLFyvB8wqGHrHsdts"
TELEGRAM_CHAT_ID = "-4741709947"

# Global variables for reuse
model = None
video_source = None
human_labels = ["person"]
animal_labels = [
    "dog", "cat", "bird", "cow", "horse", "sheep",
    "elephant", "bear", "zebra", "giraffe", "monkey"
]
skip_frames = 3

def send_telegram_alert():
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': "🐾 Animal detected alert!!"
        }
        requests.post(url, params=params)
    except Exception as e:
        print(f"Failed to send Telegram notification: {e}")

def initialize_YOLO_model():
    global model, video_source
    print("🔄 Loading YOLO model...")
    model = YOLO(r"C:\Users\mr5az\OneDrive\Desktop\Final year project\IMAGE_DATA_FILE\yolov8n.pt")
    print("✅ YOLO model loaded successfully.")
    video_source = "rtsp://admin:Skk@2004@192.168.0.3:554/stream"

class VideoCaptureThread:
    def __init__(self, source):
        self.cap = cv2.VideoCapture(source)
        self.ret = False
        self.frame = None
        self.stopped = False
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.ret = ret
                    self.frame = frame
            time.sleep(0.01)

    def read(self):
        with self.lock:
            return self.ret, self.frame

    def stop(self):
        self.stopped = True
        self.thread.join()
        self.cap.release()

def alert_model_run_program():
    global model, video_source
    video_stream = VideoCaptureThread(video_source)

    frame_count = 0
    detected_frames = 0
    start_time = time.time()
    runtime = 30  # seconds
    animal_alert_sent = False

    while time.time() - start_time < runtime:
        ret, frame = video_stream.read()
        if not ret or frame is None:
            continue

        frame_count += 1
        if frame_count % skip_frames != 0:
            continue

        try:
            results = model(frame)[0]
            boxes = results.boxes
        except Exception as e:
            print(f"Detection error: {e}")
            continue

        detected_humans = []
        detected_animals = []
        animal_detected_in_frame = False

        for box in boxes:
            cls_id = int(box.cls)
            label = model.names.get(cls_id, "unknown")
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if label in human_labels:
                detected_humans.append((x1, y1, x2, y2))
                # Draw bounding box for humans
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            elif label in animal_labels:
                detected_animals.append((x1, y1, x2, y2, label))
                animal_detected_in_frame = True
                # Draw bounding box for animals
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, "animal", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        if animal_detected_in_frame:
            detected_frames += 1

        animal_percentage = (detected_frames / frame_count) * 100 if frame_count else 0

        if detected_animals:
            for (x1, y1, x2, y2, label) in detected_animals:
                is_inside_human = any(hx1 < x1 < hx2 and hy1 < y1 < hy2 for (hx1, hy1, hx2, hy2) in detected_humans)
                if not is_inside_human:
                    print(f"Animal: {label} - Confidence: {animal_percentage:.1f}%")

        # Display the frame with bounding boxes
        cv2.imshow("YOLO Detection", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if detected_frames > 0 and animal_percentage > 10 and not animal_alert_sent:
        send_telegram_alert()
        animal_alert_sent = True

    video_stream.stop()
    cv2.destroyAllWindows()

    if animal_percentage > 10:
        print(f"✔ Animal Detected with {animal_percentage:.1f}% confidence")
    else:
        print(f"✖ No Animal Detected (Only {animal_percentage:.1f}%)")

    return "Alert_program.py"

if __name__ == "__main__":
    print("🚀 Alert_program.py called directly")
    initialize_YOLO_model()
    alert_model_run_program()
