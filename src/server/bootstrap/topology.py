class Topology:
    def __init__(self):
        self.adjacency_list = {}

    def add_node(self, node):
        if node not in self.adjacency_list:
            self.adjacency_list[node] = []

    def add_edge(self, node1, node2, weight=None, directed=False):
        if node1 not in self.adjacency_list:
            self.add_node(node1)
        if node2 not in self.adjacency_list:
            self.add_node(node2)
        
        # Add an edge from node1 to node2
        self.adjacency_list[node1].append((node2, weight))
        
        # If undirected, also add an edge from node2 to node1
        if not directed:
            self.adjacency_list[node2].append((node1, weight))

    def remove_edge(self, node1, node2, directed=False):
        self.adjacency_list[node1] = [edge for edge in self.adjacency_list[node1] if edge[0] != node2]
        if not directed:
            self.adjacency_list[node2] = [edge for edge in self.adjacency_list[node2] if edge[0] != node1]

    def remove_node(self, node):
        for key in list(self.adjacency_list):
            self.adjacency_list[key] = [edge for edge in self.adjacency_list[key] if edge[0] != node]
        if node in self.adjacency_list:
            del self.adjacency_list[node]

    def get_vertices(self):
        return list(self.adjacency_list.keys())

    def get_edges(self):
        edges = []
        for node, connections in self.adjacency_list.items():
            for edge in connections:
                edges.append((node, edge[0], edge[1]))  # (start, end, weight)
        return edges

    def display(self):
        for node in self.adjacency_list:
            print(f"{node} -> {self.adjacency_list[node]}")
