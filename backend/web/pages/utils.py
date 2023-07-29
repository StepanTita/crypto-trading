import traceback
from functools import wraps

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import pandas as pd
from dash import html
from dash.exceptions import PreventUpdate

from trading.common.blockchain_logger import logger


def last(lst):
    if len(lst) == 0:
        return None
    return lst[-1]


def is_empty(obj) -> bool:
    if hasattr(obj, '__len__'):
        return len(obj) == 0
    return obj is None


def to_readable(field: str) -> str:
    return ' '.join(field.split('_')).title()


def localize(config, field: str, locale: str) -> str:
    return config['LOCALIZATION'][field][locale]


def controller_error(config, outputs):
    def deco_error(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            session_id = None
            locale = None
            try:
                session_id = args[-1]
                locale = args[-2]
                return f(*args, **kwargs)
            except PreventUpdate:
                raise PreventUpdate
            except Exception as e:
                traceback.print_exception(e)

                logger.warning(f'Something Went Wrong for the session: {session_id}')
                logger.error(e)
                return [dash.no_update] * outputs + [dbc.Accordion([
                    dbc.AccordionItem(children=
                    [
                        html.Plaintext(localize(config, 'something_went_wrong_1', locale)),
                        html.B(id='error-session-id', children=[
                            dbc.Stack(children=[
                                html.Div(args[-1], id='error-session-id', className='p-1'),
                                html.Div(dcc.Clipboard(target_id='error-session-id', style={'cursor': 'pointer'})),
                            ],
                                direction='horizontal', gap=1)
                        ]),
                        html.Plaintext(localize(config, 'something_went_wrong_2', locale),
                                       style={'color': 'crimson', 'font-family': 'courier'})
                    ],
                        style={'color': 'crimson'},
                        title=localize(config, 'something_went_wrong', locale),
                    )
                ])] + ['']

        return wrapper

    return deco_error


def to_dataframe(data: dict):
    """
    ensures that all of the types are casted consistently
    :param data:
    :return:
    """
    data = pd.DataFrame(data)
    data['dates'] = pd.to_datetime(data['dates'])
    return data
