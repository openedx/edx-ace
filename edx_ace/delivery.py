# -*- coding: utf-8 -*-
u"""
Functions for delivering ACE messages.

This is an internal interface used by :func:`.ace.send`.
"""
from __future__ import absolute_import, division, print_function

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
    u"""
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

    timeout_seconds = getattr(settings, u'ACE_DEFAULT_EXPIRATION_DELAY', 120)
    start_time = get_current_time()
    default_expiration_time = start_time + datetime.timedelta(seconds=timeout_seconds)
    max_expiration_time = start_time + datetime.timedelta(seconds=MAX_EXPIRATION_DELAY)
    expiration_time = min(max_expiration_time, message.expiration_time or default_expiration_time)

    while get_current_time() < expiration_time:
        logger.debug(u'Attempting delivery of message')
        try:
            channel.deliver(message, rendered_message)
        except RecoverableChannelDeliveryError as delivery_error:
            num_seconds = (delivery_error.next_attempt_time - get_current_time()).total_seconds()
            logger.debug(u'Encountered a recoverable delivery error.')
            if delivery_error.next_attempt_time > expiration_time:
                logger.debug(u'Message will expire before delivery can be reattempted, aborting.')
                break
            elif num_seconds > 0:
                logger.debug(u'Sleeping for %d seconds.', num_seconds)
                time.sleep(num_seconds)
                message.report(u'{channel_type}_delivery_retried'.format(channel_type=channel_type), num_seconds)
        else:
            message.report(u'{channel_type}_delivery_succeeded'.format(channel_type=channel_type), True)
            return

    message.report(
        u'{channel_type}_delivery_expired'.format(channel_type=channel_type),
        get_current_time() - start_time
    )
