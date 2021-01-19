"""
Functions for delivering ACE messages.

This is an internal interface used by :func:`.ace.send`.
"""
import datetime
import logging
import time

from django.conf import settings

from edx_ace.errors import RecoverableChannelDeliveryError
from edx_ace.utils.date import get_current_time

LOG = logging.getLogger(__name__)

# Set a maximum expiration delay, for now, since we're currently
# not using celery to re-enqueue retries and so we could be
# potentially blocking a worker indefinitely.
#
# TODO(later): Use celery per channel delivery to be smarter
# about re-enqueueing and retrying, and to not block workers.
MAX_EXPIRATION_DELAY = 5 * 60


def deliver(channel, rendered_message, message):
    """
    Deliver a message via a particular channel.

    Args:
        channel (Channel): The channel to deliver the message over.
        rendered_message (object): Each attribute of this object contains rendered content.
        message (Message): The message that is being sent.

    Raises:
        :class:`.UnsupportedChannelError`: If no channel of the requested channel type is available.

    """
    logger = message.get_message_specific_logger(LOG)
    channel_type = channel.channel_type

    timeout_seconds = getattr(settings, 'ACE_DEFAULT_EXPIRATION_DELAY', 120)
    start_time = get_current_time()
    default_expiration_time = start_time + datetime.timedelta(seconds=timeout_seconds)
    max_expiration_time = start_time + datetime.timedelta(seconds=MAX_EXPIRATION_DELAY)
    expiration_time = min(max_expiration_time, message.expiration_time or default_expiration_time)

    logger.debug('Attempting delivery of message')
    while get_current_time() < expiration_time:
        try:
            channel.deliver(message, rendered_message)
        except RecoverableChannelDeliveryError as delivery_error:
            num_seconds = (delivery_error.next_attempt_time - get_current_time()).total_seconds()
            logger.debug('Encountered a recoverable delivery error.')
            if delivery_error.next_attempt_time > expiration_time:
                logger.debug('Message will expire before delivery can be reattempted, aborting.')
                break
            logger.debug('Sleeping for %d seconds before reattempting delivery of message.', num_seconds)
            time.sleep(num_seconds)
            message.report(f'{channel_type}_delivery_retried', num_seconds)
        else:
            message.report(f'{channel_type}_delivery_succeeded', True)
            return

    delivery_expired_report = f'{channel_type}_delivery_expired'
    logger.debug(delivery_expired_report)
    message.report(delivery_expired_report, get_current_time() - start_time)
