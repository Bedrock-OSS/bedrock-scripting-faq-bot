# type: ignore
'''
Util for extending the default lru_cache by adding a timeout possibility
'''

from datetime import datetime, timedelta, timezone
from functools import lru_cache as functools_lru_cache
from functools import wraps


def lru_cache(timeout: int, maxsize: int | None = None, typed: bool = False):
    '''
    Extend the default functools lru_cache by adding a timeout

    The cache now times out, when `timeout` seconds are passed

    :param timeout: The amount of seconds before the cache times out and gets deleted
    :type timeout: int
    :param maxsize: The maximal size of the cache (unused values get deleted first), defaults to None
    :type maxsize: int | None, optional
    :param typed: If values which are nearly identical but different types should be treated as the same values, defaults to False
    :type typed: bool, optional
    '''

    def _wrapper(f):

        f = functools_lru_cache(maxsize=maxsize, typed=typed)(f)
        f.lifetime = timedelta(seconds=timeout)
        f.expires = datetime.now(timezone.utc) + f.lifetime

        @wraps(f)
        def _wrapped(*args, **kwargs):

            if datetime.now(timezone.utc) >= f.expires:
                f.cache_clear()
                f.expires = datetime.now(timezone.utc) + f.lifetime

            return f(*args, **kwargs)

        return _wrapped

    return _wrapper
