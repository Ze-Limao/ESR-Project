import sys
import socket
from ...utils.filereader import FileReader
from ...utils.messages import Messages
from .topology import Topology

class Bootstrap:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.topology = Topology()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', 8081))
        self.socket.listen(5)
        
        self.read_file()

    def read_file(self):
        file_reader = FileReader(self.file_path)
        file_contents = file_reader.read()
        self.parse_contents(file_contents)

    def parse_contents(self, contents: str):
        lines = contents.split('\n')
        n_nodes = int(lines[0])
        n_connections = int(lines[1])
        for i in range(2,n_nodes+2):
            name, ip = lines[i].split(' ')
            self.topology.add_node(name, ip)
        for i in range(n_nodes+2, n_nodes+n_connections+2):
            node1, node2 = lines[i].split(' ')
            self.topology.add_edge(node1, node2)

        self.topology.display()

    def get_topology(self):
        return self.topology        

    def receive_connections(self):
        while True:
            conn, addr = self.socket.accept()
            print(f"Connection from {addr}")
            
            name = self.topology.get_name_by_ip(addr[0])
            if name is not None:
                neighbors = self.topology.get_neighbors(name)
                for neighbor in neighbors:
                    neighbor['name'] = self.topology.get_ip(neighbor['node'])
                Messages.send(conn, Messages.encode_list(neighbors))

            else:
                print(f"Unknown node with IP {addr[0]}")

            conn.close()
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 -m src.server.bootstrap.bootstrap <file_path>")
        sys.exit(1)

    bootstrap = Bootstrap(sys.argv[1])
    topology = bootstrap.get_topology()
    bootstrap.receive_connections()