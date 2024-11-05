from typing import TypedDict, List, Dict

class Connection(TypedDict):
    node: str
    speed: float

class Node(TypedDict):
    ip: str
    connections: List[Connection]
    alive: bool

class Topology:
    def __init__(self):
        self.topology: Dict[str, Node] = {}

    def add_node(self, node: str, ip: str):
        if node not in self.topology:
            self.topology[node] = {'ip': ip, 'connections': [], 'alive': False}

    def add_edge(self, node1: str, node2: str, speed=1.0):
        if node1 in self.topology and node2 in self.topology:
            self.topology[node1]['connections'].append({'node': node2, 'speed': speed})
            self.topology[node2]['connections'].append({'node': node1, 'speed': speed})
        else:
            raise ValueError("Both nodes must exist before adding an edge.")

    def remove_node(self, node: str):
        for key in list(self.topology):
            self.topology[key]['connections'] = [x for x in self.topology[key]['connections'] if x['node'] != node]
        if node in self.topology:
            del self.topology[node]

    def get_vertices(self):
        return list(self.topology.keys())

    def get_edges(self):
        edges = []
        seen = set()
        for node, data in self.topology.items():
            for edge in data['connections']:
                if (edge['node'], node) not in seen:  # Avoid duplicating edges for undirected graphs
                    edges.append((node, edge['node'], edge['speed']))
                    seen.add((node, edge['node']))
        return edges

    def display(self):
        for node, data in self.topology.items():
            print(f"{node} ({data['ip']} - Alive? {data['alive']}):")
            for conn in data['connections']:
                print(f"  -> {conn['node']} (speed: {conn['speed']})")

    def get_name_by_ip(self, ip: str):
        for node, data in self.topology.items():
            if data['ip'] == ip:
                return node
        return None
    
    def get_neighbors(self, node: str):
        return self.topology[node]['connections']

    def get_neighbors_alive(self, node: str):
        return [x for x in self.topology[node]['connections'] if self.topology[x['node']]['alive']]

    def get_ip(self, node: str):
        return self.topology[node]['ip']
    
    def turn_alive(self, ip: str):
        for node, data in self.topology.items():
            if data['ip'] == ip:
                self.topology[node]['alive'] = True
                return 1
        print(f"Unknown node with IP {ip}")
        return 0

    def turn_dead(self, ip: str):
        for node, data in self.topology.items():
            if data['ip'] == ip:
                self.topology[node]['alive'] = False
                return 1
        print(f"Unknown node with IP {ip}")
        return 0