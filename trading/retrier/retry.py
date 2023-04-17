import random
import time
from functools import wraps

import ccxt

from trading.common.blockchain_logger import logger

ccxt_errors = (
    ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout, ccxt.DDoSProtection)


def retry_with_exponential_backoff(ExceptionToCheck, tries=10, delay=3, backoff=2, max_delay=15 * 60):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param max_delay: max delay that can be reached in seconds
    :type max_delay: int
    """

    def deco_retry(f):

        @wraps(f)
        def f_retry(ref, *args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(ref, *args, **kwargs)
                except ccxt.BadSymbol:
                    return None
                except ExceptionToCheck as err:
                    msg = f"{str(err)}, Retrying in {mdelay} seconds..."

                    logger.warning(msg)
                    # adding random uniform delay to each sleep time to exclude any multiple requests synchronization
                    time.sleep(mdelay + random.uniform(a=1, b=10))
                    mtries -= 1
                    mdelay *= backoff
                    mdelay = min(mdelay, max_delay)
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry
