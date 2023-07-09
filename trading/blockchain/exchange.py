import datetime
from typing import Dict

import numpy as np

from trading.api.exchange_api import ExchangesAPI
from trading.asset import Asset


class Exchanger:
    def __init__(self,
                 data: Dict[str, Dict[str, Dict[str, Dict[int, float]]]] = None,
                 api: ExchangesAPI = None,
                 ):
        self.data = data
        self.api = api

    # Assets price:
    def exchange(self, timestamp: int, base_asset: Asset, quote_asset: Asset, timespan: int):
        """
        function to return the price of the quote asset in the terms of a quote asset
        for the given timestamp

        params:
        timestamp: int
        base_asset: str anyof[USDT, EUR, BTC]
        quote_asset: str anyof[USDT, EUR, BTC]
        timespan: int time interval to account for
        return: float
        """
        if base_asset.symbol == quote_asset.symbol:
            return 1.0
        if self.api is not None:
            return self.api.exchange(timestamp, base_asset, quote_asset, timespan)
        return self.data[base_asset.platform].get(base_asset.symbol, {}).get(quote_asset.symbol, {}).get(timestamp,
                                                                                                         np.inf)


def main():
    from trading.api.exchange_api import ExchangesAPI
    # binanceus, bybit, huobi
    api = ExchangesAPI(exchanges_names=['binanceus', 'bybit'])
    ex = Exchanger(api=api)

    date = datetime.datetime.strptime('2022-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    timestamp = int(datetime.datetime.timestamp(date))

    print(ex.exchange(timestamp, Asset('BTC', 'binanceus'), Asset('USDT', 'binanceus')))
    print(ex.exchange(timestamp, Asset('BTC', 'bybit'), Asset('USDT', 'bybit')))


if __name__ == '__main__':
    main()
