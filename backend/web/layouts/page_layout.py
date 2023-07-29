import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html

from backend.config import Config
from backend.web.layouts.bars import create_trades_predictions, create_trades
from backend.web.layouts.controls import create_controls, create_step_control, create_progress_bar, \
    create_only_benefit_cycle_checkbox
from backend.web.layouts.graphs import create_network, create_prices
from backend.web.layouts.tables import create_arbitrage_table, create_report_table, create_final_balances
from backend.web.pages.utils import localize


def create_page_layout(config: Config, locale: str):
    return [
        dmc.LoadingOverlay(
            html.Div(
                create_controls(config, locale), id='loading-controls'),
            loaderProps={'variant': 'bars', 'color': 'blue', 'size': 'xl'},
        ),

        html.Div(id='final-balances-container', className='invisible', children=[
            dbc.Row(children=[
                dmc.Divider(),
                dbc.Row(className='table-title', children=[
                    dmc.Title(localize(config, 'result_portfolio', locale), align='center'),
                ]),
                html.Div(id='final-balances-card-group', children=[
                    create_final_balances(),
                ])
            ]),
        ]),

        html.Div(id='progress-bar-container', className='invisible', children=[
            dbc.Row(children=[
                dbc.Col(
                    html.Div(id='simulation-progress-bar', children=[
                        create_progress_bar(0)
                    ])
                ),
            ]),
        ]),

        dbc.Row(children=[
            dbc.Col(id='arbitrage-table', className='invisible', children=[
                dmc.Divider(),
                dbc.Row(className='table-title', children=[
                    dmc.Title(localize(config, 'arbitrage_table', locale), align='center')
                ]),
                dmc.LoadingOverlay(
                    html.Div(
                        create_arbitrage_table(), id='loading-arbitrage-table-output'),
                    loaderProps={'variant': 'bars', 'color': 'blue', 'size': 'xl'},
                )
            ]),
        ]),
        dbc.Row(children=[
            dbc.Col(id='report-table', className='invisible', children=[
                dmc.Divider(),
                dbc.Row(className='table-title', children=[
                    dmc.Title([
                        localize(config, 'report_table', locale),
                    ], align='center')
                ]),
                html.Div(id='report-table-output', children=[
                    create_report_table(config, locale)
                ]),
            ]),
        ]),

        dmc.Divider(),

        html.Div(id='full-report-container', className='invisible', children=[
            dbc.Row(children=[
                dbc.Col(children=[
                    dbc.Row(className='table-title', children=[
                        dmc.Title(localize(config, 'step_slider', locale), align='center')
                    ]),

                    dbc.Row(children=[
                        dbc.Col(id='step-control', children=[
                            create_step_control()
                        ]),
                    ]),
                ]),

                dbc.Row(
                    children=[
                        dbc.Col([
                            create_only_benefit_cycle_checkbox(config, locale)
                        ], align='center')
                    ],
                    justify='center'
                ),

                dbc.Row(children=[
                    dbc.Col(
                        id='trading-graph',
                        className='graph-layout',
                        children=[
                            create_network()
                        ],
                    ),
                ]),
                dbc.Row(children=[
                    dbc.Col(
                        id='bar-plots',
                        className='graph-layout',
                        children=[
                            html.Div(id='trades-predicted-plot', children=[
                                create_trades_predictions()
                            ]),
                            # TODO: make some space between bar plots
                            html.Div(id='trades-plot', children=[
                                create_trades()
                            ]),
                        ],
                    ),
                ]),
                dbc.Row(children=[
                    html.Div(id='prices-plot', className='graph-layout', children=[
                        create_prices()
                    ]),
                ]),
            ])
        ])
        ,
    ]
