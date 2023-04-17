from itertools import combinations


def to_asset_pairs(assets_list):
    pairs = []
    for a1, a2 in combinations(assets_list, 2):
        pairs.append(f'{a1}/{a2}')
        pairs.append(f'{a2}/{a1}')
    return pairs
