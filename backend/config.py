class Config:
    """Set Flask config variables."""

    FLASK_ENV = 'development'
    TESTING = True
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

    PLATFORMS = [
        {'value': 'binanceus', 'label': 'Binance US'},
        {'value': 'binance', 'label': 'Binance'},
        {'value': 'coinbase', 'label': 'Coinbase'},
        {'value': 'bybit', 'label': 'ByBit'},
        {'value': 'kraken', 'label': 'Kraken'},
    ]
    ASSETS = [
        {'value': 'BTC', 'label': 'BTC'},
        {'value': 'USDT', 'label': 'USDT'},
        {'value': 'ETH', 'label': 'ETH'},
        {'value': 'LTC', 'label': 'LTC'},
        {'value': 'DOGE', 'label': 'DOGE'},
    ]

    STRATEGIES = [
        {'value': 'simple-single-platform', 'label': 'Simple Single Platform'},
        {'value': 'simple-multiple-platforms', 'label': 'Simple Multiple Platforms'},
        {'value': 'bellman-ford', 'label': 'Bellman-Ford'},
    ]

    GRANULARITIES = [
        {'value': 60, 'label': 'Minute'},
        {'value': 3600, 'label': 'Hour'},
        {'value': 24 * 3600, 'label': 'Day'},
        {'value': 7 * 24 * 3600, 'label': 'Week'}
    ]
