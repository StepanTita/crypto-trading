import numpy as np
from typing import List
from collections import deque

from trading.algorithms.network import Edge


def relax(from_node: int, to_node: int, weight: float, distances: List[float], prev: List[int]) -> bool:
    if distances[from_node] + weight >= distances[to_node]:
        return False
    distances[to_node] = distances[from_node] + weight
    prev[to_node] = from_node
    return True


def find_negative_cycle(edges_list: List[Edge], source: int) -> List[int] | None:
    # Initialize distances and prev arrays. All distances but the distance to
    # the source node are infinite, distance to the source node is zero.
    nodes = set()
    for edge in edges_list:
        nodes.add(edge.to_node)
        nodes.add(edge.from_node)

    nodes_count = len(nodes)

    distances = [0.0 if i == source else np.inf for i in range(nodes_count)]
    prev = [-1 for _ in range(nodes_count)]

    # Relax all edges N times where N is the number of nodes.
    for i in range(nodes_count):
        for edge in edges_list:
            relax(edge.from_node, edge.to_node, edge.weight, distances, prev)

    # Try to relax at least one more edge. If it's possible memorize the node,
    # otherwise return from the method.
    node = None
    for edge in edges_list:
        if relax(edge.from_node, edge.to_node, edge.weight, distances, prev):
            node = edge.to_node
            break

    if node is None:
        return None

    # Step back N times where N is the number of nodes. As a result, the node will
    # be in the loop for sure.
    for _ in range(nodes_count):
        node = prev[node]

    # Recover the loop by the node that is inside it and prev links.
    last_node = node
    result = []
    while True:
        result.append(node)
        node = prev[node]
        if node == last_node:
            break

    # Reverse the result list and return only if the need node is in the cycle
    result.reverse()
    for i in range(len(result)):
        if result[i] == source:
            deq = deque(result)
            deq.rotate(len(result) - i)
            return list(deq)

    return None
