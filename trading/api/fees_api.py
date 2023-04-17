import ccxt


class FeesAPI:
    def __init__(self, exchanges_names):
        self.exchanges = dict()
        for name in exchanges_names:
            # instantiate the exchange by id
            exchange = getattr(ccxt, name)()

            # save it in a dictionary under its id for future use
            self.exchanges[name] = exchange

    # @retry_with_exponential_backoff(ccxt_errors)
    # def calc_fees(self, pair, base_asset, quote_asset):
    #     self.exchanges[]