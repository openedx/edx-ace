from abc import ABCMeta

from edx_ace import errors, renderers
from edx_ace.ace_step import ACEStep


class Presentation(ACEStep):
    __metaclass__ = ABCMeta

    renderers = {
        'email': renderers.EmailRenderer,
    }

    def render(self, channel, message):
        """ Returns the rendered content for the given channel and message. """
        renderer = self.renderers.get(channel)

        if not renderer:
            error_msg = 'No renderer is registered for the channel [%s].'.format(channel)
            raise errors.UnsupportedChannelError(error_msg)

        return renderer.render(message)
