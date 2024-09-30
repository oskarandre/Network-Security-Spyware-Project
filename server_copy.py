import socket  # For network (client-server) communication.
import cv2  # For video recording.
import threading  # For running the video recording in a separate thread.
import numpy as np  # For working with video frames.

SERVER_HOST = "0.0.0.0"  # Bind the server to all available network interfaces.
SERVER_PORT = 4000
BUFFER_SIZE = 1024 * 128  # 128KB max size of messages. You can adjust this to your taste

# Global variables
s = None
client_socket = None
streaming_thread = None
running = True  # Flag to control the loop
streaming = False  # Flag to control the streaming loop

def start_server(log_message):
    global s, client_socket, client_address, streaming_thread, running
    # Create the socket object.
    s = socket.socket()
    # Bind the socket to all IP addresses of this host.
    s.bind((SERVER_HOST, SERVER_PORT))
    # Make the PORT reusable
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Set the maximum number of queued connections to 5.
    s.listen(5)
    log_message(f"Listening as {SERVER_HOST} on port {SERVER_PORT} ...")
    # Accept any connections attempted.
    client_socket, client_address = s.accept()
    log_message(f"{client_address[0]}:{client_address[1]} Connected!")

    while running:
        pass  # Keep the server running

    # Close the connection to the client and server.
    if streaming_thread is not None:
        streaming_thread.join()
    client_socket.close()
    s.close()

# Function to stream live video.
def stream_video():
    global streaming
    while streaming:
        # Receive the frame size.
        frame_size = int.from_bytes(client_socket.recv(4), byteorder='little')
        # Receive the frame data.
        frame_data = b''
        while len(frame_data) < frame_size:
            packet = client_socket.recv(min(BUFFER_SIZE, frame_size - len(frame_data)))
            if not packet:
                break
            frame_data += packet
        if not frame_data:
            break
        # Decode the frame.
        frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
        # Display the frame.
        cv2.imshow('Live Camera Feed', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

# Function to start streaming
def start_streaming(log_message):
    global streaming, streaming_thread
    if client_socket is not None and not streaming:
        streaming = True
        streaming_thread = threading.Thread(target=stream_video)
        streaming_thread.start()
        log_message("Live video streaming started.")

# Function to stop streaming
def stop_streaming(log_message):
    global streaming
    if streaming:
        streaming = False
        log_message("Live video streaming stopped.")

# Function to terminate the server
def terminate_server(log_message, root):
    global running
    running = False
    if client_socket is not None:
        client_socket.close()
    if s is not None:
        s.close()
    log_message("Server terminated.")
    root.quit()