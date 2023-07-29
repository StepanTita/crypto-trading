from datetime import datetime, date

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from dash import html

from backend.web.pages.utils import localize
from trading.common.constants import *


def create_controls(config, locale, initial_state=None):
    if initial_state is None:
        initial_state = dict()

    return dmc.LoadingOverlay(html.Div(
        id='controls',
        children=[
            dbc.Row(children=[
                dbc.Col(children=[
                    dmc.MultiSelect(
                        id='multiselect-portfolio-control',
                        label=localize(config, 'portfolio_platforms', locale),
                        value=initial_state.get('portfolio', {'platforms': ['binanceus']})['platforms'],
                        data=config.get('PLATFORMS')
                    ),
                ], width=12, md=6),
                dbc.Col(children=[
                    dmc.Select(
                        id='select-portfolio-asset-control',
                        label=localize(config, 'portfolio_asset', locale),
                        value=initial_state.get('portfolio', {'asset': 'USDT'})['asset'],
                        data=config.get('ASSETS')
                    )
                ], width=12, md=3),
                dbc.Col(children=[
                    dmc.NumberInput(
                        id='number-input-portfolio-amount',
                        label=localize(config, 'initial_portfolio_amount', locale),
                        value=initial_state.get('portfolio', {'amount': 1000})['amount'],
                        min=0,
                        max=1_000_000_000,
                        step=1e-6,
                        precision=7,
                    )
                ], width=12, md=3),
            ]),
            dbc.Row(children=[
                dbc.Col(children=[
                    dmc.Select(id='select-strategy-select-control',
                               label=localize(config, 'strategy_name', locale),
                               value=initial_state.get('strategy_name', 'bellman-ford'),
                               data=config.get('STRATEGIES'), disabled=True)
                ], width=12)
            ]),
            dbc.Row(children=[
                dbc.Col(children=[
                    html.Div(id='select-primary-granularity-control', className='text-truncate', children=[
                        dmc.Select(id='select-primary-granularity-select-control',
                                   label=localize(config, 'primary_granularity', locale),
                                   value=initial_state.get('primary_granularity', HOUR),
                                   data=config.get('GRANULARITIES'))
                    ])
                ], width=12, md=6),
                dbc.Col(children=[
                    html.Div(id='select-secondary-granularity-control', className='text-truncate', children=[
                        dmc.Select(id='select-secondary-granularity-select-control',
                                   label=localize(config, 'secondary_granularity', locale),
                                   value=initial_state.get('secondary_granularity', DAY),
                                   data=config.get('GRANULARITIES'))
                    ])
                ], width=12, md=6)

            ]),
            dbc.Row(children=[
                dbc.Col(children=[
                    dmc.DateRangePicker(
                        id='date-range-picker-control',
                        label=localize(config, 'date_range', locale),
                        minDate=config.get('DATE_RANGE', {'min_date': date(2021, 1, 1)})['min_date'],
                        maxDate=min(config.get('DATE_RANGE', {'max_date': date(2021, 1, 1)})['max_date'],
                                    datetime.now().date()),
                        value=initial_state.get('date_range', []),
                        dropdownPosition='bottom-start',
                    ),
                ], width=12, md=6),
                dbc.Col(children=[
                    html.Div(children=[
                        html.Div(id='platforms-select-control', children=[
                            dmc.MultiSelect(
                                id='multiselect-platforms-select-control',
                                label=localize(config, 'platforms', locale),
                                value=initial_state.get('platforms', ['binanceus']),
                                data=config.get('PLATFORMS'),
                            ),
                        ]),
                    ]),
                ], width=12, md=6),
            ]),

            dbc.Row(children=[
                dbc.Col(children=[
                    dbc.Row(children=[
                        dbc.Col(children=[
                            html.Div(id='time-start-control', className='time-control', children=[
                                dmc.TimeInput(
                                    id='start-timestamp-timeinput-control',
                                    label=localize(config, 'start_time', locale),
                                    withSeconds=True,
                                    value=initial_state.get('start_time', datetime(2020, 1, 1, 0, 0, 0)),
                                ),
                            ]),
                        ], width=12, md=6),
                        dbc.Col(children=[
                            html.Div(id='time-end-control', className='time-control', children=[
                                dmc.TimeInput(
                                    id='end-timestamp-timeinput-control',
                                    label=localize(config, 'end_time', locale),
                                    withSeconds=True,
                                    value=initial_state.get('end_time', datetime(2020, 1, 1, 0, 0, 0)),
                                ),
                            ]),
                        ], width=12, md=6)
                    ],
                        id='time-range-controls',
                    ),
                ], width=12, md=6),

                dbc.Col(children=[
                    html.Div(children=[
                        html.Div(id='assets-select-control', children=[
                            dmc.MultiSelect(
                                id='multiselect-assets-select-control',
                                label=localize(config, 'assets', locale),
                                value=initial_state.get('assets', ['BTC', 'USDT', 'ETH', 'LTC']),
                                data=config.get('ASSETS'),
                            ),
                        ]),
                    ])
                ], width=12, md=6),
            ]),

            dbc.Row(children=[
                dbc.Col(children=[
                    html.Div(id='min-spread-control', children=[
                        html.Div(className='control-row', children=[
                            dmc.Text(localize(config, 'min_spread', locale), className='control-label')
                        ]),
                        html.Div(className='control-row', children=[
                            html.Div(className='control-row', children=[
                                dmc.Slider(
                                    id='slider-min-spread-control',
                                    min=0,
                                    max=10,
                                    step=0.1,
                                    value=initial_state.get('min_spread', 0.5),
                                    marks=[
                                        {'value': 2.5, 'label': '2.5%'},
                                        {'value': 5, 'label': '5%'},
                                        {'value': 7.5, 'label': '7.5%'},
                                    ],
                                    mb=35,
                                ),
                            ])
                        ]),
                    ]),
                ], width=12, md=6),
                dbc.Col(children=[
                    html.Div(id='max-trade-ratio-control', children=[
                        html.Div(className='control-row', children=[
                            dmc.Text(localize(config, 'max_trade_ratio', locale), className='mantine-ittua2')
                        ]),
                        html.Div(className='control-row', children=[
                            dmc.Slider(
                                id='slider-max-trade-ratio-control',
                                value=initial_state.get('max_trade_ratio', 50),
                                marks=[
                                    {'value': 20, 'label': '20%'},
                                    {'value': 50, 'label': '50%'},
                                    {'value': 80, 'label': '80%'},
                                ],
                                mb=35,
                            ),
                        ]),
                    ])
                ], width=12, md=6)
            ]),

            dbc.Row(children=[
                dbc.Col(children=[
                    dmc.Group(children=[
                        dmc.Button(localize(config, 'run_button', locale), id='run-button-control',
                                   variant='gradient'),
                        dmc.Button(localize(config, 'view_arbitrages', locale), id='view-arbitrage-button-control',
                                   variant='gradient'),
                        dmc.Checkbox(id='use-fees-checkbox-control',
                                     label=localize(config, 'fees_estimation', locale),
                                     checked=False, )
                    ], position='center'),
                ], width=12)
            ]),

            html.Div(id='errors-section', className='invisible', children=[
                dbc.Row(children=[
                    dbc.Col(children=[
                        dbc.Container(id='errors-container', children=[]),
                    ])
                ])
            ])
        ]
    ), loaderProps={'variant': 'bars', 'color': 'blue', 'size': 'xl'},
    )


