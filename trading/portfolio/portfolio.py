import copy


class Portfolio:
    def __init__(self, portfolio: dict):
        self._portfolio = portfolio

    def _get(self, obj, *args, replace):
        if len(args) == 0:
            return obj

        if not isinstance(obj, dict):
            return replace

        if len(args) > 0:
            if args[0] in obj:
                return self._get(obj[args[0]], *args[1:], replace=replace)
            return replace

    def get(self, *args, replace):
        return self._get(self._portfolio, *args, replace=replace)

    def _set(self, obj, *args, value):
        if len(args) == 0:
            return value

        if not isinstance(obj, dict):
            return value

        obj[args[0]] = self._set(obj.get(args[0], dict()), *args[1:], value=value)
        return obj

    def set(self, *args, value):
        return self._set(self._portfolio, *args, value=value)

    def delta(self, *args, delta: float = 0):
        new_value = self.get(*args, replace=0) + delta
        return self.set(*args, value=new_value)

    def items(self):
        return self._portfolio.items()

    def clone(self):
        return Portfolio(copy.deepcopy(self._portfolio))

    def size(self):
        return len(self._portfolio)


if __name__ == '__main__':
    p = Portfolio(
        {
            'binance': {
                'USDT': 1000,
                'BTC': 1,
            },
            'bybit': {
                'LTC': 1000,
                'ETH': 100,
            }
        }
    )

    print(p.get('binance', 'USDT'))
    print(p.get('bybit', 'USDT', replace=1e40))
    print(p.get('bybit', 'ETH', replace=1e40))
    print(p.set('binance', 'ETH', value=500))
    print(p.set('bybit', 'USDT', 'low', value=1e40))
