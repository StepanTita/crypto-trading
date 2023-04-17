import dash
from dash import html, Output, Input

from trading.exchanges.arbitrage_pairs import arbitrage_pairs
from .layout import html_layout

from backend.web.layouts.graphs_layout import create_graph_layout
from backend.web.layouts.tables import create_arbitrage_table, create_report_table
from backend.utils import to_asset_pairs


def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            '/static/dist/css/styles.css',
        ]
    )

    # Initialize callbacks after our app is loaded
    # Pass dash_app as a parameter
    init_callbacks(dash_app)

    dash_app.index_string = html_layout

    # Create Dash Layout
    dash_app.layout = html.Div(
        id='dash-container',
        children=create_graph_layout(),
    )

    return dash_app.server


def init_callbacks(app):
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

    @app.callback(
        Output('loading-report-table-output', 'children'),
        Input('run-button-control', 'n_clicks'),
    )
    def update_report(n_clicks):
        if n_clicks is None:
            return create_report_table()
        return create_report_table()
