from itertools import combinations


def to_asset_pairs(assets_list):
    pairs = []
    for a1, a2 in combinations(assets_list, 2):
        pairs.append(f'{a1}/{a2}')
        pairs.append(f'{a2}/{a1}')
    return pairs


def to_controls_state_dict(*args):
    return dict(
        portfolio_platforms=args[0],
        portfolio_asset=args[1],
        portfolio_amount=args[2],
        strategy_name=args[3],
        platforms=args[4],
        fees_checkbox=args[5],
        date_range=args[6],
        start_time=args[7],
        end_time=args[8],
        assets=args[9],
        max_trade_ratio=args[10],
        min_spread=args[11],
        primary_granularity=args[12],
        secondary_granularity=args[13]
    )
