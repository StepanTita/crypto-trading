import datetime
import uuid
from typing import List, Tuple

import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html, Output, Input, State, dcc
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import FileSystemStore, Trigger

from backend import data
from backend.utils import to_asset_pairs
from backend.web.layouts.bars import create_trades
from backend.web.layouts.controls import create_controls, create_step_control, create_progress_bar
from backend.web.layouts.page_layout import create_page_layout, create_trades_predictions, create_network, \
    create_prices
from backend.web.layouts.tables import create_arbitrage_table, create_report_table, create_final_balances
from backend.web.pages.utils import is_empty, controller_error, localize, last, to_dataframe
from trading.api.exchange_api import ExchangesAPI
from trading.blockchain import Blockchain
from trading.common.constants import AVG_FEES
from trading.exchanges.arbitrage_pairs import arbitrage_pairs
from trading.portfolio.portfolio import Portfolio
from trading.strategies import name_to_strategy


def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        title='Crypto Arbitrage Analytics Bot',
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            '/static/dist/css/styles.css',
            dbc.themes.BOOTSTRAP,
        ],
    )

    # Initialize callbacks after our app is loaded
    # Pass dash_app as a parameter
    init_callbacks(dash_app, server.config)

    data.init_client(server.config.get('TRADING_CONFIG'))

    # dash_app.index_string = html_layout

    def serve_layout():
        session_id = str(uuid.uuid4())
        return html.Div(
            children=[
                dbc.Navbar(
                    [
                        dbc.NavbarBrand(
                            [
                                html.A(
                                    [
                                        html.Img(src="/static/img/logo.png",
                                                 className='logo'),
                                        "Crypto Trading Arbitrage Bot",
                                    ],
                                    href="/"
                                ),
                            ],
                            className="navbar-brand"
                        ),
                        dbc.Row([
                            dbc.Col(
                                dmc.Select(
                                    id='select-locale-control',
                                    value='en',
                                    data=server.config['LOCALES']
                                ),
                                width=8, md=10,
                            )
                        ], align='end', justify='end'),
                    ],
                    color='light',
                    dark=False,
                    sticky='top',
                    className='nav-wrapper',
                    style={'width': '100%'}
                ),
                dbc.Container(id='main', children=create_page_layout(server.config,
                                                                     locale='en')),

                dcc.Interval(id='interval-progress', interval=1000),
                dcc.Store(data=session_id, id='session-id', storage_type='session'),
                dcc.Store(data=None, id='error-state', storage_type='memory'),
                dcc.Store(data=None, id='locale-state', storage_type='session'),
                dcc.Store(data=None, id='run-state', storage_type='memory'),

                html.Div(id='empty-output', className='invisible')
            ],
        )

    # Create Dash Layout
    dash_app.layout = serve_layout

    return dash_app.server


