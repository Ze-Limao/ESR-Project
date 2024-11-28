import socket, sys, threading, signal, time
from typing import TypedDict, Dict
from ..utils.safemap import SafeMap
from ..utils.messages import Messages_UDP
from ..utils.config import ONODE_PORT, BOOTSTRAP_IP, BOOTSTRAP_PORT, VIDEO_FILES, ONODE_MONITORING_PORT
from typing import List

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

        self.socket_self_monitoring = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_self_monitoring.bind(('', ONODE_MONITORING_PORT))

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

        self.thread_monitoring = threading.Thread(target=self.receive_monitoring_messages)
        self.threads_monitoring_neighbours: List[threading.Thread] = []
        self.stop_event = threading.Event()

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

    def ask_neighbors(self) -> None:
        response_encoded = Messages_UDP.send_and_receive(self.socket_bootstrap, b'', BOOTSTRAP_IP, BOOTSTRAP_PORT)
        if response_encoded is None:
            print("No response from bootstrap server")
            sys.exit(1)

        response_decoded = Messages_UDP.decode_json(response_encoded)
        if 'new_interface' in response_decoded:
            self.bind_new_interface(response_decoded['new_interface'])

        self.register_neighbors(response_decoded['neighbours'])

    def foward_stream(self, rtpsocket: socket.socket, video: str) -> None:
        rtpsocket.settimeout(1)  # Set a 1-second timeout
        while not self.stop_event.is_set():
            try:
                data, addr = rtpsocket.recvfrom(40480)
                print(f"Received stream from {addr}")
                stream: stream_information = self.streams.get(video)
                for client in stream["clients"]:
                    Messages_UDP.send(rtpsocket, data, client, stream["port"])
            except socket.timeout:
                # Timeout occurred, loop back and check stop_event
                continue
            except Exception as e:
                print(f"An error occurred: {e}")
                break

    def process_ask_for_stream(self, video: str, addr: str) -> None:
        stream: stream_information = self.streams.get(video)

        if stream["is_streaming"]:
            stream["clients"].add(addr)
            self.streams.put(video, stream)
        else:
            if self.parent is not None:
                response_encoded = Messages_UDP.send_and_receive(self.socket_bootstrap, Messages_UDP.encode_json({"stream": video}), self.parent, ONODE_PORT)
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

    def handle_message_received(self, data: Dict[str,str], ip) -> None:
        if "stream" in data:
            self.process_ask_for_stream(data["stream"], ip)
        elif "parent" in data:
            self.register_parent(data["parent"])
        else:
            print("Invalid message received")

    def receive_monitoring_messages(self) -> None:
        self.socket_monitoring.settimeout(1)  # Set a 1-second timeout
        while not self.stop_event.is_set():
            try:
                data, addr = self.socket_monitoring.recvfrom(1024)
                # print(f"Received monitoring message from {addr}")
                Messages_UDP.send(self.socket_monitoring, b'', addr[0], addr[1])
                if data != b'':
                    video = Messages_UDP.decode_json(data)
                    self.handle_message_received(video, addr[0])
            except socket.timeout:
                # Timeout occurred, loop back and check stop_event
                continue
            except Exception as e:
                print(f"An error occurred: {e}")
                break

    def send_monitoring_messages(self, ip_neighbour: str) -> None:
        while not self.stop_event.is_set():
            rtt = float('inf')
            timestamp = time.time()
            data = Messages_UDP.send_and_receive(self.socket_self_monitoring, b'', ip_neighbour, ONODE_PORT)
            if data != None:
                rtt = time.time() - timestamp
            # print(rtt, ip_neighbour)
            Messages_UDP.send(self.socket_bootstrap, Messages_UDP.encode_json({ip_neighbour: rtt}), BOOTSTRAP_IP, BOOTSTRAP_PORT)
            time.sleep(1)

    def closeStreaming (self) -> None:
        # Close Threads
        values_streams : stream_information = self.streams.get_values()
        self.stop_event.set()
        for stream in values_streams:
            stream["is_streaming"] = False
            if stream["thread"] is not None:
                stream["thread"].join()
                stream["thread"] = None

        self.thread_monitoring.join()
        for monitoring_thread in self.threads_monitoring_neighbours:
            monitoring_thread.join()
        # Close sockets
        self.socket_bootstrap.close()
        self.socket_monitoring.close()

    def start_threads_monitoring_neighbours(self) -> None:
        for neighbour in self.neighbors:
            thread = threading.Thread(target=self.send_monitoring_messages, args=(neighbour,))
            thread.start()
            self.threads_monitoring_neighbours.append(thread)

def ctrlc_handler(sig, frame):
    print("Closing the server and the threads...")
    node.closeStreaming()

def ctrl_slash_handler(sig, frame):
    print("Simulating a sudden oNode shutdown...")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 1:
        print("python3 -m src.oNode.oNode")
        sys.exit(1)

    # Register the signal to shut down the server at the time of CTRL+C
    signal.signal(signal.SIGINT, ctrlc_handler)
    # Register the signal to simulate the sudden shutdown of the server at the time of CTRL+\
    signal.signal(signal.SIGQUIT, ctrl_slash_handler)

    node = oNode()
    node.ask_neighbors()
    node.thread_monitoring.start()
    node.start_threads_monitoring_neighbours()