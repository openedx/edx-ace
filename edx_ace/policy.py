from abc import ABCMeta, abstractmethod
import attr
from django.conf import settings

from edx_ace.ace_step import ACEStep
from edx_ace.channel import ChannelType, NON_CHANNEL_TYPES
from edx_ace.utils.plugins import get_plugins


@attr.s
class PolicyResult(object):
    # possible values:
    #   ChannelType.ALL - message should not be sent to any channel
    #   ChannelType.UNSPECIFIED -
    deny = attr.ib(attr.validators.in_(ChannelType))


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
        self.policies = self._load_policies()

    def channels_for(self, message):
        pass
        # allowed_channels = {channel for channel in ChannelType if channel not in NON_CHANNEL_TYPES}
        #
        # for policy in self.policies:
        #     policy_result = policy.check(message)
        #     if policy_result.deny == ChannelType.ALL:
        #         return []
        #     elif policy_result.deny == ChannelType.UNSPECIFIED:
        #         continue
        #     else:
        #         allowed_channels - policy_result.deny


    @staticmethod
    def _load_policies():
        return get_plugins(
            namespace=POLICY_PLUGIN_NAMESPACE,
            names= getattr(settings, 'ACE_ENABLED_POLICIES', []),
            instantiate=True,
        ).value()
