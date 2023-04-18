from dash import dash_table, html
import dash_mantine_components as dmc
from dash.dash_table.Format import Format, Scheme


def create_report_table(data=None):
    if data is None:
        return None

    columns = ['dates', 'predicted', 'real', 'coins']
    balance_columns = [k for k in data.columns if k.count('_') == 1]

    return dash_table.DataTable(
        data=data[columns + balance_columns].to_dict('records'),
        columns=[
            {'name': 'dates', 'id': 'dates', 'type': 'datetime'},
            {'name': 'predicted', 'id': 'predicted', 'type': 'numeric',
             'format': Format(precision=4, scheme=Scheme.fixed)},
            {'name': 'real', 'id': 'real', 'type': 'numeric', 'format': Format(precision=4, scheme=Scheme.fixed)},
            {'name': 'coins', 'id': 'coins', 'type': 'text'},
            *[{'name': (lambda x: f'{x[1]} {(x[0])}')(k.split('_')), 'id': k, 'type': 'numeric',
               'format': Format(precision=4, scheme=Scheme.fixed)} for k in
              balance_columns],
        ],
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{real} < 0',
                },
                'backgroundColor': '#FF4136',
                'color': 'white'
            },
            {
                'if': {
                    'filter_query': '{real} > 0',
                },
                'backgroundColor': 'lightgreen',
                'color': 'white'
            },
        ],
        page_size=10,
        style_table={'overflowX': 'scroll'}
    )


def create_arbitrage_table(data=None):
    if data is None:
        return None

    columns = [
        {'name': column, 'id': column, 'type': 'text'} for column in data.columns
    ]
    styles = [
        {
            'if': {
                'filter_query': f'{{{column}}} is blank',
                'column_id': column
            },
            'backgroundColor': '#FF4136',
            'color': 'white'
        } for column in data.columns
    ]

    return dash_table.DataTable(
        data=data.to_dict('records'),
        columns=columns,
        style_data_conditional=styles,
        page_size=10
    )
