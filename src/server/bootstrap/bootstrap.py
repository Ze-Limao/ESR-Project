import sys
import socket
import time
import threading
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

    def send_neighbors(self, conn: socket.socket, ip: str):
        name = self.topology.get_name_by_ip(ip)
        if name is not None:
            neighbors = self.topology.get_neighbors(name)
            for neighbor in neighbors:
                neighbor['name'] = self.topology.get_ip(neighbor['node'])
            Messages.send(conn, Messages.encode_list(neighbors))
        else:
            print(f"Unknown node with IP {ip}")

    def send_neighbors_alive(self, conn: socket.socket, ip: str):
        name = self.topology.get_name_by_ip(ip)
        if name is not None:
            neighbors = self.topology.get_neighbors_alive(name)
            for neighbor in neighbors:
                neighbor['name'] = self.topology.get_ip(neighbor['node'])
            Messages.send(conn, Messages.encode_list(neighbors))
        else:
            print(f"Unknown node with IP {ip}")

    def handle_connection(self, conn: socket.socket, addr: str):
        print(f"Connection from {addr}")
        ip = addr[0]

        check = self.topology.turn_alive(ip)

        if check == 0:
            print(f"Unknown node with IP {ip}")
            conn.close()
            return

        while True:
            self.send_neighbors_alive(conn, ip)
            msg = Messages.receive(conn)
            if msg == b'':
                break
            msg = Messages.decode(msg)
            print(f"Received message from {ip}: {msg}")
            time.sleep(5)

        self.topology.turn_dead(ip)
        conn.close()

    def receive_connections(self):
        try:
            while True:
                conn, addr = self.socket.accept()
                thread = threading.Thread(target=self.handle_connection, args=(conn, addr))
                thread.start()
        except KeyboardInterrupt:
            print("\nServer disconnected")
            self.socket.close()
            sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 -m src.server.bootstrap.bootstrap <file_path>")
        sys.exit(1)

    bootstrap = Bootstrap(sys.argv[1])
    topology = bootstrap.get_topology()
    bootstrap.receive_connections()