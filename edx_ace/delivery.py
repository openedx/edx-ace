import datetime
import logging
import time

import six
from django.conf import settings

from edx_ace.channel import channels
from edx_ace.errors import RecoverableChannelDeliveryError
from edx_ace.utils.date import get_current_time

LOG = logging.getLogger(__name__)


def deliver(channel_type, rendered_message, message):
    """
    Deliver a message via a particular channel.

    Args:
        channel_type (ChannelType): The channel type to deliver the channel over.
        rendered_message (object): Each attribute of this object contains rendered content.
        message (Message): The message that is being sent.

    Raises:
        ValueError: If no channel of the requested channel type is available.

    """
    channel = channels().get(channel_type)
    if not channel:
        raise ValueError(
            'No implementation for channel {channel_type} registered. Available channels are: {channels}'.format(
                channel_type=channel_type,
                channels=', '.join(six.text_type(registered_channel_type) for registered_channel_type in channels())
            )
        )
    logger = message.get_message_specific_logger(LOG)

    timeout_seconds = getattr(settings, 'ACE_DEFAULT_EXPIRATION_DELAY', 120)
    default_expiration_time = get_current_time() + datetime.timedelta(seconds=timeout_seconds)
    expiration_time = message.expiration_time or default_expiration_time
    while get_current_time() < expiration_time:
        logger.debug('Attempting delivery of message')
        try:
            channel.deliver(message, rendered_message)
        except RecoverableChannelDeliveryError as delivery_error:
            num_seconds = (delivery_error.next_attempt_time - get_current_time()).total_seconds()
            logger.debug('Encountered a recoverable delivery error.')
            if delivery_error.next_attempt_time > expiration_time:
                logger.debug('Message will expire before delivery can be reattempted, aborting.')
                break
            elif num_seconds > 0:
                logger.debug('Sleeping for %d seconds.', num_seconds)
                time.sleep(num_seconds)

    logger.warn('Message expired before it could be successfully delivered.')
