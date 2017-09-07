import functools


def once(fn):
    @functools.wraps(fn)
    def wrapper():
        if not hasattr(fn, '__once_result'):
            fn.__once_result = fn()  # pylint: disable=protected-access
        return fn.__once_result  # pylint: disable=protected-access

    return wrapper
