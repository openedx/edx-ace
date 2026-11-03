"""
:mod:`edx_ace.errors` exposes all exceptions that are specific to ACE.
"""


# TODO(later): To prevent a monolith of exception classes here,
#   we may want to declare Channel-related errors in the
#   channel subdirectory.


class ChannelError(Exception):
    """Indicates something went wrong in a delivery channel."""
    pass


class RecoverableChannelDeliveryError(ChannelError):
    """An error occurred during channel delivery that is non-fatal. The caller should re-attempt at a later time."""

    def __init__(self, message, next_attempt_time):
        self.next_attempt_time = next_attempt_time
        super().__init__(message)


class FatalChannelDeliveryError(ChannelError):
    """A fatal error occurred during channel delivery. Do not retry."""
    pass


class UnsupportedChannelError(ChannelError):
    """Raised when an attempt is made to process a message for an unsupported channel."""
    pass


class InvalidMessageError(Exception):
    """Encountered a message that cannot be sent due to missing or inconsistent information."""
    pass
