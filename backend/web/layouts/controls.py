import dash_mantine_components as dmc
from dash import html
from datetime import date, datetime


def create_controls():
    return html.Div(
        id='controls',
        children=[
            html.Div(className='row', children=[
                html.Div(className='half column', children=[
                    dmc.DateRangePicker(
                        id='date-range-picker',
                        label='Date Range',
                        minDate=date(2021, 1, 1),
                        maxDate=datetime.now().date(),
                    ),
                ]),
                html.Div(className='half column', children=[
                    html.Div(className='row', children=[
                        html.Div(id='platforms-select-control', children=[
                            dmc.MultiSelect(
                                id='multiselect-platforms-select-control',
                                label='Select platforms',
                                value=['binanceus'],
                                data=[
                                    {'value': 'binanceus', 'label': 'Binance US'},
                                    {'value': 'binance', 'label': 'Binance'},
                                    {'value': 'coinbase', 'label': 'Coinbase'},
                                    {'value': 'bybit', 'label': 'ByBit'},
                                    {'value': 'kraken', 'label': 'Kraken'},
                                ],
                            ),
                        ]),
                    ]),
                ]),
            ]),

            html.Div(className='row', children=[
                html.Div(id='time-range-controls', className='half column', children=[
                    html.Div(id='time-start-control', className='column', children=[
                        dmc.TimeInput(
                            label='Start time:',
                            withSeconds=True,
                            value=datetime(2020, 1, 1, 0, 0, 0),
                        ),
                    ]),
                    html.Div(id='time-end-control', className='half column', children=[
                        dmc.TimeInput(
                            label='End time:',
                            withSeconds=True,
                            value=datetime(2020, 1, 1, 0, 0, 0),
                        ),
                    ]),
                ]),
                html.Div(className='half column', children=[
                    html.Div(className='row', children=[
                        html.Div(id='assets-select-control', children=[
                            dmc.MultiSelect(
                                id='multiselect-assets-select-control',
                                label='Select symbols',
                                value=['BTC', 'USDT', 'ETH', 'LTC'],
                                data=[
                                    {'value': 'BTC', 'label': 'BTC'},
                                    {'value': 'USDT', 'label': 'USDT'},
                                    {'value': 'ETH', 'label': 'ETH'},
                                    {'value': 'LTC', 'label': 'LTC'},
                                ],
                            ),
                        ]),
                    ])
                ]),
            ]),

            html.Div(className='row', children=[
                html.Div(className='half column', children=[
                    html.Div(id='min-spread-control', children=[
                        html.Div(className='row', children=[
                            dmc.Text('Min Spread', className='control-label')
                        ]),
                        html.Div(className='row', children=[
                            html.Div(className='row', children=[
                                dmc.Slider(
                                    id='slider-min-spread-control',
                                    value=26,
                                    marks=[
                                        {'value': 20, 'label': '20%'},
                                        {'value': 50, 'label': '50%'},
                                        {'value': 80, 'label': '80%'},
                                    ],
                                    mb=35,
                                ),
                            ])
                        ]),
                    ]),
                ]),

                html.Div(className='half column', children=[
                    html.Div(id='max-trade-ratio-control', children=[
                        html.Div(className='row', children=[
                            dmc.Text('Max Trade Ratio', className='mantine-ittua2')
                        ]),
                        html.Div(className='row', children=[
                            dmc.Slider(
                                id='slider-max-trade-ratio-control',
                                value=26,
                                marks=[
                                    {'value': 20, 'label': '20%'},
                                    {'value': 50, 'label': '50%'},
                                    {'value': 80, 'label': '80%'},
                                ],
                                mb=35,
                            ),
                        ]),
                    ])
                ])
            ]),

            html.Div(id='run-controls', className='row', children=[
                dmc.Group(children=[
                    dmc.Button('Run!', id='run-button-control', variant="gradient"),
                    dmc.Button('View Arbitrages', id='view-arbitrage-button-control', variant="gradient"),
                    dmc.Checkbox(label='Enable fees estimation?')
                ]),
            ])
        ]
    )


def create_step_control():
    return dmc.Slider(
        id='slider-step-control',
        value=26,
        marks=[
            {'value': 20, 'label': '20%'},
            {'value': 50, 'label': '50%'},
            {'value': 80, 'label': '80%'},
        ],
        mb=35,
    )
