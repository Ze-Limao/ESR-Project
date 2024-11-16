import socket
import sys
from ..utils.safemap import SafeMap
from ..utils.messages import Messages_UDP
from ..utils.config import ONODE_PORT, BOOTSTRAP_IP, BOOTSTRAP_PORT, STREAM_PORT, VIDEO_FILES

class oNode:
    def __init__(self):
        self.socket_bootstrap = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_bootstrap.bind(('', BOOTSTRAP_PORT))
        
        self.socket_monitoring = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_monitoring.bind(('', ONODE_PORT))

        self.socket_streaming = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_streaming.bind(('', STREAM_PORT))

        self.neighbors = []
        self.parent = None

        temp_dict = {}
        for video in VIDEO_FILES:
            temp_dict[video] = (False, [])

        self.streams = SafeMap(temp_dict)

    def register_neighbors(self, neighbors: list):
        self.neighbors = neighbors
        print(f"Neighbors: {self.neighbors}")

    def register_parent(self, parent: str):
        self.parent = parent
        print(f"Parent: {self.parent}")

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
            self.register_parent(response_decoded['parent'])

    def recieve_monitoring_messages(self) -> None:
        while True:
            _, addr = self.socket_monitoring.recvfrom(1024)
            print(f"Received monitoring message from {addr}")
            Messages_UDP.send(self.socket_monitoring, b'', addr[0], addr[1])

if __name__ == "__main__":
    node = oNode()
    node.ask_neighbors()
    node.recieve_monitoring_messages()