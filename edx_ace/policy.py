# lint-amnesty, pylint: disable=missing-docstring
from abc import ABCMeta, abstractmethod
import attr
from django.conf import settings

from edx_ace.channel import ChannelType
from edx_ace.utils.plugins import get_plugins
from edx_ace.utils.once import once


@attr.s  # lint-amnesty, pylint: disable=missing-docstring
class PolicyResult(object):
    deny = attr.ib(
        default=attr.Factory(set),
    )

    @deny.validator
    def check_set_of_channel_types(self, attribute, set_value):
        for value in set_value:
            if value not in ChannelType:
                raise ValueError(u"PolicyResult for {} has an invalid value {}.".format(attribute, value))


class Policy(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def check(self, message):
        """
        Returns PolicyResult.
        """
        pass


POLICY_PLUGIN_NAMESPACE = 'openedx.ace.policy'


# TODO(later): Need to support Denying ALL channels for a message
#   For example, a user (or course) policy denies sending all messages
#   of a particular type.

# TODO(later): We may also want to consider adding a separate
#   policy method for checking MessageType objects. For example,
#   the RecipientResolver could also check platform-wide (and
#   course-wide?) policies with a MessageType object.


def channels_for(message):  # lint-amnesty, pylint: disable=missing-docstring
    allowed_channels = set(ChannelType)

    for policy in policies():
        allowed_channels -= policy.check(message).deny

    message.report(u'policy_allowed_channels', ','.join(c.value for c in allowed_channels))
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
