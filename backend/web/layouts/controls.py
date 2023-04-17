import dash_mantine_components as dmc
from dash import html
from datetime import date, datetime


def create_controls(config):
    return dmc.LoadingOverlay(html.Div(
        id='controls',
        children=[
            html.Div(className='row', children=[
                html.Div(className='full', children=[
                    dmc.Select(id='select-strategy-select-control', label='Select strategy',
                               value='bellman-ford',
                               data=config.get('STRATEGIES'))
                ])
            ]),
            html.Div(className='row', children=[
                html.Div(className='half column', children=[
                    html.Div(id='select-primary-granularity-control', children=[
                        dmc.Select(id='select-primary-granularity-select-control', label='Select primary granularity',
                                   value=60,
                                   data=config.get('GRANULARITIES'))
                    ])
                ]),
                html.Div(className='half column', children=[
                    html.Div(id='select-secondary-granularity-control', children=[
                        dmc.Select(id='select-secondary-granularity-select-control',
                                   label='Select secondary granularity',
                                   value=60,
                                   data=config.get('GRANULARITIES'))
                    ])
                ])

            ]),
            html.Div(className='row', children=[
                html.Div(className='half column', children=[
                    dmc.DateRangePicker(
                        id='date-range-picker-control',
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
                                value=['binanceus', 'bybit'],
                                data=config.get('PLATFORMS'),
                            ),
                        ]),
                    ]),
                ]),
            ]),

            html.Div(className='row', children=[
                html.Div(id='time-range-controls', className='half column', children=[
                    html.Div(id='time-start-control', className='column', children=[
                        dmc.TimeInput(
                            id='start-timestamp-timeinput-control',
                            label='Start time:',
                            withSeconds=True,
                            value=datetime(2020, 1, 1, 0, 0, 0),
                        ),
                    ]),
                    html.Div(id='time-end-control', className='half column', children=[
                        dmc.TimeInput(
                            id='end-timestamp-timeinput-control',
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
                                data=config.get('ASSETS'),
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
                                    min=0,
                                    max=10,
                                    step=0.1,
                                    value=0.5,
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
                    dmc.Checkbox(id='use-fees-checkbox-control', label='Enable fees estimation?', checked=False)
                ]),
            ])
        ]
    ), loaderProps={'variant': 'bars', 'color': 'blue', 'size': 'xl'},
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


def create_progress_bar(value):
    return dmc.Progress(
        id='simulation-progress-bar-control',
        animate=True,
        label=f'{value}%',
        value=value,
        size='xl',
    )
