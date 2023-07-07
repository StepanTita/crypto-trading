from typing import List, Tuple, Dict

import numpy as np

from trading.blockchain.asset import Asset
from trading.blockchain.exchange import Exchanger


def assets_to_adj_list(assets: List[Asset], timestamp: int, exchanger: Exchanger) -> Tuple[
    List[List[Tuple[int, float]]],
    Dict[str, int]
]:
    adj_list = [[] for _ in range(len(assets))]
    nodes_mapping = dict()
    for from_node, from_asset in enumerate(assets):
        nodes_mapping[f'{from_asset.platform}_{from_asset.symbol}'] = from_node
        for to_node, to_asset in enumerate(assets):
            if from_node == to_node:
                continue
            if from_asset.platform != to_asset.platform and from_asset.symbol != to_asset.symbol:
                continue
            adj_list[from_node].append((to_node, np.log(exchanger.exchange(timestamp, from_asset, to_asset))))

    return adj_list, nodes_mapping


def nodes_to_assets(nodes: List[int], assets: List[Asset]) -> List[Asset]:
    result = []
    for node in nodes:
        result.append(assets[node])
    return result


# TODO URGENT: rework algo to edge list everywhere
def adj_list_to_edges_list(adj_list: List[List[Tuple[int, float]]], assets: List[Asset]) -> List[
    Tuple[Asset, Asset, float]]:
    edges_list = []
    for node_from in range(len(adj_list)):
        for node_to, weight in adj_list[node_from]:
            edges_list.append((assets[node_from], assets[node_to], weight))
    return edges_list
