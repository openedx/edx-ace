# -*- coding: utf-8 -*-
u"""
:mod:`edx_ace.monitoring` exposes functions that are useful for reporting ACE
message delivery stats to monitoring services.
"""
from __future__ import absolute_import

try:
    import newrelic.agent
except ImportError:
    newrelic = None  # pylint: disable=invalid-name


def report(key, value):
    report_to_newrelic(key, value)


def report_to_newrelic(key, value):
    if newrelic:
        newrelic.agent.add_custom_parameter(key, value)
