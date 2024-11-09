import sys
import socket
import threading
from ...utils.filereader import FileReader
from ...utils.messages import Messages_UDP
from ...utils.config import BOOTSTRAP_PORT
from .topology import Topology

class Bootstrap:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.topology = Topology()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', 8080))
        
        self.read_file()

    def read_file(self) -> None:
        file_reader = FileReader(self.file_path)
        file_contents = file_reader.read_json()
        if file_contents is not None:
            self.topology.add_nodes(file_contents)
            self.topology.display()
        else:
            sys.exit(1)

    def get_topology(self) -> Topology:
        return self.topology        

    def send_neighbors(self, ip: str) -> None:
        neighbors = self.topology.get_neighbors(ip)
        ips_neighbors = self.topology.get_ips_from_list_names(neighbors)
        Messages_UDP.send(self.socket, Messages_UDP.encode_json({'neighbors': ips_neighbors}), ip, BOOTSTRAP_PORT)
        
    def send_interface(self, ip: str) -> None:
        interface = self.topology.get_primary_interface(ip)
        if interface is not None:
            print(f"New interface for {ip}: {interface}")
            Messages_UDP.send(self.socket, Messages_UDP.encode_json({'new_interface': interface}), ip, BOOTSTRAP_PORT)
        else:
            print(f"Unknown interface with IP {ip}")

    def receive_connections(self) -> None:
        try:
            while True:
                _, addr = self.socket.recvfrom(1024)
                if self.topology.correct_interface(addr[0]):
                    thread = threading.Thread(target=self.send_neighbors, args=(addr[0],))
                    thread.start()
                else:
                    thread = threading.Thread(target=self.send_interface, args=(addr[0],))
                    thread.start()
                    
        except KeyboardInterrupt:
            print("\nServer disconnected")
            self.socket.close()
            sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 -m src.server.bootstrap.bootstrap <file_path>")
        sys.exit(1)

    bootstrap = Bootstrap(sys.argv[1])
    topology = bootstrap.get_topology()
    bootstrap.receive_connections()