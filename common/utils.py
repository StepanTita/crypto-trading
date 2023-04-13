def style(s, style):
    return style + s + '\033[0m'


def grey(s):
    return style(s, '\033[90m')


def green(s):
    return style(s, '\033[92m')


def blue(s):
    return style(s, '\033[94m')


def yellow(s):
    return style(s, '\033[93m')


def red(s):
    return style(s, '\033[91m')


def pink(s):
    return style(s, '\033[95m')


def cyan(s):
    return style(s, '\033[36m')


def bold(s):
    return style(s, '\033[1m')


def underline(s):
    return style(s, '\033[4m')


def conform_timestamp(old, new):
    if (new - old) % 60 != 0:
        return new + 60 - ((new - old) % 60)
    return new


def json_keys_to_int(x):
    if isinstance(x, dict):
        return {int(k) if k.isdigit() else k: v for k, v in x.items()}
    return x


def get_blockchain(asset):
    return {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'BNB': 'binance_smart_chain',
        'DOGE': 'doge',
        'LTC': 'litecoin',
        'USDT': 'tron',
        'RUB': 'binance_smart_chain',
        'UAH': 'binance_smart_chain',
    }[asset.symbol]
