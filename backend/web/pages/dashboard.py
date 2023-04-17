import datetime

import dash
from dash import html, Output, Input, State
from dash.exceptions import PreventUpdate

from trading.api.exchange_api import ExchangesAPI
from trading.blockchain import Blockchain
from trading.exchanges.arbitrage_pairs import arbitrage_pairs
from trading.strategies import name_to_strategy
from .layout import html_layout

from dash_extensions.enrich import FileSystemCache, Trigger

from backend.web.layouts.graphs_layout import create_graph_layout
from backend.web.layouts.tables import create_arbitrage_table, create_report_table
from backend.utils import to_asset_pairs
from ..layouts.controls import create_controls


def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            '/static/dist/css/styles.css',
        ],
    )

    # Initialize callbacks after our app is loaded
    # Pass dash_app as a parameter
    init_callbacks(dash_app, server.config)

    dash_app.index_string = html_layout

    # Create Dash Layout
    dash_app.layout = html.Div(
        id='dash-container',
        children=create_graph_layout(server.config),
    )

    return dash_app.server


def init_callbacks(app, config):
    fsc = FileSystemCache('./cache')
    fsc.clear()
    fsc.set('report_progress', None)
    fsc.set('run_progress', None)

    @app.callback(
        [
            Output('report-progress-empty-output', 'value', allow_duplicate=True),
            Output('loading-controls', 'children')
        ],
        [
            Input('run-controls', 'n_clicks'),
            State('select-strategy-select-control', 'value'),
            State('multiselect-platforms-select-control', 'value'),
            State('use-fees-checkbox-control', 'checked'),
            State('date-range-picker-control', 'value'),
            State('multiselect-assets-select-control', 'value'),
            State('slider-max-trade-ratio-control', 'value'),
            State('slider-min-spread-control', 'value'),
            State('select-primary-granularity-select-control', 'value'),
            State('select-secondary-granularity-select-control', 'value'),
        ],
        prevent_initial_call=True
    )
    def update_report_state(n_clicks, strategy_name, platforms, use_fees, date_range, assets, max_trade_ratio,
                            min_spread,
                            primary_granularity, secondary_granularity):
        fsc.clear()
        fsc.set('report_progress', None)
        fsc.set('run_progress', None)

        prices_api = ExchangesAPI(platforms)
        # TODO: real fees and prices data
        blockchain = Blockchain(prices_api=prices_api, fees_data=None, prices_data=None,
                                disable_fees=not use_fees)

        start_date = datetime.datetime.strptime(f'{date_range[0]} 00:00:00', '%Y-%m-%d %H:%M:%S')
        start_timestamp = int(datetime.datetime.timestamp(start_date))

        end_date = datetime.datetime.strptime(f'{date_range[1]} 00:00:00', '%Y-%m-%d %H:%M:%S')
        end_timestamp = int(datetime.datetime.timestamp(end_date))

        for t, r in name_to_strategy(strategy_name)(blockchain, start_timestamp=start_timestamp,
                                                    end_timestamp=end_timestamp,
                                                    step=primary_granularity, primary_granularity=primary_granularity,
                                                    secondary_granularity=secondary_granularity,
                                                    portfolio={
                                                        'binanceus': {
                                                            'USDT': 1000,
                                                        },
                                                        'bybit': {
                                                            'USDT': 1000,
                                                        },
                                                    }, platforms=platforms, symbols=assets,
                                                    max_trade_ratio=max_trade_ratio / 100, min_spread=min_spread / 100):
            fsc.set('report_progress', r)
            fsc.set('run_progress', (t - start_timestamp) / (end_timestamp - start_timestamp) * 100)

        return None, create_controls(config)

    @app.callback(Output('report-progress-empty-output', 'value', allow_duplicate=True),
                  Trigger('interval-progress', 'n_intervals'), prevent_initial_call=True)
    def update_report_progress(n_intervals):
        value = fsc.get('report_progress')  # get progress
        if value is None:
            raise PreventUpdate
        return 'updated'

    @app.callback(Output('loading-report-table-output', 'children'), Input('report-progress-empty-output', 'value'))
    def update_report(value):
        return create_report_table(fsc.get('report_progress'))

    @app.callback([
        Output('simulation-progress-bar-control', 'value'),
        Output('simulation-progress-bar-control', 'label'),
    ],
        Trigger('interval-progress', 'n_intervals'))
    def update_run_progress(n_intervals):
        value = fsc.get('run_progress')  # get progress
        if value is None:
            raise PreventUpdate
        value = min(value, 100)
        return value, f'{round(value, 2)}%'

    @app.callback(
        Output('loading-arbitrage-table-output', 'children'),
        [
            Input('view-arbitrage-button-control', 'n_clicks'),
            Input('multiselect-assets-select-control', 'value'),
            Input('multiselect-platforms-select-control', 'value'),
        ],
    )
    def update_arbitrages(n_clicks, assets_list, platforms_select):
        if n_clicks is None:
            return create_arbitrage_table()
        return create_arbitrage_table(
            arbitrage_pairs(platforms_select, to_asset_pairs(assets_list)))
