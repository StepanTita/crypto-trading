import datetime
import json

import pandas as pd

from api.exchange_api import ExchangesAPI
from blockchain import Blockchain
from common.blockchain_logger import logger
from common.utils import json_keys_to_int
from common.constants import *
from exchanges.arbitrage_pairs import arbitrage_pairs
from simulation import generate
from trading.strategies import strategy_simple_triangle_generator, strategy_bellman_ford_generator, \
    strategy_between_platforms_generator


def strategy_simple_triangle(*args, **kwargs):
    return generate(strategy_simple_triangle_generator)(*args, **kwargs)


def strategy_between_platforms(*args, **kwargs):
    return generate(strategy_between_platforms_generator)(*args, **kwargs)


def strategy_bellman_ford(*args, **kwargs):
    return generate(strategy_bellman_ford_generator)(*args, **kwargs)


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
        prices_api = ExchangesAPI(exchanges_names=platforms)

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
