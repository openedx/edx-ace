"""
:mod:`edx_ace.monitoring` exposes functions that are useful for reporting ACE
message delivery stats to monitoring services.
"""
from edx_django_utils.monitoring import set_custom_attribute


def report(key, value):
    set_custom_attribute(key, value)
