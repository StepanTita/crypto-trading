from itertools import combinations


def to_asset_pairs(assets_list):
    pairs = []
    for a1, a2 in combinations(assets_list, 2):
        pairs.append(f'{a1}/{a2}')
        pairs.append(f'{a2}/{a1}')
    return pairs


def to_controls_state_dict(*args):
    return dict(
        strategy_name=args[0],
        platforms=args[1],
        fees_checkbox=args[2],
        date_range=args[3],
        start_time=args[4],
        end_time=args[5],
        assets=args[6],
        max_trade_ratio=args[7],
        min_spread=args[8],
        primary_granularity=args[9],
        secondary_granularity=args[10]
    )
