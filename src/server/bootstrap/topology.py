from typing import TypedDict, List, Dict

class Node(TypedDict):
    name: str
    possible_interfaces: List[str]
    neighbors: List[str]

class Topology:
    def __init__(self):
        self.topology: Dict[str, Node] = {}

    def add_nodes(self, nodes: Dict[str, Node]) -> None:
        self.topology = nodes

    def get_vertices(self) -> List[str]:
        return list(self.topology.keys())

    def get_edges(self) -> List[tuple]:
        edges = []
        seen = set()
        for node, data in self.topology.items():
            for neighbor in data['neighbors']:
                if neighbor not in seen:
                    edges.append((node, neighbor))
            seen.add(node)
        return edges

    def display(self) -> None:
        for node, data in self.topology.items():
            print(f"{node} ({data['name']}):")
            for conn in data['neighbors']:
                print(f"  -> {conn}")

    def get_name_by_ip(self, ip: str) -> str:
        return self.topology[ip]['name']

    def get_neighbors(self, node: str) -> List[str]:
        return self.topology[node]['neighbors']

    def get_ip(self, name: str) -> str:
        for ip, data in self.topology.items():
            if data['name'] == name:
                return ip
        return None
    
    def correct_interface(self, ip: str):
        return ip in self.topology
    
    def get_primary_interface(self, ip: str) -> str:
        for interface, data in self.topology.items():
            if ip in data['possible_interfaces']:
                return interface
        return None
    
    def get_ips_from_list_names(self, names: List[str]) -> List[str]:
        return [self.get_ip(name) for name in names]