import socket, sys, threading
from typing import TypedDict, Dict
from ..utils.safemap import SafeMap
from ..utils.messages import Messages_UDP
from ..utils.config import ONODE_PORT, BOOTSTRAP_IP, BOOTSTRAP_PORT, VIDEO_FILES

class stream_information(TypedDict):
    is_streaming: bool
    thread: threading.Thread
    port: int
    clients: set

class oNode:
    def __init__(self):
        self.socket_bootstrap = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_bootstrap.bind(('', BOOTSTRAP_PORT))
        
        self.socket_monitoring = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_monitoring.bind(('', ONODE_PORT))

        self.neighbors = []
        self.parent = None

        temp_dict: Dict[str, stream_information] = {}
        for video, port in VIDEO_FILES.items():
            temp_dict[video] = {
                'is_streaming': False,
                'thread': None,
                'port': port,
                'clients': set()
            }
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

    def foward_stream(self, rtpsocket: socket.socket, video: str) -> None:
        while True:
            data, addr = rtpsocket.recvfrom(40480)
            print(f"Received stream from {addr}")
            stream: stream_information = self.streams.get(video)
            for client in stream["clients"]:
                Messages_UDP.send(rtpsocket, data, client, stream["port"])

    def process_ask_for_stream(self, video: str, addr: str) -> None:
        stream: stream_information = self.streams.get(video)

        if stream["is_streaming"]:
            stream["clients"].add(addr)
            self.streams.put(video, stream)
        else:
            if self.parent is not None:
                response_encoded = Messages_UDP.send_and_receive(self.socket_bootstrap, video.encode(), self.parent, ONODE_PORT)
                if response_encoded is None:
                    print("No response from parent server")
                    return

                rtpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                rtpsocket.bind(('', stream["port"]))

                stream["thread"] = threading.Thread(target=self.foward_stream, args=(rtpsocket, video))
                stream["thread"].start()
                stream["is_streaming"] = True
                stream["clients"].add(addr)
                self.streams.put(video, stream)

    def recieve_monitoring_messages(self) -> None:
        while True:
            data, addr = self.socket_monitoring.recvfrom(1024)
            print(f"Received monitoring message from {addr}")
            Messages_UDP.send(self.socket_monitoring, b'', addr[0], addr[1])
            if data != b'':
                video = Messages_UDP.decode(data)
                print(f"Video: {video}")
                self.process_ask_for_stream(video, addr[0])

if __name__ == "__main__":
    node = oNode()
    node.ask_neighbors()
    node.recieve_monitoring_messages()