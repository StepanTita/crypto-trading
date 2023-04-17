import datetime

import ccxt
import numpy as np

from trading.api.utils import cached_exchanges, cached_fees, log_continue
from trading.blockchain.asset import Asset
from trading.retrier.retry import retry_with_exponential_backoff, ccxt_errors


class ExchangesAPI:
    def __init__(self, exchanges_names):
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
    def exchange(self, timestamp, base_asset, quote_asset):
        pair = f'{base_asset.symbol}/{quote_asset.symbol}'
        if pair in self.exchanges[base_asset.platform].symbols:
            ohlcv = self.exchanges[base_asset.platform].fetch_ohlcv(pair, '1m', since=int(timestamp * 1000), limit=1)
            return ohlcv[0][1]
        else:
            pair = f'{quote_asset.symbol}/{base_asset.symbol}'

        if pair in self.exchanges[base_asset.platform].symbols:
            ohlcv = self.exchanges[base_asset.platform].fetch_ohlcv(pair, '1m', since=int(timestamp * 1000), limit=1)
            return 1.0 / ohlcv[0][1]

        return np.inf

    @log_continue
    @cached_fees
    @retry_with_exponential_backoff(ccxt_errors)
    def trading_fees(self, base_asset, quote_asset, amount, price):
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
    ex = ExchangesAPI(['binanceus', 'kraken'])

    date = datetime.datetime.strptime('2022-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    timestamp = int(datetime.datetime.timestamp(date))

    print(ex.exchange(timestamp, Asset('BTC', 'binanceus'), Asset('USDT', 'binanceus')))
    for i in range(50):
        print(ex.exchange(timestamp, Asset('BTC', 'binanceus'), Asset('USDT', 'binanceus')))
    for i in range(50):
        print(ex.exchange(timestamp, Asset('USDT', 'binanceus'), Asset('BTC', 'binanceus')))
    print(ex.exchange(timestamp, Asset('KAT', 'binanceus'), Asset('BTC', 'binanceus')))
