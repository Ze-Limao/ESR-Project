import socket
import sys

class oNode:
    def __init__(self, name: str, ip: str):
        self.name = name
        self.ip = ip
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, 8080))

    def send_message(self, message: str):
        self.socket.send(message.encode())
        response = self.socket.recv(1024)
        print(f"Received: {response.decode()}")

    def close(self):
        self.socket.close()

if __name__ == "__main__":
    node = oNode("oNode1", sys.argv[1])
    node.send_message("Hello")
    node.close()