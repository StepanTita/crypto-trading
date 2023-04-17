import dash_cytoscape as cyto
import dash_core_components as dcc
import dash_mantine_components as dmc
from dash import html

import plotly.graph_objects as go

from .controls import create_controls, create_step_control
from .tables import create_arbitrage_table, create_report_table


# TODO: add arbitrable pairs table
def create_graph_layout():
    return [
        create_controls(),
        html.Div(className='row', children=[
            html.Div(id='arbitrage-table', children=[
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
            html.Div(id='report-table', children=[
                dmc.Divider(),
                html.Div(className='row table-title', children=[
                    dmc.Title('Report Table')
                ]),
                dmc.LoadingOverlay(
                    html.Div(
                        create_report_table(), id='loading-report-table-output'),
                    loaderProps={'variant': 'bars', 'color': 'blue', 'size': 'xl'},
                )
            ]),
        ]),

        dmc.Divider(),

        html.Div(className='row table-title', children=[
            dmc.Title('Step slider')
        ]),

        html.Div(className='row', children=[
            html.Div(id='step-control', className='column', children=[
                create_step_control()
            ])
        ]),

        html.Div(className='row',
                 children=[
                     html.Div(id='trading-graph',
                              className='graph-layout two-thirds column',
                              children=[
                                  create_network()
                              ]),
                     html.Div(id='trades-plot', className='graph-layout one-third column', children=[
                         create_trades()
                     ]),
                 ]),
        html.Div(className='row', children=[
            html.Div(id='prices-plot', className='graph-layout', children=[
                create_prices()
            ]),
        ])
    ]


def create_network():
    return cyto.Cytoscape(
        id='cytoscape',
        elements=[
            {'data': {'id': 'BTC', 'label': 'BTC'}},
            {'data': {'id': 'ETH', 'label': 'ETH'}},
            {'data': {'id': 'USDT', 'label': 'USDT'}},
            {'data': {'source': 'BTC', 'target': 'ETH', 'weight': 1}},
            {'data': {'source': 'ETH', 'target': 'USDT', 'weight': 2}},
            {'data': {'source': 'USDT', 'target': 'BTC', 'weight': 3}},
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
                'selector': '[weight <= 1]',
                'style': {
                    'line-color': 'red',
                    'width': 5,
                }
            }
        ]
    )


def create_trades():
    return dcc.Graph(figure=go.Figure(data=(
        go.Bar(x=['2016', '2017', '2018'],
               y=[500, 600, 700],
               base=[-500, -600, -700],
               marker_color='crimson',
               name='expenses'),
        go.Bar(x=['2016', '2017', '2018'], y=[300, 400, 700],
               base=0,
               marker_color='seagreen',
               name='revenue'
               )
    )))


def create_prices():
    return dcc.Graph(figure=go.Figure(data=(
        go.Scatter(x=[1, 2, 3, 4], y=[0, 2, 3, 5], fill='tozeroy'),
        go.Scatter(x=[1, 2, 3, 4], y=[3, 5, 1, 7], fill='tonexty'),
    )))
