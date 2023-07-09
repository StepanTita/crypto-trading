import pandas as pd
import plotly.graph_objects as go
from dash import dcc

from trading.common.constants import *

tickformat = [
    dict(dtickrange=[None, 1000], value="%H:%M:%S.%L ms"),
    dict(dtickrange=[1000, 60000], value="%H:%M:%S s"),
    dict(dtickrange=[60000, 3600000], value="%H:%M m"),
    dict(dtickrange=[3600000, 86400000], value="%H:%M h"),
    dict(dtickrange=[86400000, 604800000], value="%e. %b d"),
    dict(dtickrange=[604800000, "M1"], value="%e. %b w"),
    dict(dtickrange=["M1", "M12"], value="%b '%y M"),
    dict(dtickrange=["M12", None], value="%Y Y")
]


def create_trades(data: pd.DataFrame = None, granularity: int = HOUR):
    # replace those with empty container or something
    if data is None:
        return None

    if len(data) == 0:
        return None

    data['dates'] = data['dates'].apply(
        lambda x: (x.value - data['dates'].min().value)) // 10 ** 9 // granularity

    grouped_data = data.groupby(by=['dates'])['real'].sum()

    profitable_data = grouped_data[grouped_data > 0]
    losses_data = grouped_data[grouped_data < 0]
    return dcc.Graph(figure=go.Figure(data=(
        go.Bar(x=losses_data.index,
               y=-1 * losses_data,
               base=losses_data,
               marker_color='crimson',
               name='Losses'),
        go.Bar(x=profitable_data.index, y=profitable_data,
               base=0,
               marker_color='seagreen',
               name='Gains'
               )
    )))


def create_trades_predictions(data: pd.DataFrame = None):
    if data is None:
        return None

    if len(data) == 0:
        return None

    return dcc.Graph(figure=go.Figure(data=(
        go.Bar(x=data['dates'].dt.strftime('%Y-%m-%d %H:%M'),
               y=data['predicted'],
               marker_color='seagreen',
               name='Predicted'),
        go.Bar(x=data['dates'].dt.strftime('%Y-%m-%d %H:%M'),
               y=data['real'],
               base=0,
               marker_color=['crimson' if p < 0 else 'seagreen' for p in data['real']],
               name='Actual'
               ),
    ), layout={'showlegend': False, 'xaxis': dict(type='category')}))
