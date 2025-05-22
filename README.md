# 📚 EduCam AI - Smart Event Driven Classroom Monitoring & Real-Time Alerts

EduCam AI is an innovative, AI-powered classroom monitoring system that automates attendance, enhances security, and provides real-time alerts for critical classroom events. Designed to be efficient, scalable, and cost-effective, the system combines edge computing, facial recognition, gesture detection, and animal intrusion detection using affordable hardware like Raspberry Pi and H.265 IP cameras.

---

## 🎯 Objectives

- ✅ Automate attendance using AI-powered facial recognition.
- 🔍 Trigger real-time video processing only during motion/events.
- 🛡️ Monitor classroom security with gesture-based SOS and animal detection.
- ☁️ Log attendance to Google Sheets for centralized cloud-based access.
- 🤖 Send alerts and updates through the Telegram-based **EduCam AI Bot**.

---

## 🧠 Key Features

- **Face Recognition** using OpenCV and `face_recognition` for automated attendance.
- **Gesture Detection** (e.g., SOS sign, thumbs down) with Google Mediapipe.
- **Object Detection** using YOLOv8n for identifying animals or unusual objects.
- **Event-Driven Processing** to reduce bandwidth and power consumption.
- **Google Sheets API** integration for real-time cloud logging.
- **Telegram Bot** interface for alerts and commands.

---

## 🏗️ System Architecture

- **Raspberry Pi 4 Model B**: Edge computing and AI model host.
- **H.265 IP Cameras with Polarization Lens**: Video input under various lighting.
- **Agent DVR / NVR**: Manages video stream input.
- **YOLOv8n**: Lightweight object detection for edge devices.
- **MediaPipe**: Real-time gesture recognition.
- **Google Sheets API**: For attendance storage.
- **Telegram Bot**: Real-time alert delivery and control.

---

## ⚙️ Hardware Requirements

| Component       | Specification                        |
|----------------|--------------------------------------|
| Raspberry Pi    | 4 Model B (4GB RAM)                  |
| IP Camera       | H.265 Codec with IR + Polarizer      |
| NVR             | Hikvision DS-7604NI-Q1/4P            |
| Power Supply    | 5V 3A USB-C Adapter                  |
| Micro SD Card   | 16GB Class 10 / UHS-I                |

![Graphical Represtation](https://github.com/5azkon/Educam-AI/blob/main/IMAGE_DATAS/Educam%20AI%20circuit%20diagram.jpg)
---

## 🛠️ Software Stack

- **OS**: Raspberry Pi OS (Lite/Full)
- **Language**: Python 3.x
- **Libraries**:
  - `OpenCV`
  - `face_recognition`
  - `MediaPipe`
  - `YOLOv8 (Ultralytics)`
  - `python-telegram-bot`
  - `gspread`, `oauth2client` (Google Sheets)

![Block Diagram]()
---

## 🧪 Functional Modules

### 📷 Attendance Automation
- Face detection → Encoding → Comparison → Logging to Google Sheets.

### ✋ Gesture-Based Alerts
- SOS and thumbs-down gestures initiate alerts via Telegram.

### 🐾 Animal Detection
- YOLOv8n identifies dogs, cats, snakes, etc., and notifies via Telegram.

### 📤 Telegram Bot
- `/start` to begin attendance
- `/help` to list commands
- Sends alerts and updates in real time

---

## 🚀 Deployment Considerations

- **Static IP** setup for Raspberry Pi and camera.
- **SSH/VNC** access for remote configuration.
- **Event-based processing** to reduce CPU load and power use.
- **Backup Power** support for uninterrupted operation.

---

## 🔐 Security

- Encrypted camera feeds.
- Authorized access to the Telegram bot.
- Local AI inference to protect student data privacy.

---

## 📈 Results

- Attendance accuracy > 90%
- Real-time alerts with <1s latency
- Low resource consumption with edge processing

---

## 🔮 Future Enhancements

- Mask and behavior detection
- Voice-based alerts
- Integration with student information systems

---

## 👨‍💻 Authors

- **Fiaz Khan A** – [LinkedIn](https://www.linkedin.com)
- **Karthikeyan S** – [LinkedIn](https://www.linkedin.com)

---

## 📜 License

This project is for academic and research purposes under the guidance of Prince Shri Venkateshwara Padmavathy Engineering College, Anna University.

---

## 🙏 Acknowledgements

Special thanks to our guides, faculty, and project coordinators for their constant support and encouragement.

---

