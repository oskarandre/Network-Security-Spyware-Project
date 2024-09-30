import tkinter as tk  # For GUI
from tkinter import scrolledtext  # For scrollable text area
import threading  # For running the server in a separate thread
import signal  # For handling the ctrl+c command when exiting the program
from server import start_server, send_command, start_recording, stop_recording, start_streaming, stop_streaming, terminate_server

# Create the main window
root = tk.Tk()
root.title("Server Connection Status")
root.configure(bg='#2e2e2e')  # Set background color to dark

# Create a scrollable text area
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20, bg='#1e1e1e', fg='#ffffff', insertbackground='#ffffff')
text_area.pack(padx=10, pady=10)

# Create buttons with red theme
button_style = {'bg': '#ff0000', 'fg': '#ffffff', 'activebackground': '#cc0000', 'activeforeground': '#ffffff'}

start_button = tk.Button(root, text="Connect", command=lambda: send_command("connect", log_message, root), **button_style)
start_button.pack(side=tk.LEFT, padx=10, pady=10)

record_button = tk.Button(root, text="Record", command=lambda: start_recording(log_message), **button_style)
record_button.pack(side=tk.LEFT, padx=10, pady=10)

stop_record_button = tk.Button(root, text="Stop Recording", command=lambda: stop_recording(log_message), **button_style)
stop_record_button.pack(side=tk.LEFT, padx=10, pady=10)

stream_button = tk.Button(root, text="Stream", command=lambda: start_streaming(log_message), **button_style)
stream_button.pack(side=tk.LEFT, padx=10, pady=10)

stop_stream_button = tk.Button(root, text="Stop Streaming", command=lambda: stop_streaming(log_message), **button_style)
stop_stream_button.pack(side=tk.LEFT, padx=10, pady=10)

exit_button = tk.Button(root, text="Disconnect", command=lambda: send_command("disconnect", log_message, root), **button_style)
exit_button.pack(side=tk.LEFT, padx=10, pady=10)

terminate_button = tk.Button(root, text="Terminate", command=lambda: terminate_server(log_message, root), **button_style)
terminate_button.pack(side=tk.LEFT, padx=10, pady=10)

def log_message(message):
    text_area.insert(tk.END, message + "\n")
    text_area.see(tk.END)

# Function to handle Ctrl+C signal.
def signal_handler(sig, frame):
    log_message('Saving video and exiting...')
    terminate_server(log_message, root)

signal.signal(signal.SIGINT, signal_handler)

# Run the server in a separate thread to keep the GUI responsive
server_thread = threading.Thread(target=start_server, args=(log_message,))
server_thread.start()

# Start the GUI event loop
root.mainloop()