def init_callbacks(app, config):
    EMPTY_CLASS = ''

    controls_state = [
        State('multiselect-portfolio-control', 'value'),
        State('select-portfolio-asset-control', 'value'),
        State('number-input-portfolio-amount', 'value'),
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
        State('select-secondary-granularity-select-control', 'value')
    ]

    def reset_cache(fsc):
        graphs_history = fsc.get('graphs_history')
        fsc.clear()
        fsc.set('report_table', None)
        fsc.set('run_progress', None)
        fsc.set('graphs_history', graphs_history)

    @app.callback(
        Output('locale-state', 'data'),
        [
            Input('select-locale-control', 'value'),
            State('session-id', 'data')
        ]
    )
    def update_locale_state(locale: str, session_id: str):
        return locale

    @app.callback(
        Output('main', 'children'),
        [
            Input('locale-state', 'data'),
            State('session-id', 'data')
        ]
    )
    def update_locale(locale: str, session_id: str):
        return create_page_layout(config, locale)

    @app.callback(Output('empty-output', 'children'), Input('session-id', 'data'))
    def on_page_load(session_id):
        fsc = FileSystemStore(f'./cache/{session_id}')
        reset_cache(fsc)
        raise PreventUpdate

    @app.callback(
        [
            Output('multiselect-portfolio-control', 'error'),
            Output('select-portfolio-asset-control', 'error'),
            Output('number-input-portfolio-amount', 'error'),
            Output('select-strategy-select-control', 'error'),
            Output('multiselect-platforms-select-control', 'error'),
            Output('use-fees-checkbox-control', 'error'),
            Output('date-range-picker-control', 'error'),
            Output('start-timestamp-timeinput-control', 'error'),
            Output('end-timestamp-timeinput-control', 'error'),
            Output('multiselect-assets-select-control', 'error'),
            Output('slider-max-trade-ratio-control', 'error'),
            Output('slider-min-spread-control', 'error'),
            Output('select-primary-granularity-select-control', 'error'),
            Output('select-secondary-granularity-select-control', 'error'),

            # State:
            Output('full-report-container', 'className'),
            Output('final-balances-container', 'className'),
            Output('progress-bar-container', 'className'),
            Output('run-state', 'data', allow_duplicate=True),
            # Errors:
            Output('errors-container', 'children', allow_duplicate=True),
            Output('errors-section', 'className', allow_duplicate=True),
            Output('error-state', 'data'),
        ],
        [
            Input('run-button-control', 'n_clicks'),
            *controls_state,
            State('locale-state', 'data'),
            State('session-id', 'data')
        ],
        prevent_initial_call=True
    )
    def validate_controls(
            run_n_clicks,
            portfolio_platforms: List[str],
            portfolio_asset: str,
            initial_portfolio_amount: float,
            strategy_name: str,
            platforms: List[str],
            use_fees: bool,
            date_range: Tuple[str],
            start_time: str,
            end_time: str,
            assets: List[str],
            max_trade_ratio: float,
            min_spread: float,
            primary_granularity: int,
            secondary_granularity: int,
            locale: str,
            session_id: str
    ):
        if run_n_clicks is None:
            raise PreventUpdate

        controls_state = dict(
            portfolio_platforms=portfolio_platforms,
            portfolio_asset=portfolio_asset,
            initial_portfolio_amount=initial_portfolio_amount,
            strategy_name=strategy_name,
            platforms=platforms,
            fees_estimation=use_fees,
            date_range=date_range,
            start_time=start_time,
            end_time=end_time,
            assets=assets,
            max_trade_ratio=max_trade_ratio,
            min_spread=min_spread,
            primary_granularity=primary_granularity,
            secondary_granularity=secondary_granularity
        )

        errs = valid_input(config, controls_state, locale)
        field_updates = ['' if err is None else err['message'] for err in errs]

        if any(map(lambda x: x is not None, errs)):
            return field_updates + ['invisible', 'invisible', 'invisible'] + [None] + [dbc.Accordion([
                dbc.AccordionItem(children=
                [
                    html.Div(err['message'], style={'color': 'crimson', 'font-family': 'courier'})
                ],
                    style={'color': 'crimson'},
                    title=err['field'],
                )
                for err in errs if err is not None
            ])] + [EMPTY_CLASS] + [['error']]

        # field updates + report visibility + run state + errors cards + errors cards visibility + error-state which triggers run callback
        return field_updates + [EMPTY_CLASS, EMPTY_CLASS, EMPTY_CLASS] + ['running'] + [None] + [EMPTY_CLASS] + [None]

    @app.callback(
        [
            Output('loading-controls', 'children', allow_duplicate=True),
            Output('step-control', 'children', allow_duplicate=True),
            Output('trades-predicted-plot', 'children', allow_duplicate=True),
            Output('trades-plot', 'children', allow_duplicate=True),
            Output('trading-graph', 'children', allow_duplicate=True),
            Output('prices-plot', 'children', allow_duplicate=True),
            Output('final-balances-card-group', 'children', allow_duplicate=True),
            # State
            Output('run-state', 'data', allow_duplicate=True),
            # Errors:
            Output('errors-container', 'children', allow_duplicate=True),
            Output('errors-section', 'className', allow_duplicate=True),
        ],
        [
            Input('error-state', 'data'),
            State('run-button-control', 'n_clicks'),
            *controls_state,
            State('locale-state', 'data'),
            State('session-id', 'data')
        ],
        prevent_initial_call=True
    )
    @controller_error(config, 6)
    def update_report_state(
            errors: List | None,
            n_run_clicks: int | None,
            portfolio_platforms: List[str],
            portfolio_asset: str,
            initial_portfolio_amount: float,
            strategy_name: str,
            platforms: List[str],
            use_fees: bool,
            date_range: Tuple[str],
            start_time: str,
            end_time: str,
            assets: List[str],
            max_trade_ratio: float,
            min_spread: float,
            primary_granularity: int,
            secondary_granularity: int,
            locale: str,
            session_id: str
    ):
        if n_run_clicks is None or errors is not None:
            raise PreventUpdate

        controls_state = dict(
            portfolio_platforms=portfolio_platforms,
            portfolio_asset=portfolio_asset,
            initial_portfolio_amount=initial_portfolio_amount,
            strategy_name=strategy_name,
            platforms=platforms,
            fees_estimation=use_fees,
            date_range=date_range,
            start_time=start_time,
            end_time=end_time,
            assets=assets,
            max_trade_ratio=max_trade_ratio,
            min_spread=min_spread,
            primary_granularity=primary_granularity,
            secondary_granularity=secondary_granularity
        )

        fsc = FileSystemStore(f'./cache/{session_id}')
        reset_cache(fsc)

        prices_api = ExchangesAPI(db=data.get_db('crypto_exchanges'), exchanges_names=platforms)

        # TODO: real fees and prices data
        blockchain = Blockchain(prices_api=prices_api,
                                fees_data=AVG_FEES,
                                prices_data=None,
                                disable_fees=not use_fees)

        start_date = datetime.datetime.strptime(f'{date_range[0]} {start_time.split("T")[1]}', '%Y-%m-%d %H:%M:%S')
        start_timestamp = int(datetime.datetime.timestamp(start_date))

        end_date = datetime.datetime.strptime(f'{date_range[1]} {end_time.split("T")[1]}', '%Y-%m-%d %H:%M:%S')
        end_timestamp = int(datetime.datetime.timestamp(end_date))

        report_data = None
        prices_data = None
        graphs_history = []
        curr_portfolio = None
        initial_portfolio = None
        for run_res in name_to_strategy(strategy_name)(blockchain=blockchain,
                                                       start_timestamp=start_timestamp,
                                                       end_timestamp=end_timestamp,
                                                       timespan=primary_granularity,
                                                       primary_granularity=primary_granularity,
                                                       secondary_granularity=secondary_granularity,
                                                       portfolio=Portfolio(
                                                           {p: {
                                                               portfolio_asset: initial_portfolio_amount
                                                           } for p in
                                                               portfolio_platforms
                                                           }),
                                                       platforms=platforms,
                                                       symbols=assets,
                                                       max_trade_ratio=max_trade_ratio / 100,
                                                       min_spread=min_spread / 100):
            report_data = to_dataframe(run_res['report'])
            prices_data = run_res['prices']
            graphs_history = run_res['graphs_history']
            curr_portfolio = run_res['curr_portfolio']
            initial_portfolio = run_res['initial_portfolio']
            fsc.set('graphs_history', graphs_history)
            fsc.set('report_table', report_data)
            fsc.set('prices', prices_data)
            fsc.set('run_progress',
                    (run_res['end_timestamp'] - start_timestamp) / (end_timestamp - start_timestamp) * 100)
            fsc.set('curr_portfolio', curr_portfolio)
            fsc.set('initial_portfolio', initial_portfolio)

        return create_controls(config, locale, controls_state), \
            create_step_control(report_data, disabled=False), \
            create_trades_predictions(report_data), \
            create_trades(report_data, secondary_granularity), \
            create_network(last(graphs_history)), \
            create_prices(prices_data), \
            create_final_balances(curr_portfolio, initial_portfolio), \
            None, \
            dash.no_update, \
            'invisible',

    def valid_input(config, controls_state: dict, locale: str) -> List[dict | None]:
        errs = []

        for k, v in controls_state.items():
            if is_empty(v):
                dct = dict()
                dct['field'] = localize(config, k, locale)
                dct['message'] = localize(config, 'field_not_empty', locale)
                errs.append(dct)
            else:
                errs.append(None)

        return errs

    @app.callback([
        Output('report-table-output', 'children'),
        Output('report-table', 'className'),
    ], [
        Trigger('interval-progress', 'n_intervals'),
        State('locale-state', 'data'),
        State('session-id', 'data')
    ])
    def update_report_table(
            n_intervals: int | None,
            locale: str,
            session_id: str
    ):
        fsc = FileSystemStore(f'./cache/{session_id}')

        data = fsc.get('report_table')
        if data is None:
            raise PreventUpdate
        return create_report_table(config, locale, data), ''

    @app.callback(
        Output('simulation-progress-bar', 'children'),
        [
            Trigger('interval-progress', 'n_intervals'),
            State('locale-state', 'data'),
            State('session-id', 'data')
        ]
    )
    def update_run_progress(
            n_intervals: int | None,
            locale: str,
            session_id: str
    ):
        fsc = FileSystemStore(f'./cache/{session_id}')

        value = fsc.get('run_progress')  # get progress
        if value is None:
            # cache is only reset after we've hit 100% completion in the progress bar
            reset_cache(fsc)
            return create_progress_bar(0)
        value = min(value, 100)

        if value == 100:
            reset_cache(fsc)
        return create_progress_bar(value)

    @app.callback(
        [
            Output('loading-arbitrage-table-output', 'children'),
            Output('loading-controls', 'children', allow_duplicate=True),
            Output('arbitrage-table', 'className'),
        ],
        [
            Input('view-arbitrage-button-control', 'n_clicks'),
            *controls_state,
            State('locale-state', 'data'),
            State('session-id', 'data')
        ],
        prevent_initial_call=True,
    )
    def update_arbitrages(
            n_clicks: int | None,
            portfolio_platforms: List[str],
            portfolio_asset: str,
            initial_portfolio_amount: float,
            strategy_name: str,
            platforms: List[str],
            use_fees: bool,
            date_range: Tuple[str],
            start_time: str,
            end_time: str,
            assets: List[str],
            max_trade_ratio: float,
            min_spread: float,
            primary_granularity: int,
            secondary_granularity: int,
            locale: str,
            session_id: str,
    ):
        if n_clicks is None:
            raise PreventUpdate

        controls_state = dict(
            portfolio_platforms=portfolio_platforms,
            portfolio_asset=portfolio_asset,
            initial_portfolio_amount=initial_portfolio_amount,
            strategy_name=strategy_name,
            platforms=platforms,
            fees_estimation=use_fees,
            date_range=date_range,
            start_time=start_time,
            end_time=end_time,
            assets=assets,
            max_trade_ratio=max_trade_ratio,
            min_spread=min_spread,
            primary_granularity=primary_granularity,
            secondary_granularity=secondary_granularity
        )

        return create_arbitrage_table(
            arbitrage_pairs(controls_state['platforms'], to_asset_pairs(controls_state['assets']))), \
            create_controls(config, locale, controls_state), \
            EMPTY_CLASS

    @app.callback(
        Output('trading-graph', 'children', allow_duplicate=True),
        [
            Input('slider-step-control', 'value'),
            Input('checkbox-only-benefit-cycle-control', 'checked'),
            State('locale-state', 'data'),
            State('session-id', 'data')
        ],
        prevent_initial_call=True)
    def update_trading_graph(
            step: int,
            only_neg: bool,
            locale: str,
            session_id: str
    ):
        fsc = FileSystemStore(f'./cache/{session_id}')

        return update_network(fsc, step, only_neg=only_neg)

    @app.callback([
        Output('step-control', 'children', allow_duplicate=True),
        Output('trades-predicted-plot', 'children', allow_duplicate=True),
        Output('trades-plot', 'children', allow_duplicate=True),
        Output('trading-graph', 'children', allow_duplicate=True),
        Output('prices-plot', 'children', allow_duplicate=True),
        Output('final-balances-card-group', 'children', allow_duplicate=True),
    ], [
        Trigger('interval-progress', 'n_intervals'),
        State('run-state', 'data'),
        State('select-secondary-granularity-select-control', 'value'),
        State('select-portfolio-asset-control', 'value'),
        Input('slider-step-control', 'value'),
        State('locale-state', 'data'),
        State('session-id', 'data')
    ],
        prevent_initial_call=True)
    def update_running(n_intervals: int | None,
                       running_state: str | None,
                       secondary_granularity: int,
                       portfolio_asset: str,
                       step: int,
                       locale: str,
                       session_id: str):
        initiator_control = dash.ctx.triggered_id

        # should not update after run completed
        if initiator_control == 'interval-progress':
            if running_state is None:
                raise PreventUpdate

        fsc = FileSystemStore(f'./cache/{session_id}')

        return update_step_control(fsc), \
            update_trades_predictions(fsc), \
            update_trades(fsc, secondary_granularity), \
            update_network(fsc, step), \
            update_prices(fsc), \
            update_final_balances(fsc)

    def update_step_control(fsc: FileSystemStore):
        data = fsc.get('report_table')
        if data is None:
            raise PreventUpdate
        return create_step_control(data, disabled=False)

    def update_trades_predictions(fsc: FileSystemStore):
        data = fsc.get('report_table')
        if data is None:
            raise PreventUpdate
        return create_trades_predictions(data)

    def update_trades(fsc: FileSystemStore, gran: int):
        data = fsc.get('report_table')
        if data is None:
            raise PreventUpdate
        return create_trades(data, gran)

    def update_network(fsc: FileSystemStore, graph_idx: int = -1, only_neg: bool = False):
        data = fsc.get('graphs_history')
        if data is None:
            raise PreventUpdate
        if len(data) == 0:
            raise PreventUpdate
        if graph_idx is None:
            return create_network(last(data), only_neg=only_neg)
        return create_network(data[graph_idx - 1], only_neg=only_neg)

    def update_prices(fsc: FileSystemStore):
        data = fsc.get('prices')
        if data is None:
            raise PreventUpdate
        return create_prices(data)

    def update_final_balances(fsc: FileSystemStore):
        curr_portfolio = fsc.get('curr_portfolio')
        initial_portfolio = fsc.get('initial_portfolio')
        if curr_portfolio is None:
            raise PreventUpdate
        return create_final_balances(curr_portfolio, initial_portfolio)
