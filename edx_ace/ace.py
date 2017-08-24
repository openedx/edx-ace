# lint-amnesty, pylint: disable=missing-docstring
import logging

from edx_ace import delivery, policy, presentation
from edx_ace.errors import ChannelError


LOG = logging.getLogger(__name__)


def send(msg):  # lint-amnesty, pylint: disable=missing-docstring
    logger = msg.get_message_specific_logger(LOG)
    logger.info('Sending message')

    channels_for_message = policy.channels_for(msg)
    for channel in channels_for_message:
        try:
            rendered_message = presentation.render(channel, msg)
            delivery.deliver(channel, rendered_message, msg)
        except ChannelError:
            logger.exception("Unable to send over channel %s", channel)

    if not channels_for_message:
        logger.warning("Policy allowed no channels for message")
