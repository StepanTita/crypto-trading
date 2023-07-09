import datetime

import numpy as np

from trading.algorithms.bellman_ford import find_negative_cycle
from trading.algorithms.utils import assets_to_edges_list, nodes_to_assets
from trading.asset import Asset
from trading.blockchain.runner import Runner
from trading.common.blockchain_logger import logger
from trading.common.utils import *
from trading.simulation import simulate


@simulate
def strategy_bellman_ford_generator(*args,
                                    blockchain,
                                    timestamp,
                                    timespan,
                                    portfolio,
                                    platforms,
                                    symbols,
                                    assets,
                                    max_trade_ratio,
                                    min_spread=0.015,
                                    **kwargs):
    runner = Runner(blockchain)

    edges_list, nodes_mapping = assets_to_edges_list(assets, timestamp, blockchain.exchanger, timespan)

    max_benefit = 0
    real_benefit = 0
    best_trade = None
    best_cycle = None

    best_start = None

    for platform in portfolio.keys():
        for symbol, value in portfolio[platform].items():
            cycle_nodes = find_negative_cycle(edges_list, nodes_mapping[f'{platform}_{symbol}'])

            if cycle_nodes is None:
                continue

            start = Asset(symbol, platform)

            assets_beneficial_trade = nodes_to_assets(cycle_nodes, assets)
            if assets_beneficial_trade[-1].symbol != start.symbol:
                assets_beneficial_trade.append(start)

            trade = value * max_trade_ratio
            result = runner.dry_run(timestamp,
                                    assets_beneficial_trade,
                                    trade,
                                    timespan)

            if trade * min_spread <= trade - result > max_benefit:
                max_benefit = trade - result

                best_trade = trade

                best_cycle = assets_beneficial_trade

                best_start = start

    if max_benefit > 0:
        result, run_timestamp, _ = runner.run(timestamp, best_cycle, best_trade, timespan)

        if result == np.inf:
            return timestamp, 0, []

        timestamp = run_timestamp
        real_benefit = best_trade - result

        logger.info(f'{datetime.datetime.fromtimestamp(timestamp)} {best_cycle}')
        logger.info(f'Trade {best_trade}')

        if best_trade - result < 0:
            logger.info(red(f'Benefit {best_trade - result}'))
        else:
            logger.info(green(f'Benefit {best_trade - result}'))

        portfolio[best_start.platform][best_start.symbol] -= result
        portfolio[best_cycle[-1].platform][best_start.symbol] = portfolio[best_cycle[-1].platform].get(
            best_start.symbol,
            0) + best_trade
    return timestamp, max_benefit, real_benefit, best_cycle, TradeNetwork(edges_list, assets)
