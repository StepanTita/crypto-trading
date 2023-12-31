import datetime
import os
from typing import List

import numpy as np
from pymongo import MongoClient
from pymongo.database import Database

from trading.api.exchange_api import ExchangesAPI
from trading.asset import Asset
from trading.common.blockchain_logger import logger
from trading.common.utils import yellow, pink
from trading_config.config import get_config

MINUTE = 60
HOUR = MINUTE * 60


def load_exchange(db: Database, ex: ExchangesAPI, symbols: List[str], platforms: List[str], start_timestamp: int,
                  end_timestamp: int,
                  timestep: int):
    for platform in platforms:
        logger.info(yellow(f'Running platform: {platform}'))
        for symbol in symbols:
            logger.info(pink(f'Running symbol: {symbol}'))
            curr_timestamp = start_timestamp

            while curr_timestamp <= end_timestamp:
                logger.debug(f'Running timestamp: {datetime.datetime.fromtimestamp(curr_timestamp)}')

                base_asset = Asset(symbol.split('/')[0], platform)
                quote_asset = Asset(symbol.split('/')[1], platform)

                price = ex.exchange(curr_timestamp, base_asset, quote_asset, timestep)

                if price == np.inf:
                    logger.warning(
                        f'Price is unknown: {base_asset}:{quote_asset}. Platform: {platform}. Timestamp: {datetime.datetime.fromtimestamp(curr_timestamp)}')

                db[f'exchange_price_{platform}'].insert_one({
                    'base_asset': base_asset.symbol,
                    'quote_asset': quote_asset.symbol,
                    'timestamp': curr_timestamp,
                    'timespan': timestep,
                    'price': price,
                })

                curr_timestamp += timestep


def main():
    cfg = get_config(os.getenv('CONFIG'))

    platforms = [platform.replace('_', '') for platform in cfg['platforms']]

    client = MongoClient(cfg['database']['host'], cfg['database']['port'])

    start_date = datetime.datetime.strptime(cfg['period']['from'], '%Y-%m-%d %H:%M:%S')
    start_timestamp = int(datetime.datetime.timestamp(start_date))

    end_date = datetime.datetime.strptime(cfg['period']['to'], '%Y-%m-%d %H:%M:%S')
    end_timestamp = int(datetime.datetime.timestamp(end_date))

    ex = ExchangesAPI(exchanges_names=platforms)

    db = client['crypto_exchanges']

    load_exchange(db, ex, cfg['symbols'], platforms, start_timestamp,
                  end_timestamp, HOUR)


if __name__ == '__main__':
    main()
