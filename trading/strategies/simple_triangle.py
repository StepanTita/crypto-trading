import datetime
from itertools import combinations

import numpy as np

from trading.blockchain.asset import Asset
from trading.common.blockchain_logger import logger
from trading.common.utils import *
from trading.blockchain.runner import Runner
from trading.simulation import simulate


@simulate
def strategy_simple_triangle_generator(blockchain, timestamp, portfolio, platform, symbols, max_trade_ratio,
                                       min_spread=0.015):
    max_benefit = 0
    real_benefit = 0

    best_trade = None

    best_start = None
    best_interm = None
    best_benefiter = None

    runner = Runner(blockchain)

    for start, value in portfolio[platform].items():
        trade = value * max_trade_ratio

        for intermediater, benefiter in combinations(filter(lambda x: x != start, symbols), 2):
            result = runner.dry_run(timestamp, [Asset(start, platform),
                                                Asset(intermediater, platform),
                                                Asset(benefiter, platform)], trade)

            if trade * min_spread <= trade - result > max_benefit:
                max_benefit = trade - result

                best_trade = trade

                best_start = Asset(start, platform)
                best_interm = Asset(intermediater, platform)
                best_benefiter = Asset(benefiter, platform)

    if max_benefit > 0:
        result, run_timestamp, [time_after_first, time_after_second] = runner.run(timestamp,
                                                                                  [best_start,
                                                                                   best_interm,
                                                                                   best_benefiter],
                                                                                  best_trade)

        if result == np.inf:
            return timestamp, max_benefit, [best_start, best_interm, best_benefiter]

        timestamp = run_timestamp
        real_benefit = best_trade - result

        logger.info(f'{datetime.datetime.fromtimestamp(timestamp)} {best_start} {best_interm} {best_benefiter}')
        logger.info(f'Trade {best_trade}')
        logger.info(
            f'>>> {best_start.symbol}-{best_interm.symbol}: {blockchain.exchanger.exchange(timestamp, best_start, best_interm)}')
        logger.info(
            f'>>> {best_interm.symbol}-{best_benefiter.symbol}: {blockchain.exchanger.exchange(time_after_first, best_interm, best_benefiter)}')
        logger.info(
            f'>>> {best_benefiter.symbol}-{best_start.symbol}: {blockchain.exchanger.exchange(time_after_second, best_benefiter, best_start)}')
        if best_trade - result < 0:
            logger.info(red(f'Benefit {best_trade - result}'))
        else:
            logger.info(green(f'Benefit {best_trade - result}'))

        portfolio[platform][best_start.symbol] += best_trade - result
    return timestamp, max_benefit, real_benefit, [best_start, best_interm, best_benefiter]
