
import six

from edx_ace.ace_step import ACEStep
from edx_ace.channel import load_channels


class DeliveryStep(ACEStep):

    def __init__(self):
        self.channels = load_channels()

    def deliver(self, channel_type, rendered_message, message):
        channel = self.channels.get(channel_type)
        if not channel:
            raise ValueError(
                'No implementation for channel {channel_type} registered. Available channels are: {channels}'.format(
                    channel_type=channel_type,
                    channels=', '.join(six.text_type(channel) for channel in self.channels.keys())
                )
            )
        return channel.deliver(message, rendered_message)
