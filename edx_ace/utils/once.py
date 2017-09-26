# -*- coding: utf-8 -*-
u"""
:mod:`edx_ace.utils.once` provides the ability to create a module-level
function that caches it's result after the first call (this can be used
for lazy-loading expensive computations).
"""
from __future__ import absolute_import, division, print_function

import functools


def once(func):
    u"""
    Decorates a function that will be called exactly once.

    After the function is called once, its result is stored in memory and immediately returned to subsequent callers
    instead of calling the decorated function again.

    Examples:

        An incrementing value::

            _counter = 0

            @once
            def get_counter():
                global _counter
                _counter += 1
                return _counter

            def get_counter_updating():
                global _counter
                _counter += 1
                return _counter

            print(get_counter())  # This will print "0"
            print(get_counter_updating()) # This will print "1"
            print(get_counter())  # This will also print "0"
            print(get_counter_updating()) # This will print "2"

        Lazy loading::

            @once
            def load_config():
                with open('config.json', 'r') as cfg_file:
                    return json.load(cfg_file)

            cfg = load_config()  # This will do the relatively expensive operation to
                                 # read the file from disk.
            cfg2 = load_config() # This call will not reload the file from disk, it
                                 # will use the value returned by the first invocation
                                 # of this function.

    Args:
        func (callable): The function that should be called exactly once.

    Returns:
        callable: The wrapped function.
    """

    @functools.wraps(func)
    def wrapper():
        if not hasattr(func, u'__once_result'):
            func.__once_result = func()  # pylint: disable=protected-access
        return func.__once_result  # pylint: disable=protected-access

    return wrapper
