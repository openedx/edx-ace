"""
:mod:`edx_ace.policy` contains all classes relating to message policies.

These policies manage which messages should be sent over which channels,
and are a point of pluggability in ACE.
"""
from abc import ABCMeta, abstractmethod

import attr

from django.conf import settings

from edx_ace.channel import ChannelType
from edx_ace.utils.once import once
from edx_ace.utils.plugins import get_plugins


@attr.s
class PolicyResult:
    """
    Arguments:
        deny (set): A set of :class:`.ChannelType` values that should be excluded
            when sending a message.
    """
    deny = attr.ib(
        default=attr.Factory(set),
    )

    @deny.validator
    def check_set_of_channel_types(self, attribute, set_value):
        for value in set_value:
            if value not in ChannelType:
                raise ValueError(f"PolicyResult for {attribute} has an invalid value {value}.")  # pragma: no cover


POLICY_PLUGIN_NAMESPACE = 'openedx.ace.policy'


class Policy(metaclass=ABCMeta):
    """
    A ``Policy`` allows an application to specify what :class:`.Channel` any specific
    :class:`.Message` shouldn't be sent over. Policies are one of the primary
    extension mechanisms for ACE, and are registered using the entrypoint ``openedx.ace.policy``.
    """

    @classmethod
    def enabled(cls):
        return True

    @abstractmethod
    def check(self, message):
        """
        Validate the supplied :class:`~edx_ace.message.Message` against a specific
        delivery policy.

        Arguments:
            message (:class:`.Message`): The message to run the policy against.

        Returns: :class:`.PolicyResult`
            A :class:`.PolicyResult` that represents what channels the ``message`` should not be delivered over.
        """


# TODO(later): Need to support Denying ALL channels for a message
#   For example, a user (or course) policy denies sending all messages
#   of a particular type.

# TODO(later): We may also want to consider adding a separate
#   policy method for checking MessageType objects. For example,
#   the RecipientResolver could also check platform-wide (and
#   course-wide?) policies with a MessageType object.


def channels_for(message):
    """
    Arguments:
        message (:class:`.Message`): The message apply policies to.

    Returns: set
        A set of :class:`.ChannelType` values that are allowed by all policies
        applied to the message.
    """
    allowed_channels = set(ChannelType)

    for policy in policies():
        allowed_channels -= policy.check(message).deny

    message.report('policy_allowed_channels', ','.join(c.value for c in allowed_channels))
    return allowed_channels


@once
def policies():
    return [
        extension.obj
        for extension in get_plugins(
            namespace=POLICY_PLUGIN_NAMESPACE,
            names=getattr(settings, 'ACE_ENABLED_POLICIES', []),
        )
    ]
