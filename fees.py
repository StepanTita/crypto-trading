from common.utils import get_blockchain


class Fees:
    def __init__(self, fees_data=None, fees_api=None):
        self.fees_data = fees_data
        self.fees_api = fees_api

    def calc_fees(self, base_asset, quote_asset, amount, price):
        # some exchanges might return the result not in terms of the quote asset, then we should force it
        if self.fees_api is not None:
            platform_fee = self.fees_api.trading_fees(base_asset, quote_asset, amount, price)
        else:
            platform_fee = self.fees_data['relative']['trading'][f'{base_asset.platform}-fee'] * amount * price
        sender_fee = self.fees_data['absolute']['transaction'][f'{get_blockchain(base_asset)}-fee']
        receiver_fee = self.fees_data['absolute']['transaction'][f'{get_blockchain(quote_asset)}-fee']

        if base_asset.platform != quote_asset.platform:
            return ([
                        platform_fee,
                        self.fees_data['absolute']['withdrawal'].get(
                            f'{base_asset.platform}-{get_blockchain(base_asset)}-fee', 0),
                        self.fees_data['absolute']['deposit'].get(
                            f'{base_asset.platform}-{get_blockchain(quote_asset)}-fee', 0)],
                    sender_fee,
                    receiver_fee)

        return [platform_fee], sender_fee, receiver_fee


def main():
    from api.exchange_api import ExchangesAPI
    # binanceus, bybit, huobi, gemini
    api = ExchangesAPI(['gemini'])

    from constants import AVG_FEES
    fees = Fees(fees_data=AVG_FEES, fees_api=api)

    import datetime
    date = datetime.datetime.strptime('2022-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    timestamp = int(datetime.datetime.timestamp(date))

    from asset import Asset
    base_asset = Asset('BTC', 'gemini')
    quote_asset = Asset('USDT', 'gemini')

    price = api.exchange(timestamp, base_asset, quote_asset)

    print(fees.calc_fees(base_asset, quote_asset, 1, price))


if __name__ == '__main__':
    main()
