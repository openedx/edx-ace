import functools


def once(fn):
    @functools.wraps(fn)
    def wrapper():
        if not hasattr(fn, '__once_result'):
            fn.__once_result = fn()
        return fn.__once_result
    return wrapper
