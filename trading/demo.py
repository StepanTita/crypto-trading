import datetime
import json
from itertools import combinations

import numpy as np
import pandas as pd

from algorithms.bellman_ford import find_negative_cycle
from algorithms.utils import assets_to_adj_list, nodes_to_assets
from api.exchange_api import ExchangesAPI
from asset import Asset
from blockchain import Blockchain
from blockchain_logger import logger
from common.utils import red, json_keys_to_int, green
from runner import Runner
from simulation import simulate
from constants import *
from exchanges.arbitrage_pairs import arbitrage_pairs


@simulate
def strategy_simple_triangle(blockchain, timestamp, portfolio, platform, symbols, max_trade_ratio, min_spread=0.015):
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


@simulate
def strategy_between_platforms(blockchain, timestamp, portfolio, symbols, platforms, max_trade_ratio, min_spread=0.005):
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


@simulate
def strategy_bellman_ford(blockchain, timestamp, portfolio, platforms, symbols, max_trade_ratio, min_spread=0.015):
    runner = Runner(blockchain)

    assets = [Asset(symbol, platform) for symbol in symbols for platform in platforms]

    adj_list, nodes_mapping = assets_to_adj_list(assets, timestamp, blockchain.exchanger)

    max_benefit = 0
    real_benefit = 0
    best_trade = None
    best_cycle = None

    best_start = None

    for platform in portfolio.keys():
        for symbol, value in portfolio[platform].items():
            cycle_nodes = find_negative_cycle(adj_list, nodes_mapping[f'{platform}_{symbol}'])

            if cycle_nodes is None:
                continue

            start = Asset(symbol, platform)

            assets_beneficial_trade = nodes_to_assets(cycle_nodes, assets)
            if assets_beneficial_trade[-1].symbol != start.symbol:
                assets_beneficial_trade.append(start)

            trade = value * max_trade_ratio
            result = runner.dry_run(timestamp,
                                    assets_beneficial_trade,
                                    trade)

            if trade * min_spread <= trade - result > max_benefit:
                max_benefit = trade - result

                best_trade = trade

                best_cycle = assets_beneficial_trade

                best_start = start

    if max_benefit > 0:
        result, run_timestamp, _ = runner.run(timestamp, best_cycle, best_trade)

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
    return timestamp, max_benefit, real_benefit, best_cycle


def example1(blockchain, platforms, start_timestamp, end_timestamp):
    report = strategy_simple_triangle(blockchain, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                                      step=MINUTE,
                                      portfolio={
                                          'coinbase': {
                                              'USDT': 1000,
                                          }
                                      }, platform=platforms[0], symbols=['USDT', 'BTC', 'LTC', 'ETH'],
                                      max_trade_ratio=0.5, min_spread=0.001)
    logger.info(report)
    pd.DataFrame(report).to_csv('report-triangle.csv')


def example2(blockchain, platforms, start_timestamp, end_timestamp):
    report = strategy_between_platforms(blockchain, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                                        step=MINUTE,
                                        portfolio={
                                            'binance': {
                                                'USDT': 1000,
                                                'BTC': 0.5,
                                                'LTC': 10,
                                            },
                                            'coinbase': {
                                                'USDT': 1000,
                                                'BTC': 0.5,
                                                'LTC': 10,
                                            }
                                        }, symbols=['USDT', 'BTC', 'LTC', 'ETH'], platforms=platforms,
                                        max_trade_ratio=0.5,
                                        min_spread=0.0005)
    logger.info(report)
    pd.DataFrame(report).to_csv('report-between-platforms.csv')


def example3(blockchain, platforms, start_timestamp, end_timestamp):
    report = strategy_bellman_ford(blockchain, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                                   step=HOUR, primary_granularity=HOUR, secondary_granularity=DAY, portfolio={
            'binanceus': {
                'USDT': 1000,
            },
            'bybit': {
                'USDT': 1000,
            },
            'huobi': {
                'USDT': 1000,
            }
        }, platforms=platforms, symbols=['USDT', 'BTC', 'LTC', 'ETH'], max_trade_ratio=0.5, min_spread=0.001)
    logger.info(report)
    pd.DataFrame(report).to_csv('report-bellman-ford.csv', index=False)


def main():
    prices_data = {
        'coinbase': dict(),
        'binance': dict(),
    }

    use_data = False
    if use_data:
        with open('./data/coinbase_prices.json', 'r') as f:
            prices_data['coinbase'] = json.load(f, object_hook=json_keys_to_int)

        with open('./data/binance_prices.json', 'r') as f:
            prices_data['binance'] = json.load(f, object_hook=json_keys_to_int)

    platforms = ['binanceus', 'bybit', 'huobi']  # 'binanceus', 'bybit'

    prices_api = None
    if not use_data:
        arbitrage_pairs(platforms, symbols=['BTC/USDT', 'LTC/BTC', 'ETH/BTC', 'ETH/USDT', 'LTC/USDT'])
        prices_api = ExchangesAPI(platforms)

    blockchain = Blockchain(prices_api=prices_api, fees_data=AVG_FEES, prices_data=prices_data)

    start_date = datetime.datetime.strptime('2023-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    start_timestamp = int(datetime.datetime.timestamp(start_date))

    end_date = datetime.datetime.strptime('2023-01-07 00:00:00', '%Y-%m-%d %H:%M:%S')
    end_timestamp = int(datetime.datetime.timestamp(end_date))

    # example1(blockchain, ['binance'], start_timestamp, end_timestamp)
    #
    # example2(blockchain, ['binance', 'coinbase'], start_timestamp, end_timestamp)

    example3(blockchain, platforms, start_timestamp, end_timestamp)


if __name__ == '__main__':
    main()
