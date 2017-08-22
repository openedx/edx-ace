import logging

import edx_ace.delivery
from edx_ace.errors import UnsupportedChannelError
import edx_ace.policy
import edx_ace.presentation


LOG = logging.getLogger(__name__)


# TODO(now): Have this top-level function handle errors and log statements
#   If channels_for returns no channels
#   If delivery fails
def send(msg):
    logger = msg.get_message_specific_logger(LOG)
    logger.info('Sending message: %s', msg)

    channels_for_message = edx_ace.policy.channels_for(msg)
    for channel in channels_for_message:
        try:
            rendered_message = edx_ace.presentation.render(channel, msg)
        except UnsupportedChannelError:
            logger.exception("Unable to render for channel %s", channel)
        else:
            edx_ace.delivery.deliver(channel, rendered_message, msg)
