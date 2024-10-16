import sys, socket, signal

class Client:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.rtsp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.rtsp_socket.connect((self.server_ip, self.server_port))
        print(f"Connected to server at {self.server_ip}:{self.server_port}")

    def send_request(self, request):
        self.rtsp_socket.send(request.encode())
        response = self.rtsp_socket.recv(1024).decode()
        print(f"Received from server: {response}")

    def close(self):
        self.rtsp_socket.close()

def ctrlc_handler(sig,frame):
    print("\n Exiting server")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, ctrlc_handler)
    if len(sys.argv) != 3:
        print("[Usage: Client.py Server_IP Server_Port]\n")
        return

    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])

    client = Client(server_ip, server_port)
    client.connect()

    while True:
        request = input("Enter request (SETUP, PLAY, PAUSE, TEARDOWN): ")
        client.send_request(request)
        if request == "TEARDOWN":
            break

    client.close()

if __name__ == "__main__":
    main()