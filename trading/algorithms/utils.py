from typing import List, Tuple, Dict

import numpy as np

from asset import Asset
from exchange import Exchanger


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
