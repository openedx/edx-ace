"""
:mod:`edx_ace.channel` exposes the ACE extension point needed
to add new delivery :class:`Channel` instances to an ACE application.

Developers wanting to add a new deliver channel should subclass :class:`Channel`,
and then add an entry to the ``openedx.ace.channel`` entrypoint in their ``setup.py``.
"""
import abc
import itertools
from collections import OrderedDict, defaultdict
from enum import Enum

from django.conf import settings

from edx_ace.errors import UnsupportedChannelError
from edx_ace.utils.once import once
from edx_ace.utils.plugins import get_plugins

# TODO(later): encapsulate the shared part of this namespace in the utils.plugin module
CHANNEL_EXTENSION_NAMESPACE = 'openedx.ace.channel'


class ChannelType(Enum):
    """
    All supported communication channels.
    """
    EMAIL = 'email'
    PUSH = 'push'

    def __str__(self):
        return str(self.value)


class Channel(metaclass=abc.ABCMeta):
    """
    Channels deliver messages to users that have already passed through the presentation and policy steps.

    Examples include email messages, push notifications, or in-browser messages. Implementations of this abstract class
    should not require any parameters be passed into their constructor since they are instantiated.

    :attr:`.channel_type` must be a :class:`.ChannelType`.
    """

    channel_type = None

    @classmethod
    def enabled(cls):
        """
        Validate settings to determine whether this channel can be enabled.
        """
        return True

    @abc.abstractmethod
    def deliver(self, message, rendered_message):
        """
        Transmit a rendered message to a recipient.

        Args:
            message (Message): The message to transmit.
            rendered_message (dict): The rendered content of the message that has been personalized for this particular
                recipient.
        """
        raise NotImplementedError()


class ChannelMap:
    """
    A class that represents a channel map, usually as described in Django settings and `setup.py` files.
    """
    def __init__(self, channels_list):
        """
        Initialize a ChannelMap.

        Args:
            channels_list (list): A list of [channel_name, channel] pairs to fill in the channel map, in order.
        """
        self.channel_type_to_channel_impl = defaultdict(OrderedDict)
        for channel_name, channel in channels_list:
            self.register_channel(channel, channel_name)

    def register_channel(self, channel, channel_name):
        """
        Registers a channel in the channel map.

        Args:
            channel (Channel): The channel to register.
            channel_name (str): The channel name, as stated in the `setup.py` file.
        """
        self.channel_type_to_channel_impl[channel.channel_type][channel_name] = channel

    def get_channel_by_name(self, channel_type, channel_name):
        """
        Gets a registered a channel by its name and type.

        Raises:
            KeyError: If either of the channel or its type are not registered.

        Returns:
            Channel: The channel object.
        """
        return self.channel_type_to_channel_impl[channel_type][channel_name]

    def get_default_channel(self, channel_type):
        """
        Returns the first registered channel by type.

        Raises:
            UnsupportedChannelError: If there's no channel that matched the request.

        Args:
            channel_type (ChannelType): The channel type.
        """
        try:
            return next(itertools.islice(self.channel_type_to_channel_impl[channel_type].values(), 0, 1))
        except (StopIteration, KeyError) as error:
            raise UnsupportedChannelError((
                'No implementation for channel {channel_type} is registered. '
                'Available channels are: {channels}'
            ).format(channel_type=channel_type, channels=channels())) from error

    def __str__(self):
        return 'ChannelMap {channels}'.format(channels=repr(self.channel_type_to_channel_impl))


@once
def channels():  # pragma: no cover
    """
    Gathers all available channels.

    Note that this function loads all available channels from entry points. It expects the Django setting
    ``ACE_ENABLED_CHANNELS`` to be a list of plugin names that should be enabled. Only one plugin per channel type
    should appear in that list.

    Raises:
        ValueError: If multiple plugins are enabled for the same channel type.

    Returns:
        ChannelMap: A mapping of channel types to instances of channel objects that can be used to deliver messages.
    """
    plugins = get_plugins(
        namespace=CHANNEL_EXTENSION_NAMESPACE,
        names=getattr(settings, 'ACE_ENABLED_CHANNELS', []),
    )

    return ChannelMap([
        [extension.name, extension.obj]
        for extension in plugins
    ])


def get_channel_for_message(channel_type, message):
    """
    Based on available `channels()` returns a single channels for a message.

    Raises:
        UnsupportedChannelError: If there's no channel matches the request.

    Returns:
        Channel: The selected channel object.
    """
    channels_map = channels()

    if channel_type == ChannelType.EMAIL:
        if message.options.get('transactional'):
            channel_name = settings.ACE_CHANNEL_TRANSACTIONAL_EMAIL
        else:
            channel_name = settings.ACE_CHANNEL_DEFAULT_EMAIL
        try:
            return channels_map.get_channel_by_name(channel_type, channel_name)
        except KeyError:
            pass

    return channels_map.get_default_channel(channel_type)
