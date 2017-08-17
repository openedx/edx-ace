from abc import ABCMeta, abstractmethod
import attr
from django.conf import settings
from lazy import lazy

from edx_ace.ace_step import ACEStep
from edx_ace.channel import ChannelType
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


class Policy(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def check(self, message):
        """
        Returns PolicyResult.
        """
        pass


POLICY_PLUGIN_NAMESPACE = 'openedx.ace.policy'


class PolicyStep(ACEStep):
    def channels_for(self, message):
        allowed_channels = set(ChannelType)

        for policy in self.policies:
            allowed_channels -= policy.check(message).deny

        return allowed_channels

    @lazy
    def policies(self):
        return get_plugins(
            namespace=POLICY_PLUGIN_NAMESPACE,
            names=getattr(settings, 'ACE_ENABLED_POLICIES', []),
            instantiate=True,
        ).values()
