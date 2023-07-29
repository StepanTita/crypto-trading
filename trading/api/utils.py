import traceback

import numpy as np

from trading.common.blockchain_logger import logger
from trading.common.utils import nested_defaultdict


def cached_exchanges(fn):
    def wrapped(ref, timestamp, base_asset, quote_asset, *args, **kwargs):
        if not hasattr(ref, '__cache'):
            ref.__cache = nested_defaultdict(lambda: np.nan, 4)
        if ref.__cache[base_asset.platform][base_asset.symbol][quote_asset.symbol][timestamp] is np.nan:
            ref.__cache[base_asset.platform][base_asset.symbol][quote_asset.symbol][timestamp] = fn(ref, timestamp,
                                                                                                    base_asset,
                                                                                                    quote_asset,
                                                                                                    *args, **kwargs)
            if ref.__cache[base_asset.platform][base_asset.symbol][quote_asset.symbol][timestamp] is not None:
                ref.__cache[base_asset.platform][quote_asset.symbol][base_asset.symbol][timestamp] = 1.0 / ref.__cache[
                    base_asset.platform][
                    base_asset.symbol][
                    quote_asset.symbol][
                    timestamp]
                return ref.__cache[base_asset.platform][base_asset.symbol][quote_asset.symbol][timestamp]
            else:
                return np.inf
        return ref.__cache[base_asset.platform][base_asset.symbol][quote_asset.symbol][timestamp]

    return wrapped


def cached_fees(fn):
    def wrapped(ref, base_asset, quote_asset, *args, **kwargs):
        if not hasattr(ref, '__cache'):
            ref.__cache = nested_defaultdict(lambda: np.nan, 4)
        if ref.__cache[base_asset.platform][base_asset.symbol][quote_asset.symbol]['fees'] is np.nan:
            ref.__cache[base_asset.platform][base_asset.symbol][quote_asset.symbol]['fees'] = fn(ref,
                                                                                                 base_asset,
                                                                                                 quote_asset,
                                                                                                 *args, **kwargs)
            if ref.__cache[base_asset.platform][base_asset.symbol][quote_asset.symbol]['fees'] is not None:
                return ref.__cache[base_asset.platform][base_asset.symbol][quote_asset.symbol]['fees']
            ref.__cache[base_asset.platform][quote_asset.symbol][base_asset.symbol]['fees'] = 1.0 / ref.__cache[
                base_asset.platform][
                base_asset.symbol][
                quote_asset.symbol][
                'fees']
        return ref.__cache[base_asset.platform][base_asset.symbol][quote_asset.symbol]['fees']

    return wrapped


def log_continue(fn):
    def wrapped(ref, *args, **kwargs):
        try:
            return fn(ref, *args, **kwargs)
        except Exception as e:
            traceback.print_exception(e)
            logger.error(str(e))
            return np.inf

    return wrapped
