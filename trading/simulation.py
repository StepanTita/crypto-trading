import copy
import datetime

from trading.common.blockchain_logger import logger
from trading.common.constants import *
from trading.common.utils import *
from .blockchain.asset import Asset


def generate(fn):
    def wrapper(*args, **kwargs):
        res = None
        for _, r, _ in fn(*args, **kwargs):
            res = r  # ignore timestamp for demo purposes we don't need it
        return res

    return wrapper


def simulate(fn):
    """
    :param fn: function should run one cycle of arbitrage trading at the given moment in time
    :return: report of the arbitrage trading for the given data
    """

    def wrapper(blockchain, start_timestamp, end_timestamp, step, portfolio,
                primary_granularity=DAY,
                secondary_granularity=WEEK,
                *args, **kwargs):
        logger.info('Running simulation...')
        report = {
            **{
                'predicted': [],
                'real': [],
                'coins': [],
                'dates': [],
            },
        }
        graphs_history = []

        total_usdt_before = 0
        for platform, wallet in portfolio.items():
            for asset, value in wallet.items():
                total_usdt_before += blockchain.exchanger.exchange(start_timestamp, Asset(asset, platform),
                                                                   Asset('USDT', platform)) * value
        logger.info(yellow(f'Total USDT before arbitrage: {total_usdt_before}'))

        def simulate_iteration():
            timestamp = start_timestamp

            secondary_granularity_data = copy.deepcopy(portfolio)

            last_secondary_timestamp = start_timestamp
            last_primary_timestamp = start_timestamp

            while timestamp < end_timestamp:
                logger.debug(yellow(f'Timestamp: {datetime.datetime.fromtimestamp(timestamp)}'))

                next_timestamp, max_benefit, real_benefit, coins, trade_network = fn(blockchain, timestamp, portfolio,
                                                                                     *args, **kwargs)
                if next_timestamp == timestamp:  # if we didn't really trade, then just go to the next period
                    next_timestamp = timestamp + step

                # Report formation:
                if max_benefit > 0:
                    report['predicted'].append(max_benefit)
                    report['real'].append(real_benefit)
                    report['coins'].append('-'.join(map(lambda x: x.symbol + f'({x.platform})', coins)))
                    report['dates'].append(datetime.datetime.fromtimestamp(timestamp))
                    for platform, wallet in portfolio.items():
                        for asset, value in wallet.items():
                            if f'{platform}_{asset}' not in report:
                                report[f'{platform}_{asset}'] = []
                                report[f'{platform}_{asset}_change'] = []
                            report[f'{platform}_{asset}'].append(value)
                            report[f'{platform}_{asset}_change'].append(
                                value - secondary_granularity_data[platform].get(asset, 0))
                    graphs_history.append(trade_network)

                if (timestamp - last_primary_timestamp) // primary_granularity >= 1:
                    logger.info(blue(underline(
                        f'{GRANULARITY_TO_NAME[primary_granularity]}: {(timestamp - start_timestamp) // primary_granularity}')))
                    last_primary_timestamp = timestamp

                if (timestamp - last_secondary_timestamp) // secondary_granularity >= 1:
                    logger.info(30 * '*')
                    logger.info(pink(underline(
                        f'{GRANULARITY_TO_NAME[secondary_granularity]} {(timestamp - start_timestamp) // secondary_granularity} start:')))

                    for platform, wallet in secondary_granularity_data.items():
                        for asset, value in wallet.items():
                            logger.info(f'> {asset} ({platform}) : {value}')
                    logger.info(pink(f'{GRANULARITY_TO_NAME[secondary_granularity]} end:'))

                    for platform, wallet in portfolio.items():
                        for asset, value in wallet.items():
                            logger.info(f'> {asset} ({platform}) : {value}')

                    logger.info('Benefit:')
                    for platform, wallet in portfolio.items():
                        for asset, value in wallet.items():
                            if float(wallet[asset]) - secondary_granularity_data[platform].get(asset, 0) > 0:
                                logger.info(green(
                                    f'> {asset} ({platform}): {float(wallet[asset]) - secondary_granularity_data[platform].get(asset, 0)}'))
                            else:
                                logger.info(
                                    yellow(
                                        f'> {asset} ({platform}): {float(wallet[asset]) - secondary_granularity_data[platform].get(asset, 0)}'))

                    secondary_granularity_data = copy.deepcopy(portfolio)
                    logger.info(30 * '*')
                    last_secondary_timestamp = timestamp

                timestamp = next_timestamp

                yield timestamp, report, graphs_history

        yield from simulate_iteration()

        total_usdt_after = 0
        for platform, wallet in portfolio.items():
            for asset, value in wallet.items():
                total_usdt_after += blockchain.exchanger.exchange(start_timestamp, Asset(asset, platform),
                                                                  Asset('USDT', platform)) * value
        logger.info(yellow(f'Total USDT after arbitrage: {total_usdt_after}'))

        if total_usdt_after - total_usdt_before < 0:
            logger.info(red(f'Negative profit: {total_usdt_after - total_usdt_before}'))
        elif total_usdt_after - total_usdt_before == 0:
            logger.info(yellow(f'No profit: {total_usdt_after - total_usdt_before}'))
        else:
            logger.info(green(f'Profit: {total_usdt_after - total_usdt_before}'))

        return end_timestamp, report, graphs_history

    return wrapper
