import datetime
import uuid
from collections import defaultdict
from typing import List

import dash_cytoscape as cyto
import numpy as np
import plotly.graph_objects as go
from dash import dcc

from trading.common.utils import TradeNetwork

# shapes:
"""
'ellipse',
'triangle',
'rectangle',
'diamond',
'pentagon',
'hexagon',
'heptagon',
'octagon',
'star',
'polygon',
"""


def create_network(data: TradeNetwork = None, only_neg=False):
    if data is None:
        return None

    if len(data) == 0:
        return None

    return cyto.Cytoscape(
        id='trading-network-graph',
        zoomingEnabled=False,
        elements=[
            *[{
                'data': {
                    'id': f'{asset.symbol}_{asset.platform}',
                    'label': f'{asset.symbol} ({asset.platform})',
                }
            }
                for asset in data.assets_mapping],
            *[{
                'data': {
                    'id': f'{edge.from_asset.symbol}_{edge.from_asset.platform}-{edge.to_asset.symbol}_{edge.to_asset.platform}-{uuid.uuid4()}',
                    'source': f'{edge.from_asset.symbol}_{edge.from_asset.platform}',
                    'target': f'{edge.to_asset.symbol}_{edge.to_asset.platform}',
                    'weight': round(np.exp(edge.weight), 2),
                },
                'style': {'line-color': 'rgba(144, 238, 144, 0.7)',
                          'width': 3} if edge in data.neg_cycle and data.true_neg else \
                    {'line-color': 'rgba(255, 65, 54, 0.6)',
                     'width': 6} if edge in data.neg_cycle and not data.true_neg else None,
            }
                for edge
                in
                data.edges_list if (not only_neg) or (only_neg and edge in data.neg_cycle)],
        ],
        layout={
            'name': 'circle',
            'directed': True,
            'idealEdgeLength': 100,
            'nodeOverlap': 20,
            'refresh': 20,
            'fit': True,
            'padding': 30,
            'randomize': False,
            'componentSpacing': 100,
            'nodeRepulsion': 400000,
            'edgeElasticity': 100,
            'nestingFactor': 5,
            'gravity': 80,
            'numIter': 1000,
            'initialTemp': 200,
            'coolingFactor': 0.95,
            'minTemp': 1.0
        },
        style={'width': '100%', 'height': '100%'},
        stylesheet=[
            {
                'selector': 'node',
                'style': {
                    'content': 'data(label)',
                    'text-halign': 'center',
                    'text-valign': 'center',
                    # 'width': 'label',
                    # 'height': 'label',
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'curve-style': 'bezier',
                    'label': 'data(weight)',
                    'source-arrow-shape': 'triangle',
                    'target-arrow-shape': 'triangle',
                }
            },
            {
                'selector': f'#{data.neg_cycle[0].from_asset.symbol}_{data.neg_cycle[0].from_asset.platform}',
                'style': {
                    'shape': 'triangle',
                    'background-color': 'crimson',
                }
            },
            {
                'selector': f'#{data.neg_cycle[-1].to_asset.symbol}_{data.neg_cycle[-1].to_asset.platform}',
                'style': {
                    'shape': 'diamond' if data.neg_cycle[0].from_asset == data.neg_cycle[-1].to_asset else 'rectangle',
                    'background-color': 'rgb(255, 87, 51)' if data.neg_cycle[0].from_asset == data.neg_cycle[
                        -1].to_asset else 'rgb(34, 139, 230)'
                }
            },
        ],
        responsive=True,
    )


def create_prices(data: List[List[dict]] = None):
    if data is None:
        return None

    prices = defaultdict(list)
    timestamps = []

    for period_prices in data:
        for p in period_prices:
            prices[f'{p["symbol"]} ({p["platform"]})'].append(p['price'])
        if len(period_prices) > 0:
            timestamps.append(datetime.datetime.fromtimestamp(period_prices[0]['timestamp']))

    to_show = np.random.choice(list(prices.keys()))
    fig = go.Figure(
        data=
        [
            go.Scatter(x=timestamps, y=price, fill='tonexty', name=k, visible='legendonly' if k != to_show else None)
            for k, price in prices.items()
        ]
    )
    fig.update_yaxes(type='log')

    return dcc.Graph(
        figure=fig
    )
