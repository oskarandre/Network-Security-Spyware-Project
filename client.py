import socket
import cv2
import threading

SERVER_HOST = "172.20.10.6"
SERVER_PORT = 4000
BUFFER_SIZE = 1024 * 128

#Create the socket object.
s = socket.socket()
s.connect((SERVER_HOST, SERVER_PORT))

#Function to record and send the video.
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

#Start recording video in a separate thread.
recording_thread = threading.Thread(target=record_video)
recording_thread.start()
recording_thread.join()

s.close()