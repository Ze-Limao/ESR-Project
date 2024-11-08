import socket
import sys
from ..utils.messages import Messages_UDP
from typing import TypedDict, Dict 

BOOTSTRAP_IP = '10.0.13.10'
BOOTSTRAP_PORT = 8080
ONODE_PORT = 9090

class Neighbor(TypedDict):
    ip: str
    alive: bool

class oNode:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', 0))
        
        self.socket_onodes = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_onodes.bind(('', ONODE_PORT))

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
                msg = Messages_UDP.receive(self.socket)
                neighbors = Messages_UDP.decode_list(msg)
                print(f"Vizinhos: {neighbors}")
                self.register_neighbors(neighbors)
                
                # Envia uma mensagem de confirmação ao servidor
                Messages_UDP.send(self.socket, Messages_UDP.encode("OK"))
        except KeyboardInterrupt:
            Messages_UDP.send(self.socket, b'')
            self.close()

    def close(self):
        self.socket.close()

if __name__ == "__main__":
    node = oNode()
    node.connect()