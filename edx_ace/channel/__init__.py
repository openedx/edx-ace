# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division

import abc
from enum import Enum

import six
from django.conf import settings

from edx_ace.utils.once import once
from edx_ace.utils.plugins import get_plugins

# TODO(later): encapsulate the shared part of this namespace in the utils.plugin module
CHANNEL_EXTENSION_NAMESPACE = u'openedx.ace.channel'


@six.python_2_unicode_compatible
class ChannelType(Enum):
    u"""
    All supported communication channels.
    """
    EMAIL = u'email'
    PUSH = u'push'

    def __str__(self):
        return self.value


@six.add_metaclass(abc.ABCMeta)
class Channel(object):
    u"""
    Channels deliver messages to users that have already passed through the presentation and policy steps.

    Examples include email messages, push notifications, or in-browser messages. Implementations of this abstract class
    should not require any parameters be passed into their constructor since they are instantiated.

    :attr:`.channel_type` must be a :class:`.ChannelType`.
    """

    channel_type = None

    @classmethod
    def enabled(cls):
        u"""
        Validate settings to determine whether this channel can be enabled.
        """
        return True

    @abc.abstractmethod
    def deliver(self, message, rendered_message):
        u"""
        Transmit a rendered message to a recipient.

        Args:
            message (Message): The message to transmit.
            rendered_message (dict): The rendered content of the message that has been personalized for this particular
                recipient.
        """
        raise NotImplementedError()


@once
def channels():
    u"""
    Gathers all available channels.

    Note that this function loads all available channels from entry points. It expects the Django setting
    ``ACE_ENABLED_CHANNELS`` to be a list of plugin names that should be enabled. Only one plugin per channel type
    should appear in that list.

    Raises:
        ValueError: If multiple plugins are enabled for the same channel type.

    Returns:
        dict: A mapping of channel types to instances of channel objects that can be used to deliver messages.
    """
    plugins = get_plugins(
        namespace=CHANNEL_EXTENSION_NAMESPACE,
        names=getattr(settings, u'ACE_ENABLED_CHANNELS', []),
    )

    channel_map = {}
    for extension in plugins:
        channel = extension.obj
        if channel.channel_type in channel_map:
            raise ValueError(
                u'Multiple plugins registered for the same channel: {first} and {second}'.format(
                    first=channel_map[channel.channel_type].__class__.__name__,
                    second=channel.__class__.__name__,
                )
            )
        channel_map[channel.channel_type] = extension.obj

    return channel_map
