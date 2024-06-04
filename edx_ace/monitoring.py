"""
:mod:`edx_ace.monitoring` exposes functions that are useful for reporting ACE
message delivery stats to monitoring services.
"""
from edx_django_utils.monitoring import DatadogBackend
try:
    import ddtrace.auto
except ImportError:
    ddtrace = None  # pylint: disable=invalid-name


def report(key, value):
    report_to_datadog(key, value)


def report_to_datadog(key, value):
    if ddtrace:
        DatadogBackend().set_attribute(key, value)
