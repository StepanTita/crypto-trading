import copy
import datetime
from typing import List

from trading.asset import Asset
from trading.blockchain import Blockchain
from trading.common.blockchain_logger import logger
from trading.common.constants import *
from trading.common.utils import *
from trading.portfolio.portfolio import Portfolio


def generate(fn):
    def wrapper(*args, **kwargs):
        res = None
        for run_res in fn(*args, **kwargs):
            res = run_res['report']  # ignore timestamp for demo purposes we don't need it
        return res

    return wrapper


def simulate(fn):
    """
    :param fn: function should run one cycle of arbitrage trading at the given moment in time
    :return: dict(
        end_timestamp: end timestamp of the step,
        prices: of the assets in USD during this cycle
        report: report of the arbitrage trading for the given data,
        graph: network graph of the arbitrage
    )
    """

    def wrapper(blockchain: Blockchain,
                start_timestamp: int,
                end_timestamp: int,
                timespan: int,
                portfolio: Portfolio,
                platforms: List[str],
                symbols: List[str],
                primary_granularity: int = DAY,
                secondary_granularity: int = WEEK,
                *args, **kwargs):
        logger.info('Running simulation...')
        report = {
            **{
                'predicted': [],
                'real': [],
                'coins': [],
                'dates': [],
                'trades': [],
            },
        }

        initial_portfolio = copy.deepcopy(portfolio)

        graphs_history = []

        total_usdt_before = 0
        for platform, wallet in portfolio.items():
            for asset, value in wallet.items():
                total_usdt_before += blockchain.exchanger.exchange(start_timestamp, Asset(asset, platform),
                                                                   Asset('USDT', platform), timespan) * value
        logger.info(yellow(f'Total USDT before arbitrage: {total_usdt_before}'))

        assets = [Asset(symbol, platform) for symbol in symbols for platform in platforms]

        prices = []

        trades_count = [0]

        def simulate_iteration():
            timestamp = start_timestamp

            # TODO: rework that to use Portfolio class
            secondary_granularity_data = portfolio.clone()

            last_secondary_timestamp = start_timestamp
            last_primary_timestamp = start_timestamp

            while timestamp < end_timestamp:
                logger.debug(yellow(f'Timestamp: {datetime.datetime.fromtimestamp(timestamp)}'))

                prices.append([{
                    'timestamp': timestamp,
                    'symbol': asset.symbol,
                    'platform': asset.platform,
                    'price': blockchain.exchanger.exchange(
                        timestamp,
                        asset,
                        Asset('USDT', asset.platform),
                        timespan
                    )
                } for asset in assets])

                next_timestamp, max_benefit, real_benefit, coins, trade_network = fn(*args,
                                                                                     blockchain=blockchain,
                                                                                     timespan=timespan,
                                                                                     timestamp=timestamp,
                                                                                     portfolio=portfolio,
                                                                                     platforms=platforms,
                                                                                     symbols=symbols,
                                                                                     assets=assets,
                                                                                     **kwargs)
                if next_timestamp == timestamp:  # if we didn't really trade, then just go to the next period
                    next_timestamp = timestamp + timespan

                # Report formation:
                if max_benefit > 0:
                    trades_count[0] += 1

                    report['predicted'].append(max_benefit)
                    report['real'].append(real_benefit)
                    report['coins'].append('-'.join(map(lambda x: x.symbol + f'({x.platform})', coins)))
                    report['dates'].append(datetime.datetime.fromtimestamp(timestamp))
                    report['trades'].append(trades_count[0])

                    for platform in platforms:
                        for symbol in symbols:
                            if f'{platform}_{symbol}' not in report:
                                report[f'{platform}_{symbol}'] = []
                                report[f'{platform}_{symbol}_change'] = []

                            value = portfolio.get(platform, symbol, replace=0)
                            report[f'{platform}_{symbol}'].append(value)
                            report[f'{platform}_{symbol}_change'].append(
                                value - secondary_granularity_data.get(platform, symbol, replace=0))

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
                            if float(wallet[asset]) - secondary_granularity_data.get(platform, asset, replace=0) > 0:
                                logger.info(green(
                                    f'> {asset} ({platform}): {float(wallet[asset]) - secondary_granularity_data.get(platform, asset, replace=0)}'))
                            else:
                                logger.info(
                                    yellow(
                                        f'> {asset} ({platform}): {float(wallet[asset]) - secondary_granularity_data.get(platform, asset, replace=0)}'))

                    secondary_granularity_data = portfolio.clone()
                    logger.info(30 * '*')
                    last_secondary_timestamp = timestamp

                timestamp = next_timestamp

                yield {
                    'end_timestamp': timestamp,
                    'prices': prices,
                    'report': report,
                    'graphs_history': graphs_history,
                    'initial_portfolio': initial_portfolio,
                    'curr_portfolio': portfolio,
                }

        yield from simulate_iteration()

        total_usdt_after = 0
        for platform, wallet in portfolio.items():
            for asset, value in wallet.items():
                total_usdt_after += blockchain.exchanger.exchange(start_timestamp, Asset(asset, platform),
                                                                  Asset('USDT', platform), timespan) * value
        logger.info(yellow(f'Total USDT after arbitrage: {total_usdt_after}'))

        if total_usdt_after - total_usdt_before < 0:
            logger.info(red(f'Negative profit: {total_usdt_after - total_usdt_before}'))
        elif total_usdt_after - total_usdt_before == 0:
            logger.info(yellow(f'No profit: {total_usdt_after - total_usdt_before}'))
        else:
            logger.info(green(f'Profit: {total_usdt_after - total_usdt_before}'))

        return {
            'end_timestamp': end_timestamp,
            'prices': prices,
            'report': report,
            'graphs_history': graphs_history,
            'initial_portfolio': initial_portfolio,
            'curr_portfolio': portfolio,
        }

    return wrapper
