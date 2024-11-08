from typing import TypedDict, List, Dict

class Node(TypedDict):
    name: str
    possible_interfaces: List[str]
    neighbors: List[str]

class Topology:
    def __init__(self):
        self.topology: Dict[str, Node] = {}

    def add_nodes(self, nodes: Dict[str, Node]):
        self.topology = nodes

    def get_vertices(self):
        return list(self.topology.keys())

    def get_edges(self):
        edges = []
        seen = set()
        for node, data in self.topology.items():
            for neighbor in data['neighbors']:
                if neighbor not in seen:
                    edges.append((node, neighbor))
            seen.add(node)
        return edges

    def display(self):
        for node, data in self.topology.items():
            print(f"{node} ({data['name']}):")
            for conn in data['neighbors']:
                print(f"  -> {conn}")

    def get_name_by_ip(self, ip: str):
        return self.topology[ip]['name']

    def get_neighbors(self, node: str):
        return self.topology[node]['neighbors']

    def get_ip(self, name: str):
        for ip, data in self.topology.items():
            if data['name'] == name:
                return ip
        return None