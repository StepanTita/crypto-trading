from dash import dash_table, html
import dash_mantine_components as dmc
from dash.dash_table.Format import Format, Scheme


def create_report_table(data=None):
    if data is None:
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

    key = list(data.keys())[0]

    columns = ['dates', 'predicted', 'real', 'coins']
    balance_columns = [k for k in data.keys() if k.count('_') == 1]

    # {'dates': '2023-01-01 00:00:00', 'predicted': 3, 'real': 1.5,
    #  'coins': 'USDT(binance)-LTC(coinbase)'},
    # *[]
    return dash_table.DataTable(
        data=[
            {k: data[k][i] for k in [*columns, *balance_columns]} for i in range(len(data[key]))
        ],
        columns=[
            {'name': 'dates', 'id': 'dates', 'type': 'datetime'},
            {'name': 'predicted', 'id': 'predicted', 'type': 'numeric',
             'format': Format(precision=4, scheme=Scheme.fixed)},
            {'name': 'real', 'id': 'real', 'type': 'numeric', 'format': Format(precision=4, scheme=Scheme.fixed)},
            {'name': 'coins', 'id': 'coins', 'type': 'text'},
            *[{'name': (lambda x: f'{x[1]} {(x[0])}')(k.split('_')), 'id': k, 'type': 'numeric',
               'format': Format(precision=4, scheme=Scheme.fixed)} for k in
              balance_columns],
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
        page_size=10,
        style_table={'overflowX': 'scroll'}
    )


def create_arbitrage_table(data=None):
    if data is None:
        return html.Div(children=[dash_table.DataTable(
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
        )], style={'overflow-x': 'scroll'})

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
    return html.Div(children=[dash_table.DataTable(
        data=[
            {k: v[i] for k, v in data.items()} for i in range(len(data[key]))
        ],
        columns=columns,
        style_data_conditional=styles,
        page_size=10
    )])
