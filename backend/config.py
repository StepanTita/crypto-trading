import os
from datetime import date

from trading_config import get_config


class Config:
    """Set Flask config variables."""

    ENV = 'development'
    TESTING = True
    DEBUG = True
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

    PLATFORMS = [
        {'value': 'binanceus', 'label': 'Binance US'},
        {'value': 'huobi', 'label': 'Huobi'},
        {'value': 'okx', 'label': 'OKX'},
        {'value': 'bybit', 'label': 'ByBit'},
    ]
    ASSETS = [
        {'value': 'BTC', 'label': 'BTC'},
        {'value': 'USDT', 'label': 'USDT'},
        {'value': 'ETH', 'label': 'ETH'},
        {'value': 'LTC', 'label': 'LTC'},
    ]

    STRATEGIES = [
        {'value': 'simple-single-platform', 'label': 'Simple Single Platform (deprecated)'},
        {'value': 'simple-multiple-platforms', 'label': 'Simple Multiple Platforms (deprecated)'},
        {'value': 'bellman-ford', 'label': 'Bellman-Ford'},
    ]

    GRANULARITIES = [
        {'value': 60, 'label': 'Minute'},
        {'value': 3600, 'label': 'Hour'},
        {'value': 24 * 3600, 'label': 'Day'},
        {'value': 7 * 24 * 3600, 'label': 'Week'}
    ]

    DATE_RANGE = {
        'min_date': date(2023, 1, 1),
        'max_date': date(2023, 4, 1)
    }

    PORTFOLIO = """{
        "binanceus": {
            "USDT": 1000
        },
        "bybit": {
            "USDT": 1000
        }
}"""

    TRADING_CONFIG = get_config(os.getenv('CONFIG'))
