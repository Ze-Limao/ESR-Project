from typing import TypedDict, List, Dict, Optional, Tuple
import heapq
from ...utils.config import SOURCE_NODE, BOOTSTRAP_IP
from ...utils.safemap import SafeMap

class Neighbors(TypedDict):
    ip: str
    velocity: float

class Node(TypedDict):
    possible_interfaces: List[str]
    neighbors: List[Neighbors]

class Topology:
    def __init__(self):
        # Dict[str, Node]
        self.topology = SafeMap()
        # Store computed paths and distances
        # Dict[str, List[str]]
        self.paths = SafeMap()
        # Dict[str, float]
        self.distances = SafeMap()
        # Dict[str, List[str]]
        self.tree = SafeMap()
        # Dict[str, str]
        self.parent_map= SafeMap()
        
    def add_nodes(self, nodes: Dict[str, Node]) -> None:
        for node, data in nodes.items():
            object = {
                'possible_interfaces': data['possible_interfaces'],
                'neighbors': []
            }
            for neighbor in data['neighbors']:
                if neighbor['velocity'] == "inf":
                    neighbor['velocity'] = float('inf')
                else:
                    neighbor['velocity'] = float(neighbor['velocity'])
                object['neighbors'].append(neighbor)
            self.topology.put(node, object)

    def get_vertices(self) -> List[str]:
        return list(self.topology.get_keys())

    def get_edges(self) -> List[tuple]:
        edges = []
        seen = set()
        for node, data in self.topology.get_items():
            for neighbor in data['neighbors']:
                if neighbor not in seen:
                    edges.append((node, neighbor))
            seen.add(node)
        return edges

    def display(self) -> None:
        for node, data in self.topology.get_items():
            print(f"{node}:")
            for conn in data['neighbors']:
                print(f"  -> {conn}")

    def get_neighbors(self, node: str) -> List[Dict[str, float]]:
        return self.topology.get(node)['neighbors']

    def correct_interface(self, ip: str):
        return self.topology.exists(ip)
    
    def get_primary_interface(self, ip: str) -> str:
        for interface, data in self.topology.get_items():
            if ip in data['possible_interfaces']:
                return interface
        return None

    def find_best_path(self, destination: str) -> Optional[Tuple[float, List[str]]]:
        if not self.topology.exists(destination):
            return None
        
        inf = float('inf')

        # Initialize distances and predecessors
        keys = self.topology.get_keys()
        distances = {node: inf for node in keys}
        distances[SOURCE_NODE] = 0
        predecessors = {node: None for node in keys}
        
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
            for neighbor in self.topology.get(current_node)['neighbors']:
                neighbor_ip = neighbor['ip']
                if neighbor_ip in visited:
                    continue
                    
                # Use velocity as weight (higher velocity = lower weight)
                weight = neighbor['velocity'] if neighbor['velocity'] != inf else inf
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

        return (distances[destination], path)
    
    # Function returns True if the path is new or different from the previous one
    def store_path(self, destination: str, path: List[str], velocity: float) -> None:
        if not self.paths.exists(destination) or self.paths.get(destination) != path:
            self.paths.put(destination, path)
            self.distances.put(destination, velocity)
            return True
        return False

    def build_tree(self) -> None:
        tree: Dict[str, List[str]] = {}
        parent_map: Dict[str, str] = {}
        for path in self.paths.get_values():
            first_node = path[0]
            parent_map[first_node] = BOOTSTRAP_IP
            if BOOTSTRAP_IP not in tree:
                tree[BOOTSTRAP_IP] = []
            if first_node not in tree[BOOTSTRAP_IP]:
                tree[BOOTSTRAP_IP].append(first_node)

            for i in range(1, len(path)):
                parent = path[i - 1]
                node = path[i]
                parent_map[node] = parent
                if parent not in tree:
                    tree[parent] = []
                if node not in tree[parent]:
                    tree[parent].append(node)
        return (tree, parent_map)

    # Returns the new parents of the nodes that need to be updated
    def update_tree(self, new_tree: Dict[str, List[str]], new_parent_map: Dict[str, str]) -> List[Tuple[str,str]]:
        new_parents = []
        for node, parent in new_parent_map.items():
            if not self.parent_map.exists(node) or self.parent_map.get(node) != parent:
                new_parents.append((node, parent))
        if new_parents:
            self.tree = SafeMap(new_tree)
            self.parent_map = SafeMap(new_parent_map)
        return new_parents

    def get_parent(self, node: str) -> str:
        return self.parent_map.get(node)
    
    def display_tree(self) -> None:
        for parent, children in self.tree.get_items():
            print(f"{parent}: {children}")

    def update_velocity(self, ip_node: str, ip_neigbour: str, velocity: float) -> None:
        print(f"Updating velocity from {ip_node} to {ip_neigbour} with {velocity}")
        information_node: Node = self.topology.get(ip_node)
        for neighbor in information_node['neighbors']:
            if neighbor['ip'] == ip_neigbour:
                neighbor['velocity'] = velocity
                break
        self.topology.put(ip_node, information_node)