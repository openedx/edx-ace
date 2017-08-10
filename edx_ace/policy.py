from abc import ABCMeta, abstractmethod
import attr
from django.conf import settings

from edx_ace.ace_step import ACEStep
from edx_ace.channel import ChannelType
from edx_ace.utils.plugins import get_plugins


@attr.s
class PolicyResult(object):
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

    @staticmethod
    def _load_policies():
        policy_names = getattr(settings, 'ACE_ENABLED_POLICIES', [])
        if len(policy_names) == 0:
            return []

        plugins = get_plugins(
            namespace=POLICY_PLUGIN_NAMESPACE,
            names=policy_names,
        )

        channels = {}
        for channel_class in plugins:
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
