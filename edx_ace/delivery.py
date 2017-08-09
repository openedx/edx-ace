from abc import ABCMeta

import attr
import six

from edx_ace.ace_step import ACEStep
from edx_ace.channel import load_channels


@six.add_metaclass(ABCMeta)
class Delivery(ACEStep):

    def __init__(self):
        self.channels = load_channels()

    def deliver(self, channel_type, recipient, rendered_message):
        channel = self.channels.get(channel_type)
        if not channel:
            raise ValueError(
                'No implementation for channel {channel_type} registered. Available channels are: {channels}'.format(
                    channel_type=channel_type,
                    channels=', '.join(self.channels.keys())
                )
            )
        return channel.deliver(recipient, rendered_message)


@attr.s
class Recipient(object):
    email_address = attr.ib()
