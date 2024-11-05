import socket
import sys
from ..utils.messages import Messages

class oNode:
    def __init__(self, interface_ip: str, server_ip: str):
        self.interface_ip = interface_ip
        self.server_ip = server_ip
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.interface_ip, 0))
        self.neighbors = []

    def connect(self):
        self.socket.connect((self.server_ip, 8081))
        print(f"Conectado ao servidor em {self.server_ip}:8080")
        try:
            while True:                
                msg = Messages.receive(self.socket)
                self.neighbors = Messages.decode_list(msg)
                print(f"Vizinhos: {self.neighbors}")
                Messages.send(self.socket, Messages.encode("OK"))
        except KeyboardInterrupt:
            Messages.send(self.socket, b'')
            self.close()

    def close(self):
        self.socket.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 src.oNode.oNode <interface_ip> <server_ip>")
        sys.exit(1)

    node = oNode(sys.argv[1], sys.argv[2])
    node.connect()
