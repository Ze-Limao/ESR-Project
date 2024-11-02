import sys
from ...utils.filereader import FileReader
from .topology import Topology

class Bootstrap:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.topology = Topology()
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
    
if __name__ == "__main__":
    bootstrap = Bootstrap(sys.argv[1])
    topology = bootstrap.get_topology()