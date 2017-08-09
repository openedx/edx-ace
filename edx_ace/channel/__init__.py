import abc

import attr
from django.conf import settings
import six
from stevedore import named


CHANNEL_EXTENSION_NAMESPACE = 'openedx.ace.channel'


@six.add_metaclass(abc.ABCMeta)
class Channel(object):

    enabled = True
    channel_type = ChannelTypes.UNSPECIFIED

    @abc.abstractmethod
    def deliver(self, recipient, rendered_message):
        raise NotImplementedError()


class ChannelTypes(object):
    UNSPECIFIED = 'unspecified'
    EMAIL = 'email'


def load_channels():
    channel_names = getattr(settings, 'ACE_ENABLED_CHANNELS', [])
    if len(channel_names) == 0:
        return {}

    extension_manager = named.NamedExtensionManager(
        namespace=CHANNEL_EXTENSION_NAMESPACE,
        names=channel_names,
        invoke_on_load=False,
    )

    channels = {}
    for channel_class in extension_manager:
        if channel_class.enabled:
            if channel_class.channel_type in channels:
                raise ValueError(
                    'Multiple plugins registered for the same channel: {first} and {second}'.format(
                        first=channels[channel_class.channel_type].__class__.__name__,
                        second=channel_class.__name__,
                    )
                )

            channels[channel_class.channel_type] = channel_class()

    return channels
