# lint-amnesty, pylint: disable=missing-docstring
import functools


def once(fn):  # lint-amnesty, pylint: disable=missing-docstring
    @functools.wraps(fn)
    def wrapper():
        if not hasattr(fn, '__once_result'):
            fn.__once_result = fn()  # lint-amnesty, pylint: disable=protected-access
        return fn.__once_result  # lint-amnesty, pylint: disable=protected-access
    return wrapper
