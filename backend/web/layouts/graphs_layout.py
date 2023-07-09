import datetime
from collections import defaultdict
from typing import List

import dash_cytoscape as cyto
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import html, dcc

from trading.common.utils import TradeNetwork
from .bars import create_trades_predictions, create_trades
from .controls import create_controls, create_step_control, create_progress_bar
from .tables import create_arbitrage_table, create_report_table


def create_graph_layout(config, session_id):
    return [
        dmc.LoadingOverlay(
            html.Div(
                create_controls(config), id='loading-controls'),
            loaderProps={'variant': 'bars', 'color': 'blue', 'size': 'xl'},
        ),

        html.Div(children=[
            # html.Div(className='row table-title', children=[
            #     dmc.Title('Progress')
            # ]),

            html.Div(className='row', children=[
                html.Div(id='simulation-progress-bar', className='column', children=[
                    create_progress_bar(0)
                ])
            ]),
        ]),

        html.Div(className='row', children=[
            html.Div(id='arbitrage-table', className='invisible', children=[
                dmc.Divider(),
                html.Div(className='row table-title', children=[
                    dmc.Title('Arbitrage Table')
                ]),
                dmc.LoadingOverlay(
                    html.Div(
                        create_arbitrage_table(), id='loading-arbitrage-table-output'),
                    loaderProps={'variant': 'bars', 'color': 'blue', 'size': 'xl'},
                )
            ]),
        ]),
        html.Div(className='row', children=[
            html.Div(id='report-table', className='invisible', children=[
                dmc.Divider(),
                html.Div(className='row table-title', children=[
                    dmc.Title('Report Table')
                ]),
                html.Div(id='report-table-output', children=[
                    create_report_table()
                ]),
            ]),
        ]),

        dmc.Divider(),

        html.Div(children=[
            html.Div(className='row table-title', children=[
                dmc.Title('Step slider')
            ]),

            html.Div(className='row', children=[
                html.Div(id='step-control', className='column', children=[
                    create_step_control()
                ]),
            ]),
        ]),

        html.Div(className='row',
                 children=[
                     html.Div(id='trading-graph',
                              className='graph-layout two-thirds column',
                              children=[
                                  create_network()
                              ]),
                     html.Div(id='bar-plots', className='graph-layout one-third column', children=[
                         html.Div(id='trades-predicted-plot', children=[
                             create_trades_predictions()
                         ]),
                         # TODO: make some space between bar plots
                         html.Div(id='trades-plot', children=[
                             create_trades()
                         ]),
                     ])
                 ]),
        html.Div(className='row', children=[
            html.Div(id='prices-plot', className='graph-layout', children=[
                create_prices()
            ]),
        ]),

        dcc.Interval(id='interval-progress', interval=1000),
        dcc.Store(data=session_id, id='session-id', storage_type='session'),

        html.Div(id='empty-output', className='invisible')
    ]


def create_network(data: TradeNetwork = None):
    if data is None:
        return None

    if len(data) == 0:
        return None

    return cyto.Cytoscape(
        id='cytoscape',
        elements=[
            *[{'data': {'id': f'{asset.symbol}_{asset.platform}', 'label': f'{asset.symbol} ({asset.platform})'}}
              for asset in data.assets_mapping],
            *[{'data': {
                'id': f'{edge.from_asset.symbol}_{edge.from_asset.platform}-{edge.to_asset.symbol}_{edge.to_asset.platform}',
                'source': f'{edge.from_asset.symbol}_{edge.from_asset.platform}',
                'target': f'{edge.to_asset.symbol}_{edge.to_asset.platform}', 'weight': round(edge.weight, 2)}} for edge
                in
                data.edges_list],
        ],
        layout={'name': 'circle'},
        style={'width': '100%', 'height': '100%'},
        stylesheet=[
            {
                'selector': 'edge',
                'style': {
                    'label': 'data(weight)'
                }
            },
            {
                'selector': '[weight < 0]',
                'style': {
                    'line-color': 'crimson',
                    'width': 5,
                }
            },
            {
                'selector': '[weight > 0]',
                'style': {
                    'line-color': 'lightgreen',
                    'width': 5,
                }
            },
            {
                'selector': 'node',
                'style': {
                    'content': 'data(label)',
                    'text-halign': 'center',
                    'text-valign': 'center',
                    # 'width': 'label',
                    # 'height': 'label',
                }
            },
            *[{
                'selector': f'#{edge.from_asset.symbol}_{edge.from_asset.platform}-{edge.to_asset.symbol}_{edge.to_asset.platform}',
                'style': {
                    'curve-style': 'bezier',
                }
            } for edge in data.edges_list]
        ]
    )


def create_prices(data: List[List[dict]] = None):
    if data is None:
        return None

    prices = defaultdict(list)
    timestamps = []

    first = True
    for period_prices in data:
        for p in period_prices:
            prices[f'{p["symbol"]} ({p["platform"]})'].append(p['price'])
        if len(period_prices) > 0:
            timestamps.append(datetime.datetime.fromtimestamp(period_prices[0]['timestamp']))

    fig = go.Figure(
        data=
        [
            go.Scatter(x=timestamps, y=price, fill='tonexty', name=k)
            for k, price in prices.items()
        ]
    )
    fig.update_yaxes(type='log')

    return dcc.Graph(
        figure=fig
    )
