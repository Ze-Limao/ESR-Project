import sys, socket, threading, signal
from ...utils.filereader import FileReader
from ...utils.messages import Messages_UDP
from ...utils.config import BOOTSTRAP_PORT, POINTS_OF_PRESENCE
from .topology import Topology
from typing import Dict, Tuple, List

class Bootstrap:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.topology = Topology()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', 8080))
        
        self.read_file()

        self.port = 5000
        self.threads_oNodes: List[threading.Thread] = []

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

    def get_neighbours(self, ip: str) -> List[str]:
        neighbors = [neighbor['name'] for neighbor in self.topology.get_neighbors(ip)]
        return self.topology.get_ips_from_list_names(neighbors)
        
    def send_interface(self, ip: str) -> None:
        interface = self.topology.get_primary_interface(ip)
        if interface is not None:
            print(f"New interface for {ip}: {interface}")
            Messages_UDP.send(self.socket, Messages_UDP.encode_json({'new_interface': interface}), ip, BOOTSTRAP_PORT)
        else:
            print(f"Unknown interface with IP {ip}")

    def calculate_paths(self) -> None:
        recalculate_tree = False
        for pop in POINTS_OF_PRESENCE:
            path = self.topology.find_best_path(pop)
            if path != None:
                distances, path = path
                bool_new_path: bool = self.topology.store_path(pop, path, distances)
                if bool_new_path:
                    recalculate_tree = True
                print(f"Best path to {pop}: {path} with distance {distances}")
            else:
                print(f"Could not find a path to {pop}")

        if recalculate_tree:
            self.build_tree()

    def build_tree(self) -> None:
        (tree, parents) = self.topology.build_tree()
        updated_parents = self.topology.update_tree(tree, parents)
        self.update_nodes(updated_parents)
        self.topology.display_tree()
    
    def update_nodes(self, updated_parents: List[Tuple[str,str]]) -> None:
        for node, parent in updated_parents:
            Messages_UDP.send(self.socket, Messages_UDP.encode_json({'parent': parent}), node, BOOTSTRAP_PORT)

    def update_topology(self, data: Dict, addr: Tuple[str, int]) -> None:
        for node, time in data.items():
            self.topology.update_velocity(node, time, addr[0])

    def send_initial_data(self, socket_onode: socket.socket, ip_onode: int, onode_port: int, port: int) -> None:
        data = {}
        
        if self.topology.correct_interface(ip_onode):
            data["neighbours"] = self.get_neighbours(ip_onode)
        else:
            correct_interface = self.topology.get_primary_interface(ip_onode)
            data["new_interface"] = correct_interface
            data["neighbours"] = self.get_neighbours(correct_interface)
        data["port"] = port

        Messages_UDP.send(socket_onode, Messages_UDP.encode_json(data), ip_onode, onode_port)

    def handle_oNodes_monitoring(self, ip_onode: str, port_onode: int, port) -> None:
        socket_onode = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_onode.bind(('', port))

        self.send_initial_data(socket_onode, ip_onode, port_onode, port)

        socket_onode.settimeout(60)
        while True:
            try:
                data, addr = socket_onode.recvfrom(1024)
                print("Received data from ", addr)
                self.update_topology(Messages_UDP.decode_json(data), addr)
            except socket.timeout:
                print("Timeout reached.")
                break

        socket_onode.close()
        print(f"Socket of ip {ip_onode} closed.")

    def receive_connections(self) -> None:
        try:
            while True:
                _, addr = self.socket.recvfrom(1024)
                thread = threading.Thread(target=self.handle_oNodes_monitoring, args=(addr[0], addr[1], self.port))
                thread.start()
                self.threads_oNodes.append(thread)
                self.port += 1
        except KeyboardInterrupt:
            print("\nServer disconnected")
        finally:
            self.socket.close()
            print("Socket closed.")
            sys.exit(0)

    def closeBootstrap(self):
        for thread in self.threads_oNodes:
            thread.join()
        self.socket.close()

def ctrlc_handler(sig, frame):
    print("Closing the bootstrap and the threads...")
    bootstrap.closeBootstrap()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 -m src.server.bootstrap.bootstrap <file_path>")
        sys.exit(1)
    
    signal.signal(signal.SIGINT, ctrlc_handler)

    bootstrap = Bootstrap(sys.argv[1])
    topology = bootstrap.get_topology()
    bootstrap.calculate_paths()
    bootstrap.build_tree()
    bootstrap.receive_connections()