def create_step_control(data: pd.DataFrame = None, disabled: bool = True):
    if data is None:
        return dmc.Slider(
            id='slider-step-control',
            className='invisible',
            min=0,
            max=0,
            value=None
        )

    dates = list(data['dates'])
    step = max(1, (len(dates) - 2) // 8)
    if len(dates) > 1:
        return dmc.Slider(
            id='slider-step-control',
            min=1,
            max=len(dates),
            value=len(dates),
            marks=[{'value': 1, 'label': dates[0].strftime('%Y-%m-%d %H:%M')}] + [
                {'value': i * step + 1, 'label': val.strftime('%Y-%m-%d %H:%M')} for i, val in
                enumerate(list(dates[1:-1:step]))
            ] + [{'value': len(dates), 'label': dates[-1].strftime('%Y-%m-%d %H:%M')}],
            mb=35,
            disabled=disabled,
        )

    return None


def create_progress_bar(value):
    value = round(value, 2)
    return dmc.Progress(
        id='simulation-progress-bar-control',
        animate=True,
        label=f'{value}%',
        value=value,
        size='xl',
    )


def create_only_benefit_cycle_checkbox(config, locale):
    return dmc.Checkbox(
        id='checkbox-only-benefit-cycle-control',
        checked=False,
        label=localize(config, 'keep_only_neg', locale),
        style={
            'display': 'flex',
            'justify-content': 'center',
            'align-items': 'center',
        },
        className='p-4',
    )
