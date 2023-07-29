import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from dash import dash_table
from dash.dash_table.Format import Format, Scheme

from backend.web.pages.utils import localize
from trading.portfolio.portfolio import Portfolio


def create_report_table(config, locale: str, data: pd.DataFrame | None = None):
    if data is None:
        return None

    d = data.copy()

    d['date'] = data['dates'].dt.date
    d['time'] = data['dates'].dt.time

    columns = ['date', 'time', 'trades', 'predicted', 'real', 'coins']
    balance_columns = [k for k in d.columns if k.count('_') == 1]

    return dash_table.DataTable(
        data=d[columns + balance_columns].to_dict('records'),
        columns=[
            {'name': localize(config, 'dates', locale), 'id': 'date', 'type': 'string'},
            {'name': localize(config, 'times', locale), 'id': 'time', 'type': 'string'},
            {'name': localize(config, 'trades', locale), 'id': 'trades', 'type': 'numeric'},
            {'name': localize(config, 'predicted', locale), 'id': 'predicted', 'type': 'numeric',
             'format': Format(precision=4, scheme=Scheme.fixed)},
            {'name': localize(config, 'real', locale), 'id': 'real', 'type': 'numeric',
             'format': Format(precision=4, scheme=Scheme.fixed)},
            {'name': localize(config, 'coins', locale), 'id': 'coins', 'type': 'text'},
            *[{'name': (lambda x: f'{x[1]} {(x[0])}')(k.split('_')), 'id': k, 'type': 'numeric',
               'format': Format(precision=4, scheme=Scheme.fixed)} for k in
              balance_columns],
        ],
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{real} < 0',
                },
                'backgroundColor': 'rgba(255, 65, 54, 0.6)',
                'color': 'white'
            },
            {
                'if': {
                    'filter_query': '{real} > 0',
                },
                'backgroundColor': 'rgba(144, 238, 144, 0.7)',
                'color': 'white'
            },
        ],
        page_size=10,
        style_table={'overflowX': 'scroll'}
    )


def create_arbitrage_table(data: pd.DataFrame | None = None):
    if data is None:
        return None

    columns = [
        {'name': column, 'id': column, 'type': 'text'} for column in data.columns
    ]
    styles = [
        {
            'if': {
                'filter_query': f'{{{column}}} is blank',
                'column_id': column
            },
            'backgroundColor': 'rgba(255, 65, 54, 0.6)6',
            'color': 'white'
        } for column in data.columns
    ]

    return dash_table.DataTable(
        data=data.to_dict('records'),
        columns=columns,
        style_data_conditional=styles,
        page_size=10
    )


PLATFORM_TO_IMG_URL = {
    'binanceus': 'https://www.investopedia.com/thmb/F5w0M48xTFtv-VQE9GFpYDMA2-k=/fit-in/1500x750/filters:format(png):fill(white):max_bytes(150000):strip_icc()/Binance-0e4c4bfb014e4d9ca8f0b6e11c9db562.jpg',
    'okx': 'https://www.investopedia.com/thmb/yo4tmbp_U2mOosNAPO4gHQj6kcA=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/OKX-logo-d77d5bd69f694e9bab776e5d3fa7efb9.jpeg',
    'huobi': 'https://www.investopedia.com/thmb/Y68svulmwXWSxCl9vYDEJ6Psb-4=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/Huobi-0e7f0bcd84d94944bb4ae0fd921c5429.jpg',
}


def create_final_balances(curr_portfolio: Portfolio | None = None, initial_portfolio: Portfolio | None = None):
    if curr_portfolio is None:
        return None

    def choose_color(platform, coin, amount):
        if initial_portfolio.get(platform, coin, replace=0) > amount:
            return 'red'
        elif initial_portfolio.get(platform, coin, replace=0) == amount:
            return 'yellow'
        return 'green'

    return dbc.Row([
        dbc.Col([
            dmc.Card(
                children=[
                    dmc.CardSection(
                        dmc.Image(
                            src=PLATFORM_TO_IMG_URL[platform],
                            height=160,
                            withPlaceholder=True,
                            fit='contain',
                        )
                    ),
                    dbc.Stack([
                        dmc.Title(platform.title(), weight=500, align='center', order=3),
                        *[
                            dmc.Center(
                                dmc.Tooltip(
                                    label=f'{amount}',
                                    position='top',
                                    offset=3,
                                    children=[

                                        dmc.Badge(
                                            f'{round(amount, 4)} {coin}',
                                            variant='outline',
                                            color=choose_color(platform, coin, amount),
                                            size='xl',
                                        )

                                    ]
                                ),
                            ) for coin, amount in wallet.items()
                        ]
                    ], gap=2),
                ]
            )
        ], width=12, md=12 // curr_portfolio.size(), className='platform-balance') for platform, wallet in
        curr_portfolio.items()
    ])
