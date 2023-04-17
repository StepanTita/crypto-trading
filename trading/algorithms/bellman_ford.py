import numpy as np
from typing import List, Tuple
from collections import deque


def relax(from_node: int, to_node: int, weight: float, distances: List[float], prev: List[int]) -> bool:
    if distances[from_node] + weight >= distances[to_node]:
        return False
    distances[to_node] = distances[from_node] + weight
    prev[to_node] = from_node
    return True


def find_negative_cycle(adj_list: List[List[Tuple[int, float]]], source: int) -> List[int] | None:
    # Initialize distances and prev arrays. All distances but the distance to
    # the source node are infinite, distance to the source node is zero.
    nodes = len(adj_list)

    distances = [0.0 if i == source else np.inf for i in range(nodes)]
    prev = [-1 for _ in range(nodes)]

    # Relax all edges N times where N is the number of nodes.
    for i in range(nodes):
        for from_node, edges in enumerate(adj_list):
            for to_node, weight in edges:
                relax(from_node, to_node, weight, distances, prev)

    # Try to relax at least one more edge. If it's possible memorize the node,
    # otherwise return from the method.
    node = None
    found = False
    for from_node, edges in enumerate(adj_list):
        for to_node, weight in edges:
            if relax(from_node, to_node, weight, distances, prev):
                node = to_node
                found = True
                break
        if found:
            break
    if node is None:
        return None

    # Step back N times where N is the number of nodes. As a result, the node will
    # be in the loop for sure.
    for i in range(nodes):
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
