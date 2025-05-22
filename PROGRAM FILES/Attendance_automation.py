# importing libraries
import cv2
import face_recognition
import numpy as np
import collections
import threading
import time
import os
import gspread
from datetime import datetime
import requests
import re
from gspread.utils import rowcol_to_a1

# Google Sheets API Setup
SERVICE_ACCOUNT_FILE = r"C:\Users\mr5az\OneDrive\Desktop\Final year project\Educam AI project\attendance-automation-fk5555-cf5c94d2daac.json"
SHEET_NAME = "Attendance_automation"
TELEGRAM_BOT_TOKEN = "7626974749:AAFSfBcUqanynya1CRLLFyvB8wqGHrHsdts"
TELEGRAM_CHAT_ID = "-4741709947"  # "1654914770" - personal id

# Authenticate with Google Sheets
gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
sh = gc.open(SHEET_NAME)
worksheet = sh.sheet1


# Load known encodings
KNOWN_ENCODINGS_PATH = r"C:\Users\mr5az\OneDrive\Desktop\Final year project\Educam AI project\encodings.npy"
KNOWN_NAMES_PATH = r"C:\Users\mr5az\OneDrive\Desktop\Final year project\Educam AI project\names.npy"

known_encodings = np.load(KNOWN_ENCODINGS_PATH)
known_names = np.load(KNOWN_NAMES_PATH)

# Global Variables
frame = None
frame_lock = threading.Lock()
students = ["Fiaz Khan", "Karthikeyan", "Harish", "Deepak", "Jeeva"]

def video_capture():
    global frame
    cap = cv2.VideoCapture("rtsp://admin:Skk@2004@192.168.0.3:554/stream")
    #cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Cannot open RTSP stream")
        return

    frame_skip = 5 # Process every 5th frame
    frame_count = 0

    while True:
        ret, new_frame = cap.read()
        if not ret:
            print("⚠️ Warning: Frame capture failed, retrying...")
            time.sleep(0.1)
            continue

        frame_count += 1
        if frame_count % frame_skip == 0:  # Only update frame every 'frame_skip' captures
            with frame_lock:
                frame = new_frame

def recognize_faces():
    global frame
    recognized_counts = collections.defaultdict(int)
    total_frames = 0
    start_time = time.time()

    while time.time() - start_time < 60:  #Adjust the time based on the requirement ("n" seconds)
        with frame_lock:
            if frame is None:
                time.sleep(0.05)
                continue
            process_frame = frame.copy()
        
        rgb_frame = cv2.cvtColor(process_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if not face_encodings:
            continue

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            min_distance_index = np.argmin(distances)
            name = "Stranger"
            
            if distances[min_distance_index] < 0.5:  # Threshold for face recognition
                name = known_names[min_distance_index]
                recognized_counts[name] += 1
                total_frames += 1
            
            percentage = (recognized_counts[name] / total_frames) * 100 if total_frames > 0 else 0
            print(f"Recognized: {name} - {percentage:.2f}%")
            
            cv2.rectangle(process_frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(process_frame, f"{name} ({percentage:.2f}%)", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("Face Recognition", process_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    print_attendance_results(recognized_counts, total_frames)
    update_google_sheets(recognized_counts, total_frames)
    send_to_telegram()
    print("✅ Attendance Process Completed.")

def print_attendance_results(attendance, total_frames):
    present_list = []
    absent_list = []
    for student in students:
        percentage = (attendance.get(student, 0) / total_frames) * 100 if total_frames > 0 else 0
        if percentage >= 30:   #change the percentage based on the requirement
            present_list.append(student)
        else:
            absent_list.append(student)
    print("Present:", present_list)
    print("Absent:", absent_list)

def update_google_sheets(attendance, total_frames):
    now = datetime.now().strftime("%d/%m/%y - %I:%M %p")
    col_num = len(worksheet.row_values(1)) + 1
    worksheet.update_cell(1, col_num, now)
    col_letter = rowcol_to_a1(1, col_num)  
    worksheet.update_acell(col_letter, now) 

    for i, student in enumerate(students, start=2):
        percentage = (attendance.get(student, 0) / total_frames) * 100 if total_frames > 0 else 0
        status = "Present ✅" if percentage >= 30 else "Absent ❌" #change the percentage based on the requirement
        cell_address = rowcol_to_a1(i, col_num)  
        worksheet.update_acell(cell_address, status)
    
    print("✅ Attendance updated in Google Sheets.")

def send_to_telegram():
    sheet_url = sh.url
    safe_url = re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', sheet_url)
    message = f"📊 *Attendance Result*\nCheck here: {safe_url}"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "MarkdownV2"}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        print("📩 Attendance result sent to Telegram successfully!")
    else:
        print("❌ Failed to send message to Telegram!")

# Run video capture in a separate thread
capture_thread = threading.Thread(target=video_capture, daemon=True)
capture_thread.start()

# Run the face recognition process
recognize_faces()
