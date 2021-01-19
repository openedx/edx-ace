"""
An internal module that manages the presentation/rendering step of the
ACE pipeline.
"""
from django.utils import translation

from edx_ace import errors, renderers
from edx_ace.channel import ChannelType

RENDERERS = {
    ChannelType.EMAIL: renderers.EmailRenderer(),
}


def render(channel, message):
    """ Returns the rendered content for the given channel and message. """
    renderer = RENDERERS.get(channel.channel_type)

    if not renderer:
        error_msg = f'No renderer is registered for the channel type [{channel.channel_type}].'
        raise errors.UnsupportedChannelError(error_msg)

    message_language = message.language or translation.get_language()
    with translation.override(message_language):
        return renderer.render(channel, message)
