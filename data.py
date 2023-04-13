import datetime
import json

import pandas as pd

from collections import defaultdict
import os


def fill_gaps(data: pd.Series):
    # start_timestamp = data.index.min()
    #
    # timestamp = start_timestamp
    # for t in data.index:
    #     while t > timestamp:
    #         data[timestamp] = data[t]
    #         timestamp += 60
    #     timestamp += 60
    return data


def prepare_data(asset1, asset2, dst, src, start_timestamp):
    src = src[src.index >= start_timestamp]
    src = src[~src.index.duplicated(keep='last')]
    dst[asset1] = {**dst[asset1], asset2: dict(fill_gaps(src['open'].astype(float)))}
    dst[asset2] = {**dst[asset2], asset1: dict(fill_gaps(1 / src['open'].astype(float)))}
    return dst


def preprocess_data_parquet(basic_path, start_timestamp, assets):
    assets_price = defaultdict(dict)
    file_names = os.listdir(f'{basic_path}')
    for file_name in file_names:
        if not file_name.endswith('.parquet'):
            continue
        asset1, asset2 = file_name.rstrip('.parquet').split('-')
        if asset1 not in assets or asset2 not in assets:
            continue
        print(f'Processing {file_name}...')
        d = pd.read_parquet(f'{basic_path}/{file_name}', engine='pyarrow')
        d.index = list(map(lambda x: int(datetime.datetime.timestamp(x)), d.index))
        assets_price = prepare_data(asset1, asset2, assets_price, d, start_timestamp)
        print(f'Processed {file_name}!')
    return assets_price


def preprocess_data_csv(basic_path, start_timestamp, assets):
    assets_price = defaultdict(dict)
    file_names = os.listdir(f'{basic_path}')
    for file_name in file_names:
        if not file_name.endswith('.csv'):
            continue
        asset1, asset2 = file_name.rstrip('.csv').split('-')
        if asset1 not in assets or asset2 not in assets:
            continue
        print(f'Processing {file_name}...')
        d = pd.read_csv(f'{basic_path}/{file_name}', index_col='time')
        d.index = list(
            map(lambda x: int(datetime.datetime.timestamp(datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))),
                d.index))
        assets_price = prepare_data(asset1, asset2, assets_price, d, start_timestamp)
        print(f'Processed {file_name}!')
    return assets_price


def main():
    base_path = './data'

    start_date = datetime.datetime.strptime('2022-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    start_timestamp = int(datetime.datetime.timestamp(start_date))

    assets = [
        'USDT',
        'BTC',
        'LTC',
        'ETH',
        # 'BNB',
        # 'RUB',
        # 'UAH',
    ]

    # print('Preparing Binance data...')
    # binance_data = preprocess_data_parquet(f'{base_path}/binance', start_timestamp, assets=assets)
    # with open(f'{base_path}/binance_prices.json', 'w') as f:
    #     json.dump(binance_data, f, indent=4)

    print('Preparing Coinbase data...')
    coinbase_data = preprocess_data_csv(f'{base_path}/coinbase', start_timestamp, assets=assets)
    with open(f'{base_path}/coinbase_prices.json', 'w') as f:
        json.dump(coinbase_data, f, indent=4)


if __name__ == '__main__':
    main()
