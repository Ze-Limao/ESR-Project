from typing import TypedDict, List, Dict

class Node(TypedDict):
    ip: str
    connections: List[str]

class Topology:
    def __init__(self):
        self.topology: Dict[str, Node] = {}

    def add_node(self, node: str, ip: str):
        self.display()
        if node not in self.topology:
            self.topology[node] = {'ip': ip, 'connections': []}
        else:
            raise ValueError("Node already exists in the topology.")

    def add_edge(self, node1: str, node2: str):
        if node1 in self.topology and node2 in self.topology:
            if node2 not in self.topology[node1]['connections']:
                self.topology[node1]['connections'].append(node2)
            if node1 not in self.topology[node2]['connections']:
                self.topology[node2]['connections'].append(node1)
        else:
            raise ValueError("Both nodes must exist before adding an edge.")

    def remove_node(self, node: str):
        for key in list(self.topology):
            self.topology[key]['connections'] = list(filter(lambda x: x != node, self.topology[key]['connections']))
        if node in self.topology:
            del self.topology[node]

    def get_vertices(self):
        return list(self.topology.keys())

    def get_edges(self):
        edges = []
        seen = set()
        for node, data in self.topology.items():
            for neighbor in data['connections']:
                if neighbor not in seen:
                    edges.append((node, neighbor))
            seen.add(node)
        return edges

    def display(self):
        for node, data in self.topology.items():
            print(f"{node} ({data['ip']}):")
            for conn in data['connections']:
                print(f"  -> {conn}")

    def get_name_by_ip(self, ip: str):
        for node, data in self.topology.items():
            if data['ip'] == ip:
                return node
        return None
    
    def get_neighbors(self, node: str):
        return self.topology[node]['connections']

    def get_ip(self, node: str):
        return self.topology[node]['ip']