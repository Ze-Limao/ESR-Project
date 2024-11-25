from typing import TypedDict, List, Dict, Optional, Tuple
import heapq
from ...utils.config import SOURCE_NODE, BOOTSTRAP_IP

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
        self.tree: Dict[str, List[str]] = {}
        self.parent_map: Dict[str, str]= {}
        
    def add_nodes(self, nodes: Dict[str, Node]) -> None:
        for node, data in nodes.items():
            self.topology[node] = {
                'name': data['name'],
                'possible_interfaces': data['possible_interfaces'],
                'neighbors': []
            }
            for neighbor in data['neighbors']:
                if neighbor['velocity'] == "inf":
                    neighbor['velocity'] = float('inf')
                else:
                    neighbor['velocity'] = float(neighbor['velocity'])
                self.topology[node]['neighbors'].append(neighbor)

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
                weight = 1 / neighbor['velocity'] if neighbor['velocity'] != inf else inf
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
        if destination not in self.paths or self.paths[destination] != path:
            self.paths[destination] = path
            self.distances[destination] = velocity
            return True
        return False

    def build_tree(self) -> None:
        tree: Dict[str, List[str]] = {}
        parent_map: Dict[str, str] = {}
        for _, path in self.paths.items():
            # Set the server as the parent of the first node in the path
            first_node = path[0]
            parent_map[first_node] = BOOTSTRAP_IP
            # Add the first node as a child of the server IP in the tree
            if BOOTSTRAP_IP not in tree:
                tree[BOOTSTRAP_IP] = []
            if first_node not in tree[BOOTSTRAP_IP]:
                tree[BOOTSTRAP_IP].append(first_node)

            for i in range(1, len(path)):
                parent = path[i - 1]
                node = path[i]
                # Set the parent of the current node
                parent_map[node] = parent
                # Initialize tree structure if not present
                if parent not in tree:
                    tree[parent] = []
                # Add child to parent's list
                if node not in tree[parent]:
                    tree[parent].append(node)
        return (tree, parent_map)

    # Returns the new parents of the nodes that need to be updated
    def update_tree(self, new_tree: Dict[str, List[str]], new_parent_map: Dict[str, str]) -> List[Tuple[str,strgi]]:
        new_parents = []
        for node, parent in new_parent_map.items():
            if node not in self.parent_map or self.parent_map[node] != parent:
                new_parents.append((node, parent))
        if new_parents:
            self.tree = new_tree
            self.parent_map = new_parent_map
        return new_parents

    def get_parent(self, node: str) -> str:
        return self.parent_map[node] if node in self.parent_map else None
    
    def display_tree(self) -> None:
        for parent, children in self.tree.items():
            print(f"{parent}: {children}")

    def update_velocity(self, node: str, velocity: float, ip: str) -> None:
        for neighbour in self.topology[ip]['neighbors']:
            if neighbour['name'] == self.get_name_by_ip(node):
                neighbour['velocity'] = velocity
                break