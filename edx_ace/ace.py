import logging

import edx_ace.delivery
from edx_ace.errors import UnsupportedChannelError
import edx_ace.policy
import edx_ace.presentation


LOG = logging.getLogger(__name__)


def send(msg):
    channels_for_message = edx_ace.policy.channels_for(msg)
    for channel in channels_for_message:
        try:
            rendered_message = edx_ace.presentation.render(channel, msg)
        except UnsupportedChannelError:
            LOG.exception("Unable to render message %s for channel %s", msg, channel)
        else:
            edx_ace.delivery.deliver(channel, rendered_message, msg)
