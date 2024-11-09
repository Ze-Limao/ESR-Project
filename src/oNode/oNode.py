import socket
import sys
from ..utils.messages import Messages_UDP
from ..utils.config import ONODE_PORT, BOOTSTRAP_IP, BOOTSTRAP_PORT

class oNode:
    def __init__(self):
        self.socket_bootstrap = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_bootstrap.bind(('', BOOTSTRAP_PORT))
        
        self.socket_onodes = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_onodes.bind(('', ONODE_PORT))

        self.neighbors = []

    def register_neighbors(self, neighbors: list):
        self.neighbors = neighbors
        print(f"Neighbors: {self.neighbors}")

    def bind_new_interface(self, interface: str) -> None:
        print(f"New interface: {interface}")
        self.socket_bootstrap.close()
        self.socket_bootstrap = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_bootstrap.bind((interface, BOOTSTRAP_PORT))
        self.ask_neighbors()

    def ask_neighbors(self) -> None:
        response_encoded = Messages_UDP.send_and_receive(self.socket_bootstrap, b'', BOOTSTRAP_IP, BOOTSTRAP_PORT)
        if response_encoded is None:
            print("No response from bootstrap server")
            sys.exit(1)

        response_decoded = Messages_UDP.decode_json(response_encoded)
        if 'new_interface' in response_decoded:
            self.bind_new_interface(response_decoded['new_interface'])
        else:
            self.register_neighbors(response_decoded['neighbors'])

    def close(self) -> None:
        self.socket.close()

if __name__ == "__main__":
    node = oNode()
    node.ask_neighbors()