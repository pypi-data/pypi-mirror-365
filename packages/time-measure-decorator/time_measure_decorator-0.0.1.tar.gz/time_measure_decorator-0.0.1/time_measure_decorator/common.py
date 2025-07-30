import logging
import typing as t
from collections.abc import Callable
from functools import wraps
from time import perf_counter

P = t.ParamSpec('P')
R = t.TypeVar('R')

log = logging.getLogger('time-measure')

TOO_MANY_SECONDS_TO_SHOW: int = 120


def _log_execution_time(func_name: str, start_time: float) -> None:
    measure = (perf_counter() - start_time)
    unit = 'seconds'
    if measure >= TOO_MANY_SECONDS_TO_SHOW:
        measure = measure / 60
        unit = 'minutes'

    log.info('Func: %s. Elapsed time in %s: %s', func_name, unit, measure)


def measure_time(fn: Callable[P, R]) -> Callable[P, R]:
    @wraps(fn)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
        start_time = perf_counter()
        fn_name = fn.__name__ or str(fn)
        try:
            result = fn(*args, **kwargs)
        except KeyboardInterrupt:
            _log_execution_time(fn_name, start_time)
            raise
        _log_execution_time(fn_name, start_time)
        return result
    return wrapped


def async_measure_time(fn: Callable[P, t.Awaitable[R]]) -> Callable[P, t.Awaitable[R]]:
    @wraps(fn)
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
        start_time = perf_counter()
        fn_name = fn.__name__ or str(fn)
        try:
            result = await fn(*args, **kwargs)
        except KeyboardInterrupt:
            _log_execution_time(fn_name, start_time)
            raise
        _log_execution_time(fn_name, start_time)
        return result
    return wrapped
