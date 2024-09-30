import socket  # For network (client-server) communication.
import cv2  # For recording the video.
import threading  # For recording the video in a different thread.

SERVER_HOST = "192.168.0.8"
SERVER_PORT = 4000
BUFFER_SIZE = 1024 * 128  # 128KB max size of messages, you can adjust this.

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

# Start streaming video in a separate thread
streaming_thread = threading.Thread(target=stream_video)
streaming_thread.start()

# Keep the client running
streaming_thread.join()

# close client connection.
s.close()