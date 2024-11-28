import sys, socket, threading
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
        self.socket.bind(('', BOOTSTRAP_PORT))
        
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

    def update_topology(self, data: Dict, ip: str) -> None:
        print("Updating topology...", data)
        for node, time in data.items():
            self.topology.update_velocity(node, time, ip)

    def send_initial_data(self, socket: socket.socket, ip_onode: int, onode_port: int) -> None:
        data = {}
        
        if self.topology.correct_interface(ip_onode):
            data["neighbours"] = self.get_neighbours(ip_onode)
        else:
            correct_interface = self.topology.get_primary_interface(ip_onode)
            data["new_interface"] = correct_interface
            data["neighbours"] = self.get_neighbours(correct_interface)

        Messages_UDP.send(socket, Messages_UDP.encode_json(data), ip_onode, onode_port)

    def receive_connections(self) -> None:
        try:
            while True:
                data, addr = self.socket.recvfrom(1024)
                if data != b'':
                    threading.Thread(target=self.update_topology, args=(Messages_UDP.decode_json(data), addr[0])).start()
                else:
                    threading.Thread(target=self.send_initial_data, args=(self.socket, addr[0], addr[1])).start()
        except KeyboardInterrupt:
            print("\nServer disconnected")
        finally:
            self.socket.close()
            print("Socket closed.")
            sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 -m src.server.bootstrap.bootstrap <file_path>")
        sys.exit(1)
    
    bootstrap = Bootstrap(sys.argv[1])
    topology = bootstrap.get_topology()
    bootstrap.calculate_paths()
    bootstrap.build_tree()
    bootstrap.receive_connections()