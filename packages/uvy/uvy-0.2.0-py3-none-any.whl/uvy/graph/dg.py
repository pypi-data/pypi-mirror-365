from typing import Callable, Dict, Generic, Hashable, List, Optional, Protocol, Set, TypeVar

import rustworkx as rx

T = TypeVar("T", bound=Hashable)


class IDependencyGraph(Protocol, Generic[T]):
    def add_node(self, node: T) -> int: ...
    def add_edge(self, from_node: T, to_node: T, label: Optional[str] = None) -> int: ...
    def find_cycles(self) -> List[List[T]]: ...
    def get_dependents(self, node: T, depth: Optional[int] = None) -> List[T]: ...
    def get_dependents_of(self, nodes: List[T], depth: Optional[int] = None) -> List[T]: ...
    def get_dependees(self, node: T, depth: Optional[int] = None) -> List[T]: ...
    def get_dependees_of(self, nodes: List[T], depth: Optional[int] = None) -> List[T]: ...


class DependencyGraph(IDependencyGraph[T]):
    """
    A directed acyclic graph (DAG) implementation for managing dependencies.

    This class allows adding nodes and edges, detecting cycles, and retrieving dependents and dependee.
    It uses Rust's `rustworkx` library for efficient graph operations.
    """

    def __init__(self):
        self.graph = rx.PyDiGraph()
        self.node_map: Dict[T, int] = {}
        """Initializes an empty dependency graph."""

    def add_node(self, node: T) -> int:
        """
        Adds a node to the graph.

        Args:
            node (T): The payload of the node to be added.

        Returns:
            int: The index of the newly added node.
        """
        if node in self.node_map:
            return self.node_map[node]
        index = self.graph.add_node(node)
        self.node_map[node] = index
        return index

    def add_edge(self, from_node: T, to_node: T, label: Optional[str] = None) -> int:
        """
        Adds a directed edge from one node to another.

        Args:
            from_node (T): The payload of the source node.
            to_node (T): The payload of the target node.
            label (str, optional): An optional label for the edge.
        """
        from_index = self.add_node(from_node)
        to_index = self.add_node(to_node)
        return self.graph.add_edge(from_index, to_index, label)

    def find_cycles(self) -> List[List[T]]:
        """
        Finds all cycles in the graph.

        Returns:
            List[List[T]]: A list of cycles, where each cycle is represented as a list of node payloads.
        """
        cycles = rx.simple_cycles(self.graph)
        return [[self.graph[node] for node in cycle] for cycle in cycles]

    def get_dependents(self, node: T, depth: Optional[int] = None) -> List[T]:
        """
        Retrieves all nodes that the given node depends on.

        Args:
            node (T): The payload of the node to find dependencies for.
            depth (int, optional): The maximum depth to traverse. If None, traverses all levels.

        Returns:
            List[T]: A list of payloads representing the dependencies of the node.
        """
        if node not in self.node_map:
            return []
        return self._traverse(self.graph.successor_indices, self.node_map[node], depth)

    def get_dependents_of(self, nodes: List[T], depth: Optional[int] = None) -> List[T]:
        """
        Retrieves all dependents of multiple nodes.
        Args:
            nodes (List[T]): A list of node payloads to find dependents for.
            depth (int, optional): The maximum depth to traverse. If None, traverses all levels.
        Returns:
            List[T]: A list of payloads of dependent nodes.
        """
        collected_nodes = set[T]()
        for node in nodes:
            collected_nodes = collected_nodes | set(self.get_dependents(node, depth))
        return list(collected_nodes)

    def get_dependees(self, node: T, depth: Optional[int] = None) -> List[T]:
        """
        Retrieves all dependees of a given node.

        Args:
            node (T): The payload of the node to find dependees for.
            depth (int, optional): The maximum depth to traverse. If None, traverses all levels.

        Returns:
            List[T]: A list of payloads of dependent nodes.
        """
        if node not in self.node_map:
            return []
        return self._traverse(self.graph.predecessor_indices, self.node_map[node], depth)

    def get_dependees_of(self, nodes: List[T], depth: Optional[int] = None) -> List[T]:
        """
        Retrieves all nodes that depend on the given nodes (i.e., their dependees).

        Args:
            nodes (List[T]): A list of node payloads to find dependees for.
            depth (int, optional): The maximum depth to traverse. If None, traverses all levels.

        Returns:
            List[T]: A list of payloads representing the dependees (reverse dependencies) of the given nodes.
        """
        collected_nodes: Set[T] = set()
        for node in nodes:
            collected_nodes = collected_nodes | set(self.get_dependees(node, depth))
        return list(collected_nodes)

    def _traverse(
        self, direction_fn: Callable[[int], rx.NodeIndices], start_index: int, depth: Optional[int]
    ) -> List[T]:
        """
        Traverses the graph in the specified direction (successors or predecessors) starting from a given node index.
        Args:
            direction_fn (Callable[[int], rx.NodeIndices]): A function that returns the indices of the nodes in the specified direction.
            start_index (int): The index of the starting node.
            depth (Optional[int]): The maximum depth to traverse. If None, traverses all levels.
        Returns:
            List[T]: A list of payloads of nodes reached during the traversal.
        """

        visited = set[int]()
        result = set[int]()

        def dfs(node: int, current_depth: int):
            if depth is not None and current_depth > depth:
                return
            for neighbor in direction_fn(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    result.add(neighbor)
                    dfs(neighbor, current_depth + 1)

        dfs(start_index, 1)
        return [self.graph[i] for i in result]
