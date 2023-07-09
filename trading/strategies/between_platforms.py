import datetime

import numpy as np

from trading.asset import Asset
from trading.blockchain.runner import Runner
from trading.common.blockchain_logger import logger
from trading.common.utils import *
from trading.simulation import simulate


# DEPRECATED: This is method might not be compatible with current simulation interface
@simulate
def strategy_between_platforms_generator(*args,
                                         blockchain,
                                         timestamp,
                                         timespan,
                                         portfolio,
                                         symbols,
                                         platforms,
                                         max_trade_ratio,
                                         min_spread=0.005,
                                         **kwargs):
    max_benefit = 0
    real_benefit = 0

    best_trade = None

    best_from = None
    best_to = None

    runner = Runner(blockchain)

    for platformFrom in platforms:
        for platformTo in platforms:
            if platformFrom == platformTo:
                continue

            for symbolFrom, value in portfolio[platformFrom].items():
                for symbolTo in symbols:
                    if symbolFrom == symbolTo:
                        continue

                    trade = value * max_trade_ratio

                    result = runner.dry_run(timestamp,
                                            [Asset(symbolFrom, platformFrom),
                                             Asset(symbolTo, platformFrom),
                                             Asset(symbolTo, platformTo),
                                             Asset(symbolFrom, platformTo)], trade)

                    if trade * min_spread <= trade - result > max_benefit:
                        max_benefit = trade - result

                        best_trade = trade

                        best_from = Asset(symbolFrom, platformFrom)
                        best_to = Asset(symbolTo, platformTo)

    if max_benefit > 0:
        result, run_timestamp, _ = runner.run(timestamp,
                                              [best_from,
                                               Asset(best_to.symbol, best_from.platform),
                                               best_to,
                                               Asset(best_from.symbol, best_to.platform)],
                                              best_trade)

        if result == np.inf:
            return timestamp, max_benefit, [best_from, best_to]

        timestamp = run_timestamp
        real_benefit = best_trade - result

        logger.info(f'{datetime.datetime.fromtimestamp(timestamp)} {best_from} {best_to}')
        logger.info(f'Trade {best_trade}')
        logger.info(f'>>> {best_from}: {blockchain.exchanger.exchange(timestamp, best_from, best_to)}')
        if best_trade - result < 0:
            logger.info(red(f'Benefit {best_trade - result}'))
        else:
            logger.info(green(f'Benefit {best_trade - result}'))

        portfolio[best_from.platform][best_from.symbol] -= result
        portfolio[best_to.platform][best_from.symbol] = portfolio[best_to.platform].get(best_from.symbol,
                                                                                        0) + best_trade
    return timestamp, max_benefit, real_benefit, [best_from, best_to]
