from dash import dash_table
import dash_mantine_components as dmc


def create_report_table():
    return dash_table.DataTable(
        data=[
            {'timestamp': '2023-01-01 00:00:00', 'predicted': 1, 'real': 2, 'coins': 'USDT(binance)-LTC(coinbase)'},
            {'timestamp': '2023-01-01 00:00:00', 'predicted': 2, 'real': -1,
             'coins': 'LTC(coinbase)-USDT(binance)'},
            {'timestamp': '2023-01-01 00:00:00', 'predicted': 3, 'real': 1.5,
             'coins': 'USDT(binance)-LTC(coinbase)'},
        ],
        columns=[
            {'name': 'timestamp', 'id': 'timestamp', 'type': 'datetime'},
            {'name': 'predicted', 'id': 'predicted', 'type': 'numeric'},
            {'name': 'real', 'id': 'real', 'type': 'numeric'},
            {'name': 'coins', 'id': 'coins', 'type': 'text'},
        ],
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{real} < 0',
                },
                'backgroundColor': '#FF4136',
                'color': 'white'
            },
            {
                'if': {
                    'filter_query': '{real} > 0',
                },
                'backgroundColor': 'lightgreen',
                'color': 'white'
            },
        ],
    )


def create_arbitrage_table(data=None):
    if data is None:
        return dash_table.DataTable(
            data=[
                {'symbol': 'BTC/USDT', 'binance': 'binance', 'kraken': 'kraken', 'coinbase': 'coinbase'},
                {'symbol': 'ETH/BTC', 'binance': 'binance', 'kraken': 'kraken', 'coinbase': 'coinbase'},
                {'symbol': 'ETH/BTC', 'binance': 'binance', 'kraken': 'kraken', 'coinbase': 'coinbase'},
            ],
            columns=[
                {'name': 'Symbol', 'id': 'symbol', 'type': 'text'},
                {'name': 'Binance', 'id': 'binance', 'type': 'text'},
                {'name': 'Kraken', 'id': 'kraken', 'type': 'text'},
                {'name': 'Coinbase', 'id': 'coinbase', 'type': 'text'},
            ],
        )

    columns = [
        {'name': column, 'id': column, 'type': 'text'} for column in data.keys()
    ]
    styles = [
        {
            'if': {
                'filter_query': f'{{{column}}} is blank',
                'column_id': column
            },
            'backgroundColor': '#FF4136',
            'color': 'white'
        } for column in data.keys()
    ]

    key = list(data.keys())[0]
    return dash_table.DataTable(
        data=[
            {k: v[i] for k, v in data.items()} for i in range(len(data[key]))
        ],
        columns=columns,
        style_data_conditional=styles,
    )
