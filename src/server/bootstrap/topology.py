from typing import TypedDict, List, Dict, Optional, Tuple
import heapq
from ...utils.config import SOURCE_NODE

class Neighbors(TypedDict):
    name: str
    velocity: float

class Node(TypedDict):
    name: str
    possible_interfaces: List[str]
    neighbors: List[Neighbors]

class Topology:
    def __init__(self):
        self.topology: Dict[str, Node] = {}
        # Store computed paths and distances
        self.paths: Dict[str, List[str]] = {}
        self.distances: Dict[str, float] = {}
        
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
    
    def find_best_path(self, destination: str) -> Optional[Tuple[float, List[str]]]:
        # Return cached result if available
        if destination in self.paths:
            return (self.distances[destination], self.paths[destination])
            
        if destination not in self.topology:
            return None
        
        inf = float('inf')

        # Initialize distances and predecessors
        distances = {node: inf for node in self.topology}
        distances[SOURCE_NODE] = 0
        predecessors = {node: None for node in self.topology}
        
        # Priority queue for Dijkstra's algorithm
        pq = [(0, SOURCE_NODE)]
        visited = set()
        
        while pq:
            _, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
                
            visited.add(current_node)
            
            # Found destination
            if current_node == destination:
                break
            
            # Check all neighbors of current node
            for neighbor in self.topology[current_node]['neighbors']:
                neighbor_ip = self.get_ip(neighbor['name'])
                if neighbor_ip in visited:
                    continue
                    
                # Use velocity as weight (higher velocity = lower weight)
                weight = 1 / neighbor['velocity'] if neighbor['velocity'] > 0 else inf
                new_distance = distances[current_node] + weight
                
                if new_distance < distances[neighbor_ip]:
                    distances[neighbor_ip] = new_distance
                    predecessors[neighbor_ip] = current_node
                    heapq.heappush(pq, (new_distance, neighbor_ip))
        
        # Build path
        if distances[destination] == inf:
            return None
            
        path = []
        current = destination
        while current is not None:
            path.append(current)
            current = predecessors[current]
        path.reverse()
        
        # Store results in class
        self.paths[destination] = path
        self.distances[destination] = distances[destination]
        
        return (distances[destination], path)