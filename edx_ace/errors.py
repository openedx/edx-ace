# -*- coding: utf-8 -*-
u"""
:mod:`edx_ace.errors` exposes all exceptions that are specific to ACE.
"""
from __future__ import absolute_import, division, print_function

# TODO(later): To prevent a monolith of exception classes here,
#   we may want to declare Channel-related errors in the
#   channel subdirectory.


class ChannelError(Exception):
    u"""Indicates something went wrong in a delivery channel."""
    pass


class RecoverableChannelDeliveryError(ChannelError):
    u"""An error occurred during channel delivery that is non-fatal. The caller should re-attempt at a later time."""

    def __init__(self, message, next_attempt_time):
        self.next_attempt_time = next_attempt_time
        super(RecoverableChannelDeliveryError, self).__init__(message)


class FatalChannelDeliveryError(ChannelError):
    u"""A fatal error occurred during channel delivery. Do not retry."""
    pass


class UnsupportedChannelError(ChannelError):
    u"""Raised when an attempt is made to process a message for an unsupported channel."""
    pass


class InvalidMessageError(Exception):
    u"""Encountered a message that cannot be sent due to missing or inconsistent information."""
    pass
