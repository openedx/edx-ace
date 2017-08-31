
# TODO(later): To prevent a monolith of exception classes here,
#   we may want to declare Channel-related errors in the
#   channel subdirectory.


class ChannelError(Exception):
    pass


class RecoverableChannelDeliveryError(ChannelError):
    def __init__(self, message, next_attempt_time):
        self.next_attempt_time = next_attempt_time
        super(RecoverableChannelDeliveryError, self).__init__(message)


class FatalChannelDeliveryError(ChannelError):
    pass


class UnsupportedChannelError(ChannelError):
    """ Raised when an attempt is made to process a message for an unsupported channel. """
    pass


class InvalidMessageError(Exception):
    pass
