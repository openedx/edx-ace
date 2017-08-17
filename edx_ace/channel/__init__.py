import abc
from django.conf import settings
from enum import Enum
import logging
import six

from edx_ace.utils.plugins import get_plugins
from edx_ace.utils.once import once

LOG = logging.getLogger(__name__)


# TODO(later): encapsulate the shared part of this namespace in the utils.plugin module
CHANNEL_EXTENSION_NAMESPACE = 'openedx.ace.channel'


class ChannelType(Enum):
    EMAIL = 'email'
    PUSH = 'push'


@six.add_metaclass(abc.ABCMeta)
class Channel(object):

    enabled = True
    channel_type = None

    @abc.abstractmethod
    def deliver(self, recipient, rendered_message):
        raise NotImplementedError()


@once
def channels():
    plugins = get_plugins(
        namespace=CHANNEL_EXTENSION_NAMESPACE,
        names=getattr(settings, 'ACE_ENABLED_CHANNELS', []),
    )

    channels = {}
    for extension in plugins:
        channel = extension.obj
        if channel.channel_type in channels:
            raise ValueError(
                'Multiple plugins registered for the same channel: {first} and {second}'.format(
                    first=channels[channel.channel_type].__class__.__name__,
                    second=channel.__class__.__name__,
                )
            )
        channels[channel.channel_type] = extension.obj

    return channels
