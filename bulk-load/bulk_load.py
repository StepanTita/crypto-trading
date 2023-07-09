import datetime
from typing import List

import numpy as np
from pymongo import MongoClient
from pymongo.database import Database

import trading_config
from trading.api.exchange_api import ExchangesAPI
from trading.asset import Asset
from trading.common.blockchain_logger import logger
from trading.common.utils import yellow, pink

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
    cfg = trading_config.get_config('./config.local.yaml')

    client = MongoClient(cfg['database']['host'], cfg['database']['port'])

    start_date = datetime.datetime.strptime('2023-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    start_timestamp = int(datetime.datetime.timestamp(start_date))

    end_date = datetime.datetime.strptime('2023-01-01 00:01:00', '%Y-%m-%d %H:%M:%S')
    end_timestamp = int(datetime.datetime.timestamp(end_date))

    ex = ExchangesAPI(exchanges_names=cfg['platforms'])

    db = client['crypto_exchanges']

    load_exchange(db, ex, cfg['symbols'], cfg['platforms'], start_timestamp, end_timestamp, HOUR)


if __name__ == '__main__':
    main()
