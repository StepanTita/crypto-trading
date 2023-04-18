import dash_cytoscape as cyto
import dash_core_components as dcc
import dash_mantine_components as dmc
from dash import html

import plotly.graph_objects as go

from .controls import create_controls, create_step_control, create_progress_bar
from .tables import create_arbitrage_table, create_report_table


def create_graph_layout(config):
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
                dmc.LoadingOverlay(
                    html.Div(
                        create_report_table(), id='loading-report-table-output'),
                    loaderProps={'variant': 'bars', 'color': 'blue', 'size': 'xl'},
                )
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
        # TODO: remove if not used
        html.Div(id='empty-output'),
        dcc.Input(id='report-table-empty-output'),
        dcc.Interval(id='interval-progress', interval=1000)
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


def create_trades(data=None):
    # replace those with empty container or something
    if data is None:
        return None
    return dcc.Graph(figure=go.Figure(data=(
        go.Bar(x=data['dates'],
               y=data[''],
               base=[-500, -600, -700],
               marker_color='crimson',
               name='Losses'),
        go.Bar(x=data['dates'], y=[300, 400, 700],
               base=0,
               marker_color='seagreen',
               name='Gains'
               )
    )))


def create_trades_predictions(data=None):
    if data is None:
        return None
    return dcc.Graph(figure=go.Figure(data=(
        go.Bar(x=data['dates'],
               y=data['predicted'],
               marker_color='seagreen',
               name='Predicted'),
        go.Bar(x=data['dates'],
               y=data['real'],
               base=0,
               marker_color=['crimson' if p < 0 else 'seagreen' for p in data['real']],
               name='Actual'
               ),
    ), layout={'showlegend': False}))


def create_prices():
    return dcc.Graph(figure=go.Figure(data=(
        go.Scatter(x=[1, 2, 3, 4], y=[0, 2, 3, 5], fill='tozeroy'),
        go.Scatter(x=[1, 2, 3, 4], y=[3, 5, 1, 7], fill='tonexty'),
    )))
