import cv2
import mediapipe as mp
import numpy as np
import threading
import time
import requests
import subprocess

# Initialize MediaPipe Hands inside the function
def initialize_mediapipe():
    global hands, mp_hands, mp_draw
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "7626974749:AAFSfBcUqanynya1CRLLFyvB8wqGHrHsdts"
TELEGRAM_CHAT_ID = "-4741709947"  # "1654914770"

# RTSP URL (Handle special characters in passwords properly)
rtsp_url = "rtsp://admin:Skk%402004@192.168.0.3:554"

# Define ROI polygon
POINTS = np.array([[100, 260], [200, 260], [200, 360], [100, 360]], dtype=np.int32)

# Function to send alerts to Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)
    print(f"✅ Telegram Alert Sent: {message}")

# Function to check if hand is inside defined polygon
def is_inside_polygon(hand_landmarks, frame_width, frame_height):
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    wrist_x, wrist_y = int(wrist.x * frame_width), int(wrist.y * frame_height)
    return cv2.pointPolygonTest(POINTS, (wrist_x, wrist_y), False) >= 0

# Function to detect gestures inside polygon
def detect_gesture(hand_landmarks, frame_width, frame_height):
    if not is_inside_polygon(hand_landmarks, frame_width, frame_height):
        return None

    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

    # Gesture 1: Thumbs Down
    if (thumb_tip.y > thumb_ip.y > wrist.y) and \
       (index_tip.y < thumb_tip.y and middle_tip.y < thumb_tip.y and 
        ring_tip.y < thumb_tip.y and pinky_tip.y < thumb_tip.y):
        return "Thumbs Down 👎 - Problem detected!"
    
    # Gesture 2: SOS Signal
    if (thumb_tip.x > middle_tip.x and 
        index_tip.y < wrist.y and 
        middle_tip.y < wrist.y and 
        ring_tip.y < wrist.y and 
        pinky_tip.y < wrist.y):
        return "🚨 SOS Signal Detected!"
    
    return None

# Function to capture RTSP frames using FFmpeg
def capture_frames(frame_buffer):
    ffmpeg_cmd = [
        r"C:\Users\mr5az\OneDrive\Desktop\Final year project\ffmpeg-7.0.2-full_build\ffmpeg-7.0.2-full_build\bin\ffmpeg.exe",
        "-rtsp_transport", "tcp", "-i", rtsp_url, "-an",  # Disable audio
        "-vf", "scale=640:480",  # Resize to 640x480
        "-pix_fmt", "bgr24", "-f", "rawvideo", "-"
    ]

    try:
        ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**8)
        while True:
            raw_frame = ffmpeg_process.stdout.read(640 * 480 * 3)  # Read a single frame
            if not raw_frame:
                print("⚠️ Error: No frame received from FFmpeg")
                break
            frame = np.frombuffer(raw_frame, np.uint8).reshape((480, 640, 3))
            frame_buffer[0] = frame
    except Exception as e:
        print(f"❌ FFmpeg Error: {e}")

# Function to run OpenCV and detect gestures
def cv_run_program():
    frame_buffer = [None]  # Buffer to hold frames
    frame_thread = threading.Thread(target=capture_frames, args=(frame_buffer,))
    frame_thread.daemon = True
    frame_thread.start()

    global POINTS  
    POINTS = np.array(POINTS, dtype=np.int32)  

    start_time = time.time()
    thumbs_down_count = 0
    sos_signal_count = 0
    total_frames = 0

    while True:
        frame = frame_buffer[0]  # Get the latest frame
        if frame is None:
            time.sleep(0.01)
            continue  # Skip processing if no frame is available

        frame = frame.copy()  # Ensure frame is writable
        frame.flags.writeable = True  

        frame_height, frame_width = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        gesture_detected = None
        cv2.polylines(frame, [POINTS], isClosed=True, color=(255, 0, 0), thickness=2)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                gesture = detect_gesture(hand_landmarks, frame_width, frame_height)
                if gesture:
                    gesture_detected = gesture
                total_frames += 1
                if gesture_detected == "Thumbs Down 👎 - Problem detected!":
                    thumbs_down_count += 1
                    percentage_thumb = (thumbs_down_count / total_frames) * 100
                    print("👎 Thumbs Down Detected!", f"Confidence: {percentage_thumb:.2f}%")
                elif gesture_detected == "🚨 SOS Signal Detected!":
                    sos_signal_count += 1
                    percentage_sos = (sos_signal_count / total_frames) * 100
                    print("🚨 SOS Signal Detected!", f"Confidence: {percentage_sos:.2f}%")

        cv2.putText(frame, gesture_detected if gesture_detected else "", (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow("Hand Gesture Detection", frame)

        if time.time() - start_time > 30 or cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    thumbs_down_percentage = (thumbs_down_count / total_frames) * 100 if total_frames > 0 else 0
    sos_signal_percentage = (sos_signal_count / total_frames) * 100 if total_frames > 0 else 0
    
    if thumbs_down_percentage > 30:  
        send_telegram_message("⚠ ALERT: 👎 Problem detected!")
    elif sos_signal_percentage > 30:  
        send_telegram_message("⚠ ALERT: 🚨 SOS Signal detected!")

    #hands.close()  # Release MediaPipe resources properly
    return "Hand_gesture.py"

#initialize_mediapipe()
#cv_run_program()