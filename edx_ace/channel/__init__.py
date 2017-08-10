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


@six.add_metaclass(abc.ABCMeta)
class Channel(object):

    enabled = True
    channel_type = ChannelType.UNSPECIFIED

    @abc.abstractmethod
    def deliver(self, recipient, rendered_message):
        raise NotImplementedError()


def load_channels():
    channel_names = getattr(settings, 'ACE_ENABLED_CHANNELS', [])
    if len(channel_names) == 0:
        return {}

    plugins = get_plugins(
        namespace=CHANNEL_EXTENSION_NAMESPACE,
        names=channel_names,
    )

    channels = {}
    for channel_extension in plugins:
        channel_class = channel_extension.plugin
        if channel_class.enabled:
            if channel_class.channel_type in channels:
                raise ValueError(
                    'Multiple plugins registered for the same channel: {first} and {second}'.format(
                        first=channels[channel_class.channel_type].__class__.__name__,
                        second=channel_class.__name__,
                    )
                )

            channels[channel_class.channel_type] = channel_class()
        else:
            LOG.info("Channel %s not enabled", channel_class)

    return channels
