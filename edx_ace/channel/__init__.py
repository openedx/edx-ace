import abc
from django.conf import settings
from enum import Enum
import logging
import six

from edx_ace.utils.plugins import get_plugins

LOG = logging.getLogger(__name__)


CHANNEL_EXTENSION_NAMESPACE = 'openedx.ace.channel'


class ChannelType(Enum):
    ALL = 'all'
    UNSPECIFIED = 'unspecified'
    EMAIL = 'email'


NON_CHANNEL_TYPES = (ChannelType.ALL, ChannelType.UNSPECIFIED)


@six.add_metaclass(abc.ABCMeta)
class Channel(object):

    enabled = True
    channel_type = ChannelType.UNSPECIFIED

    @abc.abstractmethod
    def deliver(self, recipient, rendered_message):
        raise NotImplementedError()


def load_channels():
    plugins = get_plugins(
        namespace=CHANNEL_EXTENSION_NAMESPACE,
        names=getattr(settings, 'ACE_ENABLED_CHANNELS', []),
    )

    channels = {}
    for channel_class in plugins.itervalues():
        if channel_class.channel_type in channels:
            raise ValueError(
                'Multiple plugins registered for the same channel: {first} and {second}'.format(
                    first=channels[channel_class.channel_type].__class__.__name__,
                    second=channel_class.__name__,
                )
            )
        channels[channel_class.channel_type] = channel_class()

    return channels
