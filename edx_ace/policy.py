from abc import ABCMeta, abstractmethod
import attr
from django.conf import settings

from edx_ace.ace_step import ACEStep
from edx_ace.channel import ChannelType, NON_CHANNEL_TYPES
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
    def __init__(self):
        # self.policies = self._load_policies()
        self.policies = None

    def channels_for(self, message):
        allowed_channels = {channel for channel in ChannelType if channel not in NON_CHANNEL_TYPES}

        for policy in self.policies:
            deny_value = policy.check(message).deny
            if ChannelType.ALL in deny_value:
                return set()
            elif ChannelType.UNSPECIFIED in deny_value:
                continue
            else:
                allowed_channels -= deny_value

        return allowed_channels

    @staticmethod
    def _load_policies():
        return get_plugins(
            namespace=POLICY_PLUGIN_NAMESPACE,
            names=getattr(settings, 'ACE_ENABLED_POLICIES', []),
            instantiate=True,
        ).values()
