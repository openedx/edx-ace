
from lazy import lazy
import six

from edx_ace.channel import load_channels


class DeliveryStep(object):
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

    @lazy
    def channels(self):
        return load_channels()