import socket
import threading
import queue
import os

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 4000
BUFFER_SIZE = 1024 * 128  # Buffer size for receiving data
SEPARATOR = "<sep>"

clients = []
client_sockets = {}
keypress_queues = {}
message_queues = {}  # Add this line


# Function to handle client messages, including image data
def handle_client(client_socket, client_address):
    client_ip = client_address[0]
    print(f"Connection from {client_ip} established!")

    message_queues[client_address] = queue.Queue()  # Add this line

    while True:
        try:
            # Wait to receive the first message from the client
            data = client_socket.recv(BUFFER_SIZE).decode()

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
                print(f"Received message from {client_ip}: {data}")
                message_queues[client_address].put(data)  # Add this line
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
        update_clients_list(clients)
        print(f"{client_address[0]}:{client_address[1]} Connected!")
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()


# Function to stop the server and close all client connections
def stop_server():
    try:
        for client in clients:
            client_sockets[client].close()
        s.close()
    except Exception as e:
        print(f"Error stopping server: {e}")