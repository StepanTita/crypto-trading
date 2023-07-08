import datetime
from typing import List

import ccxt
import numpy as np

from pymongo.database import Database

from trading.api.utils import cached_exchanges, cached_fees, log_continue
from trading.blockchain.asset import Asset
from trading.common.constants import MINUTE, HOUR, DAY
from trading.retrier.retry import retry_with_exponential_backoff, ccxt_errors


def timespan_to_period(timespan: int) -> str:
    if timespan == MINUTE:
        return '1m'
    elif timespan == HOUR:
        return '1h'
    elif timespan == DAY:
        return '1d'
    return '1m'


class ExchangesAPI:
    def __init__(self, db: Database = None, exchanges_names: List[str] = None):
        self.db = db
        self.exchanges = dict()
        for name in exchanges_names:
            # instantiate the exchange by id
            exchange = getattr(ccxt, name)({'enableRateLimit': True})
            exchange.load_markets()

            assert exchange.has['fetchOHLCV']

            # save it in a dictionary under its id for future use
            self.exchanges[name] = exchange

    @log_continue
    @cached_exchanges
    @retry_with_exponential_backoff(ccxt_errors)
    def exchange(self, timestamp: int, base_asset: Asset, quote_asset: Asset, timespan: int = 60):
        """
        :param timestamp: integer timestamp in seconds to retrieve the rate for
        :param base_asset:
        :param quote_asset:
        :param timespan: time period to watch for OHLCV in seconds
        :return:
        np.float exchange rate or np.inf if not found
        """

        if self.db:
            price = self.db[f'exchange_price_{base_asset.platform}'].find_one(
                {'base_asset': base_asset.symbol, 'quote_asset': quote_asset.symbol, 'timestamp': timestamp})
            if price is not None:
                return price

        pair = f'{base_asset.symbol}/{quote_asset.symbol}'
        if pair in self.exchanges[base_asset.platform].symbols:
            ohlcv = self.exchanges[base_asset.platform].fetch_ohlcv(pair, timespan_to_period(timespan),
                                                                    since=int(timestamp * 1000), limit=1)
            return ohlcv[0][1]
        else:
            pair = f'{quote_asset.symbol}/{base_asset.symbol}'

        if pair in self.exchanges[base_asset.platform].symbols:
            ohlcv = self.exchanges[base_asset.platform].fetch_ohlcv(pair, timespan_to_period(timespan),
                                                                    since=int(timestamp * 1000), limit=1)
            return 1.0 / ohlcv[0][1]

        return np.inf

    @log_continue
    @cached_fees
    @retry_with_exponential_backoff(ccxt_errors)
    def trading_fees(self, base_asset: Asset, quote_asset: Asset, amount: float, price: float):
        if base_asset.symbol == quote_asset.symbol:
            return 0
        pair = f'{base_asset.symbol}/{quote_asset.symbol}'
        if pair in self.exchanges[base_asset.platform].symbols:
            return self.exchanges[base_asset.platform].calculateFee(symbol=pair, type='market', takerOrMaker='taker',
                                                                    side='sell', amount=amount, price=price)
        else:
            pair = f'{quote_asset.symbol}/{base_asset.symbol}'
            return self.exchanges[base_asset.platform].calculateFee(symbol=pair, type='market', takerOrMaker='taker',
                                                                    side='buy', amount=1.0 / amount, price=1.0 / price)


if __name__ == '__main__':
    ex = ExchangesAPI(exchanges_names=['binanceus', 'kraken'])

    date = datetime.datetime.strptime('2022-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    timestamp = int(datetime.datetime.timestamp(date))

    print(ex.exchange(timestamp, Asset('BTC', 'binanceus'), Asset('USDT', 'binanceus')))
    for i in range(50):
        print(ex.exchange(timestamp, Asset('BTC', 'binanceus'), Asset('USDT', 'binanceus')))
    for i in range(50):
        print(ex.exchange(timestamp, Asset('USDT', 'binanceus'), Asset('BTC', 'binanceus')))
    print(ex.exchange(timestamp, Asset('KAT', 'binanceus'), Asset('BTC', 'binanceus')))
