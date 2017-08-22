import six

from edx_ace.channel import channels


def deliver(channel_type, rendered_message, message):
    channel = channels().get(channel_type)
    if not channel:
        # TODO(now): There is no 'self' variable, although it's used below.
        raise ValueError(
            'No implementation for channel {channel_type} registered. Available channels are: {channels}'.format(
                channel_type=channel_type,
                channels=', '.join(six.text_type(channel) for channel in self.channels.keys())
            )
        )
    return channel.deliver(message, rendered_message)
