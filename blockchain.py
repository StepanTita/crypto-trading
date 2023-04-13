import datetime

from asset import Asset
from blockchain_logger import logger
from constants import *
from exchange import Exchanger
from fees import Fees


def get_blocktime(blockchain):
    return AVG_BLOCK_TIME[blockchain]


class Blockchain:
    def __init__(self, prices_data=None, prices_api=None, fees_data=None):
        self.exchanger = Exchanger(data=prices_data, api=prices_api)
        self.fees = Fees(fees_data=fees_data, fees_api=prices_api)

    def calc_transaction(self, timestamp, base_asset, quote_asset, amount):
        logger.debug(f'Transaction amount in base asset: {base_asset.symbol}, {amount}')
        logger.debug(
            f'Transaction amount in USDT: {self.exchanger.exchange(timestamp, base_asset, Asset("USDT", base_asset.platform)) * amount} ')

        price = self.exchanger.exchange(timestamp, base_asset, quote_asset)
        platf_fees, sender_fees, receiver_fees = self.fees.calc_fees(base_asset, quote_asset, amount, price)

        total_platform_fees = 0
        for fee in platf_fees:
            if isinstance(fee, dict):
                total_platform_fees += fee['cost'] * self.exchanger.exchange(timestamp, Asset(fee['currency'],
                                                                                              quote_asset.platform),
                                                                             quote_asset)
            else:
                total_platform_fees += fee

        transaction_cost = amount * price + total_platform_fees + sender_fees * price + receiver_fees
        logger.debug(f'Transaction cost in quote asset: {quote_asset.symbol} {transaction_cost}')
        logger.debug(
            f'Transaction cost in base asset: {base_asset.symbol} {self.exchanger.exchange(timestamp, quote_asset, base_asset) * transaction_cost}')
        logger.debug(
            f'Transaction cost in USDT: {self.exchanger.exchange(timestamp, quote_asset, Asset("USDT", quote_asset.platform)) * transaction_cost}')
        logger.debug('*' * 30)
        # base amount and sender fees are in base asset
        return transaction_cost


def main():
    from api.exchange_api import ExchangesAPI
    # binanceus, bybit, huobi
    api = ExchangesAPI(['bybit', 'binanceus'])
    blockchain = Blockchain(prices_api=api, fees_data=AVG_FEES)

    date = datetime.datetime.strptime('2022-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    timestamp = int(datetime.datetime.timestamp(date))

    base_asset = Asset('USDT', 'binanceus')
    quote_asset = Asset('BTC', 'binanceus')

    cost = blockchain.calc_transaction(timestamp, base_asset, quote_asset, 250)
    print(base_asset, quote_asset, cost)

    base_asset = quote_asset
    quote_asset = Asset('BTC', 'bybit')

    cost = blockchain.calc_transaction(timestamp, base_asset, quote_asset, cost)
    print(base_asset, quote_asset, cost)

    base_asset = quote_asset
    quote_asset = Asset('USDT', 'bybit')

    cost = blockchain.calc_transaction(timestamp, base_asset, quote_asset, cost)
    print(base_asset, quote_asset, cost)


if __name__ == '__main__':
    main()
