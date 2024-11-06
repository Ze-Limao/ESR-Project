import socket
import sys
from ..utils.messages import Messages
from typing import TypedDict, Dict 

class Neighbor(TypedDict):
    ip: str
    alive: bool

class oNode:
    def __init__(self, interface_ip: str, server_ip: str):
        self.interface_ip = interface_ip
        self.server_ip = server_ip
        self.server_port = 8080
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.interface_ip, 0))
        
        self.socket_onodes = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_onodes.bind((self.interface_ip, 9090))

        self.neighbors: Dict[str, Neighbor] = {}

    def register_neighbors(self, neighbors: list):
        for neighbor in neighbors:
            ip = neighbor['ip']
            name = neighbor['name']
            if name not in self.neighbors:
                self.neighbors[name] = {'ip': ip, 'alive': False}

    def connect(self):
        print(f"Conectado ao servidor em {self.server_ip}:{self.server_port}")
        try:
            while True:
                # Recebe a mensagem do servidor
                msg = Messages.receive(self.socket)
                neighbors = Messages.decode_list(msg)
                print(f"Vizinhos: {neighbors}")
                self.register_neighbors(neighbors)
                
                # Envia uma mensagem de confirmação ao servidor
                Messages.send(self.socket, Messages.encode("OK"))
        except KeyboardInterrupt:
            Messages.send(self.socket, b'')
            self.close()

    def close(self):
        self.socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 -m src.oNode.oNode <interface_ip> <server_ip>")
        sys.exit(1)

    node = oNode(sys.argv[1], sys.argv[2])
    node.connect()