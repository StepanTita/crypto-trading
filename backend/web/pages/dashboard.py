import datetime

import dash
import pandas as pd
from dash import html, Output, Input, State
from dash.exceptions import PreventUpdate

from trading.api.exchange_api import ExchangesAPI
from trading.blockchain import Blockchain
from trading.exchanges.arbitrage_pairs import arbitrage_pairs
from trading.strategies import name_to_strategy
from .layout import html_layout

from dash_extensions.enrich import FileSystemCache, Trigger

from backend.web.layouts.graphs_layout import create_graph_layout, create_trades_predictions
from backend.web.layouts.tables import create_arbitrage_table, create_report_table
from backend.utils import to_asset_pairs
from backend.web.layouts.controls import create_controls, create_step_control, create_progress_bar


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

    def reset_cache():
        fsc.clear()
        fsc.set('report_progress', None)
        fsc.set('run_progress', None)

    @app.callback(
        [
            Output('report-table-empty-output', 'value', allow_duplicate=True),
            Output('loading-controls', 'children'),
            Output('step-control', 'children'),
            Output('trades-predicted-plot', 'children')
        ],
        [
            Input('run-controls', 'n_clicks'),
            State('select-strategy-select-control', 'value'),
            State('multiselect-platforms-select-control', 'value'),
            State('use-fees-checkbox-control', 'checked'),
            State('date-range-picker-control', 'value'),
            State('start-timestamp-timeinput-control', 'value'),
            State('end-timestamp-timeinput-control', 'value'),
            State('multiselect-assets-select-control', 'value'),
            State('slider-max-trade-ratio-control', 'value'),
            State('slider-min-spread-control', 'value'),
            State('select-primary-granularity-select-control', 'value'),
            State('select-secondary-granularity-select-control', 'value'),
        ],
        prevent_initial_call=True
    )
    def update_report_state(n_clicks, strategy_name, platforms, use_fees, date_range, start_time, end_time, assets,
                            max_trade_ratio,
                            min_spread,
                            primary_granularity, secondary_granularity):
        reset_cache()

        prices_api = ExchangesAPI(platforms)
        # TODO: real fees and prices data
        blockchain = Blockchain(prices_api=prices_api, fees_data=None, prices_data=None,
                                disable_fees=not use_fees)

        controls_state = dict(
            strategy=strategy_name,
            platforms=platforms,
            fees_checkbox=use_fees,
            date_range=date_range,
            start_time=start_time,
            end_time=end_time,
            assets=assets,
            max_trade_ratio=max_trade_ratio,
            min_spread=min_spread,
            primary_granularity=primary_granularity,
            secondary_granularity=secondary_granularity
        )

        start_date = datetime.datetime.strptime(f'{date_range[0]} {start_time.split("T")[1]}', '%Y-%m-%d %H:%M:%S')
        start_timestamp = int(datetime.datetime.timestamp(start_date))

        end_date = datetime.datetime.strptime(f'{date_range[1]} {end_time.split("T")[1]}', '%Y-%m-%d %H:%M:%S')
        end_timestamp = int(datetime.datetime.timestamp(end_date))

        data = None
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
            data = pd.DataFrame(r)
            fsc.set('report_progress', r)
            fsc.set('run_progress', (t - start_timestamp) / (end_timestamp - start_timestamp) * 100)

        return None, \
            create_controls(config, controls_state), \
            create_step_control(data, disabled=False), \
            create_trades_predictions(data)

    @app.callback(Output('report-table-empty-output', 'value', allow_duplicate=True),
                  Trigger('interval-progress', 'n_intervals'), prevent_initial_call=True)
    def update_report_table_proxy(n_intervals):
        value = fsc.get('report_progress')  # get progress
        if value is None:
            raise PreventUpdate
        return 'updated'

    @app.callback([
        Output('loading-report-table-output', 'children'),
        Output('report-table', 'style'),
    ], Input('report-table-empty-output', 'value'))
    def update_report_table(value):
        data = fsc.get('report_progress')
        if value is None or data is None:
            raise PreventUpdate
        return create_report_table(data), {'display': 'block'}

    @app.callback(
        Output('simulation-progress-bar', 'children'),
        Trigger('interval-progress', 'n_intervals'))
    def update_run_progress(n_intervals):
        value = fsc.get('run_progress')  # get progress
        if value is None:
            # cache is only reset after we've hit 100% completion in the progress bar
            reset_cache()
            return create_progress_bar(0)
        value = min(value, 100)

        if value == 100:
            reset_cache()
        return create_progress_bar(value)

    @app.callback(
        [
            Output('loading-arbitrage-table-output', 'children'),
            Output('arbitrage-table', 'style'),
        ],
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
            arbitrage_pairs(platforms_select, to_asset_pairs(assets_list))), {'display': 'block'}
