import socket
import subprocess
import threading
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from Hand_gesture import cv_run_program, initialize_mediapipe

# Telegram bot token
TELEGRAM_BOT_TOKEN = "7626974749:AAFSfBcUqanynya1CRLLFyvB8wqGHrHsdts"

# Paths
ATTENDANCE_PROGRAM = r"C:\Users\mr5az\OneDrive\Desktop\Final year project\Educam AI project\Attendance_automation.py"
ALERT_PROGRAM_PATH = r"C:\Users\mr5az\OneDrive\Desktop\Final year project\Educam AI project\Alert_program.py"


# UDP settings
UDP_IP = "0.0.0.0"
UDP_PORT = 5005

# Global flag and lock
ai_running = False
lock = threading.Lock()

# ========== Telegram Bot Handlers ==========
async def start(update: Update, context: CallbackContext):
    global ai_running
    with lock:
        if ai_running:
            await update.message.reply_text("⚠️ Another task is already running. Please wait...")
        else:
            ai_running = True
            await update.message.reply_text("🤖 Starting Attendance Automation...")
            print("🚀 Starting Attendance Automation...")
            threading.Thread(target=run_attendance_program, daemon=True).start()

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text("Use /start to run the attendance automation script.")

def run_attendance_program():
    global ai_running
    try:
        subprocess.run(["python", ATTENDANCE_PROGRAM], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Script Execution Error: {e}")
    finally:
        ai_running = False
        print("✅ Attendance automation finished.")

# ========== UDP Server ==========
def udp_server():
    global ai_running

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"📡 Listening for UDP messages on {UDP_IP}:{UDP_PORT}...")

    while True:
        data, addr = sock.recvfrom(1024)
        message = data.decode().strip().lower()
        print(f"📩 Received from {addr}: {message}")

        with lock:
            if ai_running:
                print("⚠️ Another task is already running. Ignoring request.")
                continue

            ai_running = True
            if "hand_gesture" in message:
                print("🚀 Starting Hand Gesture Model...")
                threading.Thread(target=run_Gesture_model, daemon=True).start()

            elif "start_the_ai_model" in message:
                print("🚀 Starting Alert Model...")
                threading.Thread(target=run_alert_model, daemon=True).start()

        time.sleep(1)

def run_alert_model():
    global ai_running
    try:
        subprocess.run(["python", ALERT_PROGRAM_PATH], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Alert Model Error: {e}")
    finally:
        ai_running = False
        print("✅ Alert model finished.")

def run_Gesture_model():
    global ai_running
    try:
        cv_run_program()
    except Exception as e:
        print(f"❌ Hand Gesture Error: {e}")
    finally:
        ai_running = False
        print("✅ Hand Gesture model finished.")

# ========== Main ==========
def main():
    initialize_mediapipe()
    threading.Thread(target=udp_server, daemon=True).start()

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    print("🚀 Telegram Bot and UDP Server running...")
    app.run_polling()

if __name__ == "__main__":
    main()
