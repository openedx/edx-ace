
from django.utils import translation

from edx_ace import errors, renderers
from edx_ace.channel import ChannelType

RENDERERS = {
    ChannelType.EMAIL: renderers.EmailRenderer(),
}


def render(channel, message):
    """ Returns the rendered content for the given channel and message. """
    renderer = RENDERERS.get(channel)

    if not renderer:
        error_msg = 'No renderer is registered for the channel [{}].'.format(channel)
        raise errors.UnsupportedChannelError(error_msg)

    message_language = message.language or translation.get_language()
    with translation.override(message_language):
        return renderer.render(message)
