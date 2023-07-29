import os
from datetime import datetime

from localization.localization import get_localization
from trading_config import get_config


class Config:
    """Set Flask config variables."""

    ENV = 'development'
    TESTING = True
    DEBUG = True
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

    LOCALES = [
        {'value': 'en', 'label': 'English'},
        {'value': 'ru', 'label': 'Русский'},
    ]

    TRADING_CONFIG = get_config(os.getenv('CONFIG'))

    PLATFORMS = [
        {'value': platform.replace('_', ''), 'label': platform.replace('_', '').title()}
        for platform in TRADING_CONFIG['platforms']
    ]
    ASSETS = [
        {'value': symbol, 'label': symbol}
        for symbol in set(
            list(map(lambda x: x.split('/')[0], TRADING_CONFIG['symbols'])) +
            list(map(lambda x: x.split('/')[1], TRADING_CONFIG['symbols'])))
    ]

    STRATEGIES = [
        {'value': 'bellman-ford', 'label': 'Bellman-Ford'},
    ]

    GRANULARITIES = [
        # {'value': 60, 'label': 'Minute'},
        {'value': 3600, 'label': 'Hour'},
        {'value': 24 * 3600, 'label': 'Day'},
        {'value': 7 * 24 * 3600, 'label': 'Week'}
    ]

    DATE_RANGE = {
        'min_date': datetime.fromisoformat(TRADING_CONFIG['period']['from']).date(),
        'max_date': datetime.fromisoformat(TRADING_CONFIG['period']['to']).date()
    }

    PORTFOLIO_AMOUNT = 1000

    LOCALIZATION = get_localization(os.getenv('LOCALE'))
