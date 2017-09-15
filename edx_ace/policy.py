
from abc import ABCMeta, abstractmethod

import attr
import six

from django.conf import settings

from edx_ace.channel import ChannelType
from edx_ace.utils.once import once
from edx_ace.utils.plugins import get_plugins


@attr.s
class PolicyResult(object):
    deny = attr.ib(
        default=attr.Factory(set),
    )

    @deny.validator
    def check_set_of_channel_types(self, attribute, set_value):
        for value in set_value:
            if value not in ChannelType:
                raise ValueError(u"PolicyResult for {} has an invalid value {}.".format(attribute, value))


@six.add_metaclass(ABCMeta)
class Policy(object):

    @classmethod
    def enabled(cls):
        return True

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


def channels_for(message):
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
