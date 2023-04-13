import datetime
import copy

from blockchain_logger import logger
from common.utils import *

MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY


def simulate(fn):
    """
    :param fn: function should run one cycle of arbitrage trading at the given moment in time
    :return: report of the arbitrage trading for the given data
    """

    def wrapper(blockchain, start_timestamp, end_timestamp, portfolio, *args, **kwargs):

        report = {
            **{
                'coins': [],
                'dates': [],
                'weeks': [],
            },
        }

        timestamp = start_timestamp

        week_start = copy.deepcopy(portfolio)

        last_week_timestamp = start_timestamp
        last_day_timestamp = start_timestamp
        while timestamp < end_timestamp:
            logger.debug(yellow(f'Timestamp: {datetime.datetime.fromtimestamp(timestamp)}'))

            next_timestamp = timestamp + 60
            next_timestamp, max_benefit, coins = fn(blockchain, next_timestamp, portfolio, *args, **kwargs)

            # Report formation:
            if max_benefit > 0:
                report['coins'].append('-'.join(map(lambda x: x.symbol + f'({x.platform})', coins)))
                report['weeks'].append((timestamp - start_timestamp) // WEEK)
                report['dates'].append(datetime.datetime.fromtimestamp(timestamp))
                for platform, wallet in portfolio.items():
                    for asset, value in wallet.items():
                        if f'{platform}_{asset}' not in report:
                            report[f'{platform}_{asset}'] = []
                            report[f'{platform}_{asset}_change'] = []
                        report[f'{platform}_{asset}'].append(value)
                        report[f'{platform}_{asset}_change'].append(value - week_start[platform].get(asset, 0))

            if (timestamp - last_day_timestamp) // DAY >= 1:
                logger.info(blue(underline(f'Day: {(timestamp - start_timestamp) // DAY}')))
                last_day_timestamp = timestamp

            if (timestamp - last_week_timestamp) // WEEK >= 1:
                logger.info(30 * '*')
                logger.info(pink(underline(f'Week {(timestamp - start_timestamp) // WEEK} start:')))
                for platform, wallet in week_start.items():
                    for asset, value in wallet.items():
                        logger.info(f'> {asset} : {value}')
                logger.info('Week end:')
                for asset, value in portfolio.items():
                    logger.info(f'> {asset} : {value}')

                logger.info('Benefit:')
                for platform, wallet in portfolio.items():
                    for asset, value in wallet.items():
                        if float(wallet[asset]) - week_start[platform].get(asset, 0) > 0:
                            logger.info(green(
                                f'> {platform} {asset}: {float(wallet[asset]) - week_start[platform].get(asset, 0)}'))
                        else:
                            logger.info(
                                yellow(
                                    f'> {platform} {asset}: {float(wallet[asset]) - week_start[platform].get(asset, 0)}'))

                week_start = copy.deepcopy(portfolio)
                logger.info(30 * '*')
                last_week_timestamp = timestamp

            timestamp = next_timestamp
        return report

    return wrapper
