import dash_cytoscape as cyto
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import html, dcc

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


def create_prices():
    return dcc.Graph(figure=go.Figure(data=(
        go.Scatter(x=[1, 2, 3, 4], y=[0, 2, 3, 5], fill='tozeroy'),
        go.Scatter(x=[1, 2, 3, 4], y=[3, 5, 1, 7], fill='tonexty'),
    )